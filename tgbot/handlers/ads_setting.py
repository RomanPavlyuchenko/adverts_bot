import asyncio
import logging
import os
import threading
from threading import Thread

from aiogram import Dispatcher

from tgbot.browser_work.login_acc import add_new_cookies, auth_account, check_valid_acc, update_wbtoken
from tgbot.handlers.ads_setting_card import *
from tgbot.handlers.ads_setting_search import *
from tgbot.handlers.ads_setting_utils import *
from tgbot.handlers.my_campaigns_set_start_stop_delete import my_campaign_start_campaign, my_campaign_stop_campaign
from tgbot.keyboards import kb_user
from tgbot.keyboards.kb_user import cancel_inline
from tgbot.services import db_queries
from tgbot.services.db_queries import get_wbaccounts_by_user_id, add_new_wbaccount, add_new_campaign, set_wbacc_is_work, \
    delete_wbaccount, get_wbaccount, update_wb_account, get_all_default_campaign_by_phone, get_all_wbaccounts, \
    add_wbacc_to_user, get_wbaccount_by_token

from tgbot.services.texts import Texts
from tgbot.states.user_state import AdsSettingState, AddAccountState
from tgbot.utils import all_texts
from tgbot.utils.registration import reg, start_reg, run_wait, end_reg
from tgbot.utils.utils import get_companies_by_name, get_company_info, make_auto_pay, check_phone, \
    async_get_and_save_default_campaigns, campaign_is_active, auth
from tgbot.utils.wb_api import api_add_balance, api_get_campaign_by_id, set_excluded_words, api_get_balance


async def cmd_my_accounts(message: Message, db: AsyncSession, state: FSMContext):
    """Комнда мои аккаунты. Выбрать Создать Удалить"""
    await state.finish()
    accounts = await get_wbaccounts_by_user_id(db, message.from_user.id)
    markup = InlineKeyboardMarkup()
    if accounts:
        for i in accounts:
            if i:
                if i.choice:
                    markup.add(InlineKeyboardButton(f'Аккаунт {i.name} (выбран)', callback_data=f'set_acc:{i.phone}'))
                else:
                    markup.add(InlineKeyboardButton(f'Выбрать аккаунт {i.name}', callback_data=f'set_acc:{i.phone}'))
                markup.add(InlineKeyboardButton(f'Удалить аккаунт {i.name}', callback_data=f'set_acc:{i.phone}:delete'))
    if len(accounts) < 2 or not accounts:
        print(accounts)
        markup.add(InlineKeyboardButton(f'Добавить новый', callback_data='set_acc:9999'))
    await AdsSettingState.set_account.set()
    await message.answer('Выберите аккаунт для работы:', reply_markup=markup)


