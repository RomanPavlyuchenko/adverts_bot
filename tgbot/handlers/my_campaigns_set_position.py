from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tgbot.keyboards import kb_user
from tgbot.services import logger
from tgbot.services.db_queries import update_campaign, get_campaign_by_id
from tgbot.services.wb import wb, common
from tgbot.states.my_campaign_state import MyCampaignState
from tgbot.states.user_state import AdsSettingState
from tgbot.utils.all_markups import my_campaign_markup
from tgbot.utils.all_texts import my_campaign_text
from tgbot.utils.wb_api import get_adverts_strange_method


async def show_pos_by_search_or_sku(message: Message, state: FSMContext):
    """Обрабатывает введеный поисковой запрос или артикул конкурента. Выводятся строки с позициями и ценой"""
    async with state.proxy() as data:
        company_type = data['company_type']
    if company_type == 'search':
        try:
            result = get_adverts_strange_method(message.text.lower())
            text = f"Ваш запрос: <b>{message.text.lower()}</b>\n\nВыберите позицию для отслеживания:\n"  # <b>1-ая страница</b>\n"
            pos = 0
            markup = InlineKeyboardMarkup()
            for i in result:
                pos += 1
                markup.add(InlineKeyboardButton(f'Позиция {pos}: ~{i["position"]} место - {i["cpm"]} руб.',
                                                callback_data=f'choice_position:{pos}'))



            # headers = common.get_headers()
            # async with AsyncClient(headers=headers, timeout=common.TIMEOUT) as client:
            #     adverts, positions = await wb.get_adverts_by_query_search(client, message.text.lower())
            #
            # text = f"Ваш запрос: <b>{message.text.lower()}</b>\n\nВыберите позицию для отслеживания:\n"  # <b>1-ая страница</b>\n"
            # pos = 0
            # markup = InlineKeyboardMarkup()
            #
            # for i in positions[0]['positions']:
            #     pos += 1
            #     markup.add(InlineKeyboardButton(f'Позиция {pos}: ~{i} место - {adverts[i]["cpm"]} руб.', callback_data=f'choice_position:{pos}'))
            async with state.proxy() as data:
                data['keywords'] = message.text.lower()
            await MyCampaignState.set_position.set()
            await message.answer(text, reply_markup=markup)
        except:
            await message.answer("Не удалось обработать запрос. Возможно неверный поисковый запрос. Повторите ввод", reply_markup=kb_user.cancel_inline())
    elif company_type == 'carousel-auction':
        if not message.text.isdigit():
            await message.answer("Артикул должен быть числом")
            return
        try:
            headers = common.get_headers()
            async with AsyncClient(headers=headers, timeout=common.TIMEOUT) as client:
                prices_with_position, scu = await wb.get_adverts_by_scu_inline(client, message.text)
        except Exception as e:
            logger.error(e)
            return
        async with state.proxy() as data:
            data['sku'] = int(message.text)
        markup = InlineKeyboardMarkup()
        text = f"Карточка с артикулом: {scu}\n\nВыберите позицию для отслеживания:"
        pos = 0
        for price, position in prices_with_position.items():
            pos += 1
            print('position[0]', position[0])
            if len(position) > 1:
                markup.add(InlineKeyboardButton(f"\nПозиции {position[0]}-{position[-1]}: {price} руб.", callback_data=f'choice_position:{str(position[0])}'))
            else:
                markup.add(InlineKeyboardButton(f"\nПозиция {position[0]}: {price}: {price} руб.", callback_data=f'choice_position:{str(position[0])}'))
        await MyCampaignState.set_position.set()
        await message.answer(text, reply_markup=markup)


async def choice_position(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """После выбора позиции. Просит установить лимит"""
    pos = query.data.split(':')[1]
    async with state.proxy() as data:
        campaign_id = data['campaign_id']
        args = {'position': int(pos), 'keywords': data.get('keywords'), 'sku': data.get('sku')}
    await update_campaign(db, campaign_id, args)
    campaign = await get_campaign_by_id(db, campaign_id)
    await MyCampaignState.choice_campaign.set()
    await query.message.edit_text('Позиция установлена.\n\n' + my_campaign_text(campaign), reply_markup=my_campaign_markup(campaign))

