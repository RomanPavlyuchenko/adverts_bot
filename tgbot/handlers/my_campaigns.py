from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Dispatcher

from tgbot.handlers.my_campaigns_auto_change_keywords import my_campaign_process_generate_keywords, my_campaign_process_generate_keywords_choice_phrase, \
    my_campaign_process_insert_phrases, my_campaign_search_company_continue, my_campaign_process_generate_keywords_save, \
    my_campaign_process_insert_phrases_save
from tgbot.handlers.my_campaigns_set_position import show_pos_by_search_or_sku, choice_position
from tgbot.handlers.my_campaigns_set_start_stop_delete import my_campaign_start_campaign, my_campaign_stop_campaign, \
    my_campaign_delete_campaign
from tgbot.keyboards import kb_user
from tgbot.models.tables import Campaigns
from tgbot.services.db_queries import get_campaigns_by_user_id, get_campaign_by_id, get_wbaccount, update_campaign
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.states.my_campaign_state import MyCampaignState
from tgbot.utils import all_texts
from tgbot.utils.all_markups import my_campaign_markup
from tgbot.utils.all_texts import my_campaign_text
from tgbot.utils.utils import update_campaign_balance, campaign_is_active, CampaignIsActive
from tgbot.utils.wb_api import api_add_balance, api_get_stat_campaign


async def command_my_campaigns(message: Message, db: AsyncSession, state: FSMContext):
    """Команда Мои кампании"""
    await state.finish()
    try:
        #print('command_my_campaigns campaign_is_active', campaign_is_active.campaigns)
        markup = InlineKeyboardMarkup()
        res = await get_campaigns_by_user_id(db, message.from_user.id)

        if res:
            for i in res:
                print(i.campaign_id)
                print(CampaignIsActive.campaigns)
                status = '🟢' if campaign_is_active.get_is_active_campaign(i.campaign_id) else '🔴'
                print(status)
                type_ad = 'Поиск' if i.type == 'search' else 'КТ'
                markup.add(InlineKeyboardButton(f'{status}{i.campaign_name} - {type_ad}', callback_data=f'show_campaign:{i.campaign_id}'))
            await message.answer('Ваши кампании:', reply_markup=markup)
        else:
            await message.answer(all_texts.campaign_has_no)
    except Exception as e:
        print('command_my_campaigns', e)

