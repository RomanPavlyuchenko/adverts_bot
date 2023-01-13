from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tgbot.keyboards import kb_user
from tgbot.services.wb import wb, common
from tgbot.states.user_state import AdsSettingState
from loguru import logger

from tgbot.utils import all_texts, all_markups


async def card_company_show_pos_by_sku(message: Message, state: FSMContext):
    """Обрабатывает введеный артикул. Выводятся строки с позициями и ценой"""
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

            markup.add(InlineKeyboardButton(f"\nПозиции {position[0]}-{position[-1]}: {price} руб.", callback_data=f'carousel-auction:choose_place:{str(position[0])}'))
            #text += f"\nПозиции {position[0]}-{position[-1]}: {price}"
        else:
            #text += f"\nПозиция {position[0]}: {price}"
            markup.add(InlineKeyboardButton(f"\nПозиция {position[0]}: {price}: {price} руб.", callback_data=f'carousel-auction:choose_place:{str(position[0])}'))
    await message.answer(text, reply_markup=markup)
    await AdsSettingState.card_choice_place.set()


async def card_company_choice_position(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """После выбора позиции. Просит установить лимит"""
    pos = query.data.split(':')[2]
    print('pos', pos)
    async with state.proxy() as data:
        data['position'] = int(pos)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(all_markups.btn_skip, callback_data=f'search_skip'))
    await query.message.edit_text('Позиция установлена. ' + all_texts.enter_limit, reply_markup=markup)
    await AdsSettingState.card_choice_limit.set()


async def card_company_choice_limit(message: Message, state: FSMContext):
    """Установка лимита. Готово"""
    try:
        limit = int(message.text)
        async with state.proxy() as data:
            data['limit'] = limit
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f'Да', callback_data=f'run_ad:yes'))
        markup.add(InlineKeyboardButton(f'Нет', callback_data=f'run_ad:no'))
        await AdsSettingState.confirm.set()
        await message.answer('Готово. Запустить?', reply_markup=markup)
    except:
        await message.answer('Некорректный ввод. Повторите попытку', reply_markup=kb_user.cancel_inline())


async def card_company_choice_limit_query(query: CallbackQuery, state: FSMContext):
    """Установка лимита. Готово"""

    limit = 99999
    async with state.proxy() as data:
        data['limit'] = limit
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f'Да', callback_data=f'run_ad:yes'))
    markup.add(InlineKeyboardButton(f'Нет', callback_data=f'run_ad:no'))
    await AdsSettingState.confirm.set()
    await query.message.edit_text('Готово. Запустить?', reply_markup=markup)