async def btn_choice_account(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    phone_id = query.data.split(':')[1]

    try:

        _ = query.data.split(':')[2]
        await delete_wbaccount(db, phone_id, query.from_user.id)
        accounts = await get_wbaccounts_by_user_id(db, query.from_user.id)
        markup = InlineKeyboardMarkup()
        if accounts:
            for i in accounts:
                if i.choice:
                    markup.add(InlineKeyboardButton(f'Аккаунт {i.name} (выбран)', callback_data=f'set_acc:{i.phone}'))
                else:
                    markup.add(InlineKeyboardButton(f'Выбрать аккаунт {i.name}', callback_data=f'set_acc:{i.phone}'))
                markup.add(InlineKeyboardButton(f'Удалить аккаунт {i.name}', callback_data=f'set_acc:{i.phone}:delete'))
        if len(accounts) <= 2 or not accounts:
            markup.add(InlineKeyboardButton(f'Добавить новый', callback_data='set_acc:9999'))
        await AdsSettingState.set_account.set()
        await query.message.edit_text('Аккаунт удален.\n\nВыберите аккаунт для работы:', reply_markup=markup)
    except:
        if phone_id == '9999':
            await AddAccountState.phone.set()

            await query.message.answer_video(open('/root/bots/bot_adverts/video/instr_1.MP4', 'rb'), width=1920, height=1080, caption='Видео инструкция как подключить аккаунт WB к боту.')
            await query.message.edit_text('Введите название для аккаунта')
        else:
            await state.finish()
            await set_wbacc_is_work(db, query.from_user.id, phone_id)
            await query.message.edit_text('Аккаунт выбран!\n\nВыберите пункт меню', reply_markup=kb_user.menu)


async def btn_ads_setting(call: CallbackQuery, db: AsyncSession, state: FSMContext):
    """Откликается на кнопку 'Управление рекламой'"""
    await call.answer()
    user = await db_queries.get_user(db, call.from_user.id)
    if not user:
        await call.message.answer(Texts.start)
        return
    #res = await add_new_wbaccount(db, call.from_user.id, 9876146123)

    accounts = await get_wbaccounts_by_user_id(db, call.from_user.id)
    markup = InlineKeyboardMarkup()
    if accounts:
        for i in accounts:
            print(i)
            if i.choice:
                async with state.proxy() as data:
                    data['phone'] = i.phone
                    data['wb_user_id'] = i.wb_user_id
                await call.message.edit_text(all_texts.enter_campaign_name)
                await AdsSettingState.campaign_name.set()
                return

        for i in accounts:
            markup.add(InlineKeyboardButton(f'Аккаунт {i.name}', callback_data=f'choice_acc:{i.phone}'))
        await AdsSettingState.account.set()
        await call.message.edit_text(f'Выберите аккаунт wb', reply_markup=markup)
    else:
        markup.add(InlineKeyboardButton(f'Добавить новый', callback_data='add_new_acc'))
        await call.message.edit_text(f'Сначала добавьте аккаунт', reply_markup=markup)
        await AdsSettingState.account.set()


async def btn_choice_acc(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """Нажатие на выбираемый аккаунт"""
    phone_id = query.data.replace('choice_acc:', '')
    async with state.proxy() as data:

        data['phone'] = phone_id
    await query.message.edit_text(all_texts.enter_campaign_name)
    await AdsSettingState.campaign_name.set()


async def btn_add_acc(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """Нажатие добавить аккаунт"""
    await AddAccountState.phone.set()
    #print('wtf1')
    await query.message.edit_text('Введите название для аккаунта')


async def process_add_acc(message: Message, db: AsyncSession, state: FSMContext):#, dp: Dispatcher
    """Сохраняет название аккаунта"""

    name = message.text

    async with state.proxy() as data:
        data['name'] = name
    await AddAccountState.supplier.set()
    await message.answer('Введите x-supplier-id-external от аккаунта')

async def process_add_suplier(message: Message, db: AsyncSession, state: FSMContext):#, dp: Dispatcher
    """Сохраняет название аккаунта"""

    name = message.text

    async with state.proxy() as data:
        data['supplier'] = name
    await AddAccountState.code.set()

    await message.answer('''Добавьте номер 79181015645 в свой кабинет WB, как менеджера:

1. Зайдите в Ваш личный кабинет ВБ Партнеры
2. Наведите мышкой на свое название профиля, справа вверху, и нажмите «настройки»
3. В открывшемся окне нажмите «Добавить пользователя»
4. В открывшемся окне в поле номер телефона введите номер 79181015645 (будет найден пользователь Рекламщик Бот) и нажмите добавить.
5. Вернитесь в бот и нажмите проверить подключение.''', reply_markup=kb_user.check_account())



async def process_add_acc_enter_code(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """Ввод wb3 кук для аккаунта"""
    async with state.proxy() as data:
                name = data['name']
                supplier = data['supplier']
                # print(supplier)
    wbacc = await db_queries.get_supplier_id(db, supplier)
    if wbacc:
        print('acc exist')
        await add_wbacc_to_user(db, query.from_user.id, wbacc.phone)
        await query.message.answer(f'Аккаунт сохранен.\n\nИмя аккаунт из базы:{wbacc.name}\n\n {all_texts.enter_campaign_name}')
        WBToken = wbacc.wbtoken
        # WBToken = wbaccounts[0].wbtoken
        res = 200
        # res, WBToken = await auth()
        args = {'WBToken': WBToken}
        # print(args)
        async with state.proxy() as data:
            data['phone'] = wbacc.phone
            data['WBToken'] = args['WBToken']
        await AdsSettingState.campaign_name.set()
    else:
        try:
            last_acc = await get_wbaccounts_by_user_id(db, query.from_user.id)
            if last_acc:
                phone = f"{query.from_user.id}_{int(last_acc[-1].phone.split('_')[1]) + 1}"
            else:
                phone = f"{query.from_user.id}_1"

            await query.message.answer('Идет добавление аккаунта, ожидайте 1-2 минуты')
            # res, WBToken = await auth()
            wbaccounts = await get_all_wbaccounts(db)
            print(wbaccounts)
            WBToken = wbaccounts[0].wbtoken
            res = 200
            args = {'WBToken': WBToken}
            await db.update()
            print(res)
        except Exception as e:
            print('process_add_acc_enter_code', e)
        if res:
            async with state.proxy() as data:
                data['phone'] = phone
            try:
                await add_new_wbaccount(db, query.from_user.id, phone, '', name, supplier)
                args['wb_user_id'] = 98660848
                await update_wb_account(db, phone, args)
                await add_wbacc_to_user(db, query.from_user.id, phone)
                async with state.proxy() as data:
                    data['wb_user_id'] = args['wb_user_id']
                await query.message.answer('Аккаунт сохранен.\n\nИдет добавление кампаний')
                await async_get_and_save_default_campaigns(db, phone, args['wb_user_id'], args['WBToken'], supplier)
                await query.message.answer('Кампании добавлены.\n\n' + all_texts.enter_campaign_name)
                await AdsSettingState.campaign_name.set()
            except Exception as e:
                print('process_add_acc_enter_code', e)
                await query.message.answer('При сохранении возникла ошибка')
        else:
            await query.message.answer('При сохранении возникла ошибка')
            await state.finish()


async def enter_company_name(message: Message, db: AsyncSession, state: FSMContext):
    """После ввода названия кампании. Выводится список кампаний"""

    name = message.text.lower()

    async with state.proxy() as data:
        phone = data['phone']
        companies = await get_all_default_campaign_by_phone(db, phone)
        wbacc = await get_wbaccount(db, phone)
        data['wb_user_id'] = wbacc.wb_user_id
        data['WBToken'] = wbacc.wbtoken
        data['supplier'] = wbacc.supplier_id
    res = []
    exist_campaigns = await get_campaigns_by_user_id(db, message.from_user.id)
    exist_campaigns = [i.campaign_id for i in exist_campaigns]
    for i in companies:
        if name in i.name.lower() and i.campaign_id not in exist_campaigns:
            res.append(i)

    companies = res
    print(companies)
    if companies:
        exist_campaigns = await get_campaigns_by_user_id(db, message.from_user.id)
        exist_campaigns = [i.campaign_id for i in exist_campaigns]
        async with state.proxy() as data:
            data['companies'] = companies
        markup = InlineKeyboardMarkup()
        for i in companies:
            if i.campaign_id not in exist_campaigns:
                if i.type == 'search':
                    company_type_ru = 'Поиск'
                if i.type ==  'carousel-auction':
                    company_type_ru = 'КТ'
                if i.type ==  'catalog':
                    company_type_ru = 'Каталог'
                    continue
                markup.add(InlineKeyboardButton(f'{i.name} - {company_type_ru}', callback_data=f'choice_company:{i.campaign_id}:{i.type}'))
        await AdsSettingState.campaign_choice_name.set()
        await message.answer('Выберите кампанию', reply_markup=markup)
    else:
        await message.answer('Компании не найдены, повторите ввод')
    asyncio.create_task(async_get_and_save_default_campaigns(db, phone, wbacc.wb_user_id, wbacc.wbtoken, wbacc.supplier_id, important=False))


async def choice_company(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """После нажатия на выбранную кампанию. Выводится бюджет"""
    try:
        company_id = int(query.data.split(':')[1])
        company_type = query.data.split(':')[2]

        async with state.proxy() as data:
            companies = data['companies']
            data['company_id'] = company_id
            data['campaign_id'] = company_id
            data['company_type'] = company_type
            wb_user_id = data['wb_user_id']
            phone = data['phone']
            params = {'company_type': company_type, 'company_id': company_id, 'phone': phone, 'wb_user_id': wb_user_id, 'campaign_id': company_id, 'WBToken':data['WBToken'], 'supplier': data['supplier']}
            company = get_company_info(params)
            print(company)
            if not company:
                if not check_valid_acc(phone):
                    await query.message.edit_text('Токен устарел, сейчас идет обновление токена, ожидайте 1-2 минуты.')
                    await update_wbtoken(db, phone)
                    company = get_company_info(params)
            balance = api_get_balance(params)
            data['company'] = company
            for i in companies:
                if i.campaign_id == company_id:
                    data['company_name'] = i.name
                    break
        markup = InlineKeyboardMarkup()
        company_id = str(company_id)
        if company_type == 'search':
            company_type = 1
        if company_type == 'carousel-auction':
            company_type = 2
        if company_type == 'catalog':
            company_type = 3
        markup.add(InlineKeyboardButton(f'Пополнить', callback_data=f'company_balance:{company_type}:company_add_balance:{company_id}'))
        markup.add(InlineKeyboardButton(f'Автопополнение', callback_data=f'company_balance:{company_type}:company_auto_add_balance:{company_id}'))
        markup.add(InlineKeyboardButton(f'Продолжить', callback_data=f'company_balance:{company_type}:company_balance_continue:{company_id}'))
        await AdsSettingState.balance.set()
        await query.message.edit_text(f'Баланс {company["balance"]}. Доступно {balance}.', reply_markup=markup)
    except Exception as e:
        print(e)



async def company_balance(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """После нажатия Продолжить в бюджете. Просит ввести поисковой запрос"""
    company_type = int(query.data.split(':')[1])

    if company_type ==  1:
        company_type = 'search'
    if company_type ==  2:
        company_type = 'carousel-auction'
    if company_type ==  3:
        company_type = 'catalog'
    action = query.data.split(':')[2]
    company_id = int(query.data.split(':')[3])
    async with state.proxy() as data:
        print(data)
        data['company_type'] = company_type
        data['company_id'] = company_id
        wbacc = await get_wbaccount(db, data['phone'])
        args = {'phone': data['phone'], 'wb_user_id': data['wb_user_id'],
                'company_type': company_type, 'company_id': company_id, 'campaign_id': company_id, 'WBToken': wbacc.wbtoken,'supplier':wbacc.supplier_id}
    try:

        if action ==  'company_add_balance':
            await AdsSettingState.balance_add.set()
            await query.message.edit_text('Введите сумму кратную 50 (мин. сумма 100р)')
        if action == 'company_auto_add_balance':
            await query.message.edit_text('Бюджет пополнен на 100р, и будет автоматически пополняться при остатке 10р')
            args['append_balance'] = 100
            await api_add_balance(args)
            async with state.proxy() as data:
                data['append_balance'] = 100
            if company_type == 'search':
                await query.message.answer('Введите поисковой запрос')
                await AdsSettingState.search_search_text.set()
            if company_type == 'carousel-auction':
                # print('ктился_1')
                await query.message.answer('Введите артикул конкурента')
                await AdsSettingState.card_enter_sku.set()
            if company_type == 'catalog':
                pass

        if action == 'company_balance_continue':

            if company_type == 'search':
                await query.message.edit_text('Введите поисковой запрос')
                await AdsSettingState.search_search_text.set()
            if company_type == 'carousel-auction':
                # print('Я запустился_2')
                await query.message.edit_text('Введите артикул конкурента')
                await AdsSettingState.card_enter_sku.set()
            if company_type == 'catalog':
                pass
    except Exception as e:
        print('company_balance', e)


async def add_balance(message: Message, db: AsyncSession, state: FSMContext):
    """После нажатия пополнить баланс. Ввод суммы и пополнение"""
    try:
        append_balance = int(message.text)
        async with state.proxy() as data:
            company_id = data['company_id']
            company_type = data['company_type']
            phone = data['phone']
            wbacc = await get_wbaccount(db, data['phone'])
            args = {'phone': data['phone'], 'wb_user_id': data['wb_user_id'], 'append_balance':append_balance,
                    'company_type': company_type, 'company_id': company_id, 'campaign_id': company_id,
                    'WBToken': wbacc.wbtoken, 'supplier': wbacc.supplier_id}

        if await api_add_balance(args):
            print('Я здесь')
            company = get_company_info(args)
            markup = InlineKeyboardMarkup()

            if company_type == 'search':
                company_type = 1
            if company_type == 'carousel-auction':
                company_type = 2
            if company_type == 'catalog':
                company_type = 3
            markup.add(InlineKeyboardButton(f'Пополнить', callback_data=f'company_balance:{company_type}:company_add_balance:{company_id}'))
            markup.add(InlineKeyboardButton(f'Автопополнение', callback_data=f'company_balance:{company_type}:company_auto_add_balance:{company_id}'))
            markup.add(InlineKeyboardButton(f'Продолжить', callback_data=f'company_balance:{company_type}:company_balance_continue:{company_id}'))
            await AdsSettingState.balance.set()
            await message.answer(f'Баланс пополнен.', reply_markup=markup)
        else:
            await state.finish()
            await message.answer('Ошибка при пополнении баланса', reply_markup=kb_user.menu)
    except Exception as e:
        print('add_balance', e)
        await message.answer('Некорректное число, повторите ввод', reply_markup=kb_user.cancel_inline())


async def cancel_all(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    await state.finish()
    await query.message.edit_text('Отменено!\nВыберите пункт', reply_markup=kb_user.menu)


async def company_run(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """После подтверждения. Запись в базу данных"""
    is_run = query.data.split(':')[1] == 'yes'
    # try:
    async with state.proxy() as data:

            company_id = data['company_id']
            limit = data['limit']
            position = data['position']
            company_type = data['company_type']
            phone = data['phone']
            wbacc = await get_wbaccount(db, data['phone'])
            keywords = data.get('keywords')
            phrases = data.get('choice')
            phrases_default = data.get('phrases')
            balance = data['company']['balance']
            campaign_name = data['company_name']
            append_balance = data.get('append_balance', 0)
            sku = data.get('sku', 0)
            excluded = data.get('excluded')
            wb_user_id = data['wb_user_id']
            auto_change_phrases = data.get('auto_change_phrases', False)
    await state.finish()
    args = {}

    """Добавляет новую кампанию"""
    args['campaign_name'] = campaign_name
    args['campaign_id'] = company_id
    args['phone'] = phone
    args['company_type'] = company_type
    args['position'] = position
    args['limit'] = limit
    args['keywords'] = keywords
    args['balance'] = balance
    args['append_balance'] = append_balance
    args['is_active'] = is_run
    args['sku'] = sku
    args['wb_user_id'] = wb_user_id
    args['WBToken'] = wbacc.wbtoken
    args['supplier'] = wbacc.supplier_id
    if phrases:
        phrases = ';'.join(phrases)
    args['phrases'] = phrases
    args['auto_change_phrases'] = auto_change_phrases
    await add_new_campaign(db, args)
    if company_type == 'search' and phrases:
        try:
            # print('phrases_default', phrases_default)
            # print('excluded', excluded)
            # print('choice', phrases)
            for i in phrases_default:
                excluded.append(phrases_default[i]['keyword'])
            result_excluded = []
            for i in excluded:
                if i not in phrases.split(';'):
                    result_excluded.append(i)
            print('phrases_default', phrases_default)
            print('result_excluded', result_excluded)
            print('excluded', excluded)
            print('choice', phrases)
            set_excluded_words(args, result_excluded)
        except Exception as e:
            print('excluded', e)
    if is_run:
        campaign_is_active.add_campaign(args['campaign_id'], True, position)
        if await my_campaign_start_campaign(db, args):
            await query.message.edit_text('<b>Кампания запущена</b>\n\nВыберите пункт меню', reply_markup=kb_user.menu)
        else:
            await my_campaign_stop_campaign(db, args)
            campaign_is_active.set_is_active_campaign(args['campaign_id'], False)
            await query.message.edit_text(all_texts.campaign_start_error + '\n\n<b>Кампания сохранена</b>\n\nВыберите пункт меню', reply_markup=kb_user.menu)
    else:
        campaign_is_active.add_campaign(args['campaign_id'], False, position)
        await query.message.edit_text('<b>Кампания сохранена</b>\n\nВыберите пункт меню', reply_markup=kb_user.menu)
    # except Exception as e:
    #     print('company_run', e)


def register_ads_setting(dp: Dispatcher):

    dp.register_message_handler(cmd_my_accounts, commands='choice_acc', state='*')
    dp.register_callback_query_handler(btn_choice_account, lambda query: query.data.startswith('set_acc'), state=AdsSettingState.set_account)

    dp.register_callback_query_handler(btn_ads_setting, lambda call: call.data == "ads_settings")
    dp.register_callback_query_handler(cancel_all, lambda query: query.data == 'cancel', state='*')
    dp.register_callback_query_handler(btn_choice_acc, lambda query: query.data.startswith('choice_acc'), state=AdsSettingState.account)
    dp.register_callback_query_handler(btn_add_acc, lambda query: query.data == 'add_new_acc', state=AdsSettingState.account)
    dp.register_message_handler(process_add_acc, state=AddAccountState.phone)
    dp.register_callback_query_handler(process_add_acc_enter_code, lambda query: query.data == 'check_auth', state=AddAccountState.code)
    dp.register_message_handler(process_add_suplier, state=AddAccountState.supplier)

    dp.register_message_handler(enter_company_name, state=AdsSettingState.campaign_name)
    dp.register_callback_query_handler(choice_company, lambda query: query.data.startswith('choice_company'), state=AdsSettingState.campaign_choice_name)
    dp.register_callback_query_handler(company_balance, lambda query: query.data.startswith('company_balance'), state=AdsSettingState.balance)

    dp.register_message_handler(add_balance, state=AdsSettingState.balance_add)

    """search"""
    dp.register_message_handler(search_company_show_pos_by_search_text, state=AdsSettingState.search_search_text)
    dp.register_callback_query_handler(search_company_choice_position, lambda query: query.data.startswith('search:choose_place'), state=AdsSettingState.search_choice_place)
    dp.register_message_handler(search_company_choice_limit, state=AdsSettingState.search_choice_limit)
    dp.register_callback_query_handler(search_company_choice_limit_query, state=AdsSettingState.search_choice_limit)

    dp.register_callback_query_handler(search_company_auto_change_keywords, lambda query: query.data.startswith('search:auto_change_keywords'), state=AdsSettingState.search_auto_change_keywords)

    """card"""
    dp.register_message_handler(card_company_show_pos_by_sku, state=AdsSettingState.card_enter_sku)
    dp.register_callback_query_handler(card_company_choice_position, lambda query: query.data.startswith('carousel-auction:choose_place'), state=AdsSettingState.card_choice_place)
    dp.register_message_handler(card_company_choice_limit, state=AdsSettingState.card_choice_limit)
    dp.register_callback_query_handler(card_company_choice_limit_query, state=AdsSettingState.card_choice_limit)

    dp.register_callback_query_handler(company_run, lambda query: query.data.startswith('run_ad:'), state=AdsSettingState.confirm)