async def command_my_campaign_query(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """Инлайн кнопка Мои кампании"""
    await state.finish()
    markup = InlineKeyboardMarkup()
    res = await get_campaigns_by_user_id(db, query.from_user.id)
    if res:
        for i in res:
            status = '🟢' if campaign_is_active.get_is_active_campaign(i.campaign_id) else '🔴'
            type_ad = 'Поиск' if i.type == 'search' else 'КТ'
            markup.add(InlineKeyboardButton(f'{status}{i.campaign_name} - {type_ad}', callback_data=f'show_campaign:{i.campaign_id}'))# -  - {i.balance}руб.
        await query.message.edit_text('Ваши кампании:', reply_markup=markup)
    else:
        await query.message.edit_text(all_texts.campaign_has_no)


async def show_campaign(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """При клике на кампанию"""
    try:
        await MyCampaignState.choice_campaign.set()
        campaign_id = int(query.data.split(':')[1])
        campaign = await get_campaign_by_id(db, campaign_id)
        async with state.proxy() as data:
            data['campaign_id'] = campaign_id
            data['phone'] = campaign.phone
            data['company_type'] = campaign.type
            wbacc = await get_wbaccount(db, campaign.phone)
            data['wb_user_id'] = wbacc.wb_user_id
            if campaign.phrases:
                data['choice'] = campaign.phrases.split(';')
            data['WBToken'] = wbacc.wbtoken
            data['supplier'] = wbacc.supplier_id
            await update_campaign_balance(db, data)

        campaign = await get_campaign_by_id(db, campaign_id)
        await query.message.edit_text(my_campaign_text(campaign), reply_markup=my_campaign_markup(campaign))
    except Exception as e:
        print('show_campaign', e)


async def my_campaigns_action(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """При выборе действия с кампанией"""
    action = query.data.split(':')[1]
    campaign_id = int(query.data.split(':')[2])
    campaign = await get_campaign_by_id(db, campaign_id)
    wbacc = await get_wbaccount(db, campaign.phone)
    async with state.proxy() as data:
        data['campaign_id'] = campaign_id
        data['phone'] = campaign.phone
        data['wb_user_id'] = wbacc.wb_user_id
        data['company_type'] = campaign.type
        data['args'] = {'campaign_id': campaign_id, 'phone': campaign.phone,
                        'wb_user_id': wbacc.wb_user_id, 'company_type': campaign.type, 'WBToken': wbacc.wbtoken, 'supplier': wbacc.supplier_id}
        args = data['args']
    if action == 'add_balance':
        await MyCampaignState.add_balance.set()
        await query.message.edit_text(all_texts.balance_enter_append_sum)
    if action == 'set_position':
        await MyCampaignState.enter_search_or_sku.set()

        if campaign.type == 'search':
            await query.message.edit_text(all_texts.search_enter_keyword)
        if campaign.type == 'carousel-auction':
            await query.message.edit_text(all_texts.carousel_enter_sku)
    if action == 'set_limit':
        await MyCampaignState.set_limit.set()
        await query.message.edit_text(all_texts.enter_limit)
    if action == 'on_auto_add_balance':
        args = {'append_balance': 100}
        await update_campaign(db, campaign_id, args)
        campaign = await get_campaign_by_id(db, campaign_id)
        await query.message.edit_text(all_texts.auto_add_balance_on + '\n\n' + all_texts.my_campaign_text(campaign),reply_markup=my_campaign_markup(campaign))
    if action == 'off_auto_add_balance':
        args = {'append_balance': 0}
        await update_campaign(db, campaign_id, args)
        campaign = await get_campaign_by_id(db, campaign_id)
        await query.message.edit_text(all_texts.auto_add_balance_off + '\n\n' + all_texts.my_campaign_text(campaign), reply_markup=my_campaign_markup(campaign))
    if action == 'auto_change_keywords':
        markup = InlineKeyboardMarkup()

        markup.add(InlineKeyboardButton(f'Сгенерировать ключевые фразы', callback_data=f'my_campaign:generate_keywords'))
        markup.add(InlineKeyboardButton(f'Выгрузить существующие', callback_data=f'my_campaign:load_exist_keywords'))
        markup.add(InlineKeyboardButton(f'Вписать фразы', callback_data=f'my_campaign:enter_keywords'))
        if campaign.auto_change_phrases:
            markup.add(InlineKeyboardButton(f'Выключить автоудаление ключевых фраз', callback_data=f'my_campaign:auto_change_phrases_off'))
        else:
            markup.add(InlineKeyboardButton(f'Включить автоудаление ключевых фраз', callback_data=f'my_campaign:auto_change_phrases_on'))
        markup.add(InlineKeyboardButton(f'Назад', callback_data=f'my_campaign:back'))
        await MyCampaignState.keywords.set()
        await query.message.edit_text('Корректировка ключевых фраз\n\nВыберите пункт', reply_markup=markup)
    if action == 'get_keywords':
        text = 'Ключевые фразы:\n\n'
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f'Назад', callback_data=f'campaign:get_keywords_back:{campaign_id}'))
        if campaign.phrases:
            for i in campaign.phrases.split(';'):
                text += f'{i}\n'
            await query.message.edit_text(text, reply_markup=markup)
        else:
            await query.message.edit_text(all_texts.get_keywords_have_no, reply_markup=markup)
    if action == 'get_keywords_back':
        #campaign = await get_campaign_by_id(db, campaign_id)
        await query.message.edit_text(all_texts.my_campaign_text(campaign), reply_markup=my_campaign_markup(campaign))

    if action == 'set_stop':
        if await my_campaign_stop_campaign(db, args):
            campaign_is_active.set_is_active_campaign(campaign.campaign_id, False)
            campaign = await get_campaign_by_id(db, campaign_id)
            await query.message.edit_text(all_texts.campaign_stop + '\n\n' + all_texts.my_campaign_text(campaign), reply_markup=my_campaign_markup(campaign))
        else:
            campaign = await get_campaign_by_id(db, campaign_id)
            await query.message.edit_text(all_texts.campaign_stop_error + '\n\n' + all_texts.my_campaign_text(campaign),
                                          reply_markup=my_campaign_markup(campaign))
    if action == 'set_start':
        if await my_campaign_start_campaign(db, args):
            campaign_is_active.set_is_active_campaign(campaign.campaign_id, True)
            campaign = await get_campaign_by_id(db, campaign_id)
            await query.message.edit_text(all_texts.campaign_start + '\n\n' + all_texts.my_campaign_text(campaign), reply_markup=my_campaign_markup(campaign))
        else:
            await my_campaign_stop_campaign(db, args)
            campaign_is_active.set_is_active_campaign(campaign.campaign_id, False)
            campaign = await get_campaign_by_id(db, campaign_id)
            await query.message.edit_text(all_texts.campaign_start_error + '\n\n' + all_texts.my_campaign_text(campaign), reply_markup=my_campaign_markup(campaign))
    if action == 'stat':
        text = await my_campaign_get_stat(args)
        await query.message.answer(text)
    if action == 'delete':
        await my_campaign_delete_campaign(db, args)
        campaign_is_active.del_campaigns(args['campaign_id'])
        await state.finish()
        markup = InlineKeyboardMarkup()
        res = await get_campaigns_by_user_id(db, query.from_user.id)
        if res:
            for i in res:
                status = '🟢' if campaign_is_active.get_is_active_campaign(i.campaign_id) else '🔴'
                type_ad = 'Поиск' if i.type == 'search' else 'КТ'
                markup.add(InlineKeyboardButton(f'{status}{i.campaign_name} - {type_ad}', callback_data=f'show_campaign:{i.campaign_id}'))
            await query.message.edit_text(all_texts.campaign_delete + '\n\nВаши кампании:', reply_markup=markup)
        else:
            await query.message.edit_text(all_texts.choice_menu, reply_markup=kb_user.menu)
        # if res:
        #     for i in res:
        #         status = 'Запущена' if i.is_active else 'Приостановлена'
        #         type_ad = 'Поиск' if i.type == 'search' else 'Карточка'
        #         markup.add(InlineKeyboardButton(f'{i.campaign_name} - {type_ad} - {status} - {i.balance}руб.',
        #                                         callback_data=f'show_campaign:{i.campaign_id}'))
        #     await query.message.edit_text(all_texts.campaign_delete + '\n\nВаши кампании:', reply_markup=markup)
        # else:
        #     await query.message.edit_text(all_texts.choice_menu, reply_markup=kb_user.menu)
    if action == 'menu':
        await state.finish()
        await query.message.edit_text(all_texts.choice_menu, reply_markup=kb_user.menu)


async def my_campaign_add_balance(message: Message, db: AsyncSession, state: FSMContext):
    """После ввода суммы пополнения. Пополнение баланса"""
    try:
        append_balance = int(message.text)
    except:
        await message.answer('Неверная сумма, повторите ввод')
        return
    async with state.proxy() as data:
        args = data['args']
        args['append_balance'] = append_balance
        campaign_id = data['campaign_id']
    if await api_add_balance(args):
        await message.answer('Баланс пополнен')
    else:
        await message.answer('При пополнении баланса возникла ошибка')
    await MyCampaignState.choice_campaign.set()
    campaign = await get_campaign_by_id(db, campaign_id)
    await message.answer(all_texts.limit_set_complete + '\n\n' + all_texts.my_campaign_text(campaign), reply_markup=my_campaign_markup(campaign))


async def my_campaigns_set_limit(message: Message, db: AsyncSession, state: FSMContext):
    """Обрабатывает введеный лимит ставки"""
    try:
        limit = int(message.text)

        async with state.proxy() as data:
            campaign_id = data['campaign_id']
        args = {'limit': limit}
        await update_campaign(db, campaign_id, args)
        await MyCampaignState.choice_campaign.set()
        campaign = await get_campaign_by_id(db, campaign_id)
        await message.answer(all_texts.limit_set_complete + '\n\n' + all_texts.my_campaign_text(campaign), reply_markup=my_campaign_markup(campaign))
    except:
        await message.answer('Некорректное число')


async def my_campaign_get_stat(args: dict):

    res = await api_get_stat_campaign(args)
    text = ''
    if args['company_type'] == 'search':
        for i in res:
            text += f'\n\n<b>{i["keyword"]}</b>\nПросмотры - {i["views"]}\nКлики - {i["clicks"]}\nCTR - {i["ctr"]}%\nЗатраты - {round(i["sum"], 2)}₽'
    else:
        for i in res:
            advertName = 'Всего по кампании' if not i["advertName"] else i["advertName"]
            text += f'\n\n<b>{advertName}</b>\nПросмотры - {i["views"]}\nКлики - {i["clicks"]}\nCTR - {i["ctr"]}%\nЗатраты - {round(i["sum"], 2)}₽'
    return text


def register_user_my_campaigns(dp: Dispatcher):

    dp.register_callback_query_handler(show_campaign, lambda query: query.data.startswith('show_campaign'))
    dp.register_callback_query_handler(my_campaigns_action, lambda query: query.data.startswith('campaign:'), state=MyCampaignState.choice_campaign)
    
    dp.register_message_handler(my_campaign_add_balance, state=MyCampaignState.add_balance)
    dp.register_message_handler(show_pos_by_search_or_sku, state=MyCampaignState.enter_search_or_sku)
    dp.register_callback_query_handler(choice_position, lambda query: query.data.startswith('choice_position'), state=MyCampaignState.set_position)

    dp.register_message_handler(my_campaigns_set_limit, state=MyCampaignState.set_limit)

    dp.register_callback_query_handler(my_campaign_search_company_continue, lambda query: query.data.startswith('my_campaign'), state=MyCampaignState.keywords)
    dp.register_message_handler(my_campaign_process_generate_keywords, state=MyCampaignState.generate_keywords)
    dp.register_callback_query_handler(my_campaign_process_generate_keywords_choice_phrase, lambda query: query.data.startswith('choice_phrase'), state=MyCampaignState.keywords_confirm)
    dp.register_message_handler(my_campaign_process_insert_phrases, state=MyCampaignState.insert_keywords)
    dp.register_callback_query_handler(my_campaign_process_generate_keywords_save, lambda query: query.data.startswith('generate'), state=MyCampaignState.keywords_confirm)
    dp.register_callback_query_handler(my_campaign_process_insert_phrases_save, lambda query: query.data.startswith('insert_phrases'), state=MyCampaignState.keywords_confirm)

