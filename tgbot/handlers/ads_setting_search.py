from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tgbot.keyboards import kb_user
from tgbot.services.wb import wb, common
from tgbot.states.user_state import AdsSettingState
from tgbot.utils import all_texts, all_markups
from tgbot.utils.wb_api import get_adverts_strange_method, api_set_new_price

async def search_company_show_pos_by_search_text(message: Message, state: FSMContext):
    """Обрабатывает введеный поисковой запрос. Выводятся строки с позициями и ценой"""
    try:
        result = get_adverts_strange_method(message.text.lower())
        text = f"Ваш запрос: <b>{message.text.lower()}</b>\n\nВыберите позицию для отслеживания:\n"  # <b>1-ая страница</b>\n"
        pos = 0
        markup = InlineKeyboardMarkup()
        for i in result:
            pos += 1
            markup.add(InlineKeyboardButton(f'Позиция {pos}: ~{i["position"]} место - {i["cpm"]} руб.', callback_data=f'search:choose_place:{pos}'))

        # headers = common.get_headers()
        # async with AsyncClient(headers=headers, timeout=common.TIMEOUT) as client:#, proxies="http://109.172.114.4:45785"
        #     adverts, positions = await wb.get_adverts_by_query_search(client, message.text.lower())
        #
        # text = f"Ваш запрос: <b>{message.text.lower()}</b>\n\nВыберите позицию для отслеживания:\n"  # <b>1-ая страница</b>\n"
        # pos = 0
        # markup = InlineKeyboardMarkup()
        #
        # for i in positions[0]['positions']:
        #     pos += 1
        #     markup.add(InlineKeyboardButton(f'Позиция {pos}: ~{i} место - {adverts[i]["cpm"]} руб.', callback_data=f'search:choose_place:{pos}'))
        async with state.proxy() as data:
            data['keywords'] = message.text.lower()
        await AdsSettingState.search_choice_place.set()
        await message.answer(text, reply_markup=markup)
    except:
        await message.answer("Не удалось обработать запрос. Возможно неверный поисковый запрос. Повторите ввод", reply_markup=kb_user.cancel_inline())


async def search_company_choice_position(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """После выбора позиции. Просит установить лимит"""
    pos = query.data.split(':')[2]
    async with state.proxy() as data:
        data['position'] = int(pos)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(all_markups.btn_skip, callback_data=f'search_skip'))
    await query.message.edit_text('Позиция установлена. ' + all_texts.enter_limit, reply_markup=markup)
    await AdsSettingState.search_choice_limit.set()


async def search_company_choice_limit(message: Message, state: FSMContext):
    """Установка лимита. Включить ли автокор ключевых фраз"""
    try:
        limit = int(message.text)
        async with state.proxy() as data:
            data['limit'] = limit
            data['auto_change_phrases'] = False
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f'Да', callback_data=f'search:auto_change_keywords:yes'))
        markup.add(InlineKeyboardButton(f'Нет', callback_data=f'search:auto_change_keywords:no'))
        await AdsSettingState.search_auto_change_keywords.set()
        await message.answer('Лимит установлен.\nВключить автокорректировку ключевых фраз?', reply_markup=markup)
    except:
        await message.answer('Некорректный ввод. Повторите попытку', reply_markup=kb_user.cancel_inline())


async def search_company_choice_limit_query(query: CallbackQuery, state: FSMContext):
    """Установка лимита. Включить ли автокор ключевых фраз"""
    limit = 99999
    async with state.proxy() as data:
        data['limit'] = limit
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f'Да', callback_data=f'search:auto_change_keywords:yes'))
    markup.add(InlineKeyboardButton(f'Нет', callback_data=f'search:auto_change_keywords:no'))
    await AdsSettingState.search_auto_change_keywords.set()
    await query.message.edit_text('Лимит установлен.\nВключить автокорректировку ключевых фраз?', reply_markup=markup)


async def search_company_auto_change_keywords(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """on/off автокор. Изменить фразы/end"""
    ans = query.data.split(':')[2]
    if ans == 'yes':
        async with state.proxy() as data:
            data['auto_change_phrases'] = True
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f'Сгенерировать ключевые фразы', callback_data=f'search:search_keywords:generate_keywords'))
        markup.add(InlineKeyboardButton(f'Выгрузить существующие', callback_data=f'search:search_keywords:load_exist_keywords'))
        markup.add(InlineKeyboardButton(f'Вписать фразы', callback_data=f'search:search_keywords:enter_keywords'))
        markup.add(InlineKeyboardButton(f'Продолжить', callback_data=f'search:search_keywords:continue'))
        await AdsSettingState.search_keywords.set()
        await query.message.edit_text('Автокорректировка включена\nВыберите пункт', reply_markup=markup)
    else:
        async with state.proxy() as data:
            data['auto_change_phrases'] = False
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f'Да', callback_data=f'run_ad:yes'))
        markup.add(InlineKeyboardButton(f'Нет', callback_data=f'run_ad:no'))
        await AdsSettingState.confirm.set()
        await query.message.edit_text('Готово. Запустить?', reply_markup=markup)


