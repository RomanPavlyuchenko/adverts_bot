from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Dispatcher
from tgbot.services.db_queries import get_campaigns_by_user_id, get_campaign_by_id
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.services.db_queries import get_wbaccount
from tgbot.states.user_state import AdsSettingState, GenerateKeywordsState, InsertKeywordsState
from tgbot.utils.utils import generate_keywords, get_exist_phrases_and_excluded


async def search_company_continue(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """Реагираует на кнопку включения автокор фраз (Сгенерировать, Существющие, Вписать)"""
    async with state.proxy() as data:
        company_id = data['company_id']
        wbacc = await get_wbaccount(db, data['phone'])
        args = {'phone': data['phone'], 'company_type': data['company_type'],
                'company_id': company_id, 'wb_user_id': data['wb_user_id'], 'WBToken': wbacc.wbtoken, 'supplier': wbacc.supplier_id}

    phrases, excluded = get_exist_phrases_and_excluded(args)
    async with state.proxy() as data:
        data['phrases'] = phrases
        data['excluded'] = excluded
    if query.data.split(':')[2] == 'generate_keywords':
        await GenerateKeywordsState.search.set()
        await query.message.edit_text('Введите название товара')
    if query.data.split(':')[2] == 'load_exist_keywords':

        if phrases:

            await query.message.edit_text('Выберите фразы:')
            for i in phrases:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(f'Выбрать', callback_data=f'choice_phrase:{i}'))
                await query.message.answer(f'{phrases[i]["keyword"]} {phrases[i]["count"]}', reply_markup=markup)
            s = 'Сохранить выбор?'
        else:
            s = 'Активных фраз нет'
        await GenerateKeywordsState.confirm.set()
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f'Сохранить', callback_data=f'generate:save'))
        await query.message.answer(s, reply_markup=markup)
    if query.data.split(':')[2] == 'enter_keywords':
        await InsertKeywordsState.insert.set()
        await query.message.edit_text('Выпишите фразы в столбик')
    if query.data.split(':')[2] == 'continue':
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f'Да', callback_data=f'run_ad:yes'))
        markup.add(InlineKeyboardButton(f'Нет', callback_data=f'run_ad:no'))
        await AdsSettingState.confirm.set()
        await query.message.edit_text('Готово. Запустить кампанию?', reply_markup=markup)
    async with state.proxy() as data:
        company_id = data['company_id']


async def process_generate_keywords(message: Message, state: FSMContext):
    """Ввод ключевой фразы. Вывод фраз с кнопками"""
    phrases = generate_keywords(message.text)
    if phrases:
        async with state.proxy() as data:
            data['phrases'] = phrases
        await message.answer('Выберите фразы:')
        for i in phrases:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(f'Выбрать', callback_data=f'choice_phrase:{i}'))
            await message.answer(f'{phrases[i]["keyword"]}', reply_markup=markup)
        s = 'Сохранить выбор?'
    else:
        s = 'Фраз по этому ключевому слову не найдено'
    await GenerateKeywordsState.confirm.set()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f'Выбрать еще', callback_data=f'generate:more'))
    markup.add(InlineKeyboardButton(f'Сохранить', callback_data=f'generate:save'))
    await message.answer(s, reply_markup=markup)


async def process_generate_keywords_choice_phrase(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """Реагирует на нажатие по выбранной фразе"""
    phrase_id = int(query.data.split(':')[1])
    try:
        _ = query.data.split(':')[2]
        delete = True
    except:
        delete = False
    async with state.proxy() as data:
        current_phrases = data['phrases']
        if not delete:
            try:
                data['choice'].append(current_phrases[phrase_id]['keyword'])
            except:
                data['choice'] = [current_phrases[phrase_id]['keyword']]
        else:
            data['choice'].remove(current_phrases[phrase_id]['keyword'])
    markup = InlineKeyboardMarkup()
    if delete:
        markup.add(InlineKeyboardButton(f'Выбрать', callback_data=f'choice_phrase:{phrase_id}'))
    else:
        markup.add(InlineKeyboardButton(f'Выбрано ✅', callback_data=f'choice_phrase:{phrase_id}:delete'))
    await query.message.edit_text(current_phrases[phrase_id]['keyword'], reply_markup=markup)


async def process_generate_keywords_save(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """После выбора фраз. Сохраняет выбранные фразы/генерирует новые"""
    action = query.data.split(':')[1]
    if action == 'more':
        await GenerateKeywordsState.search.set()
        await query.message.edit_text('Введите название товара')
    if action == 'save':
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f'Сгенерировать ключевые фразы', callback_data=f'search:search_keywords:generate_keywords'))
        markup.add(InlineKeyboardButton(f'Выгрузить существующие', callback_data=f'search:search_keywords:load_exist_keywords'))
        markup.add(InlineKeyboardButton(f'Вписать фразы', callback_data=f'search:search_keywords:enter_keywords'))
        markup.add(InlineKeyboardButton(f'Продолжить', callback_data=f'search:search_keywords:continue'))
        await AdsSettingState.search_keywords.set()
        await query.message.edit_text('Фразы сохранены\n\nВыберите пункт', reply_markup=markup)


async def process_insert_phrases(message: Message, state: FSMContext):
    """Ввод фраз в столбик"""
    phrases = message.text.split('\n')

    async with state.proxy() as data:
        try:
            data['choice'] += phrases
        except:
            data['choice'] = phrases
    await InsertKeywordsState.confirm.set()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f'Вписать еще', callback_data=f'insert_phrases:more'))
    markup.add(InlineKeyboardButton(f'Сохранить', callback_data=f'insert_phrases:save'))
    await message.answer('Фразы добавлены', reply_markup=markup)


async def process_insert_phrases_save(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """После вписанных фраз. Сохраняет фразы/просит вписать еще"""
    action = query.data.split(':')[1]
    if action == 'more':
        await InsertKeywordsState.insert.set()
        await query.message.edit_text('Выпишите фразы в столбик')
    if action == 'save':
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f'Сгенерировать ключевые фразы', callback_data=f'search:search_keywords:generate_keywords'))
        markup.add(InlineKeyboardButton(f'Выгрузить существующие', callback_data=f'search:search_keywords:load_exist_keywords'))
        markup.add(InlineKeyboardButton(f'Вписать фразы', callback_data=f'search:search_keywords:enter_keywords'))
        markup.add(InlineKeyboardButton(f'Продолжить', callback_data=f'search:search_keywords:continue'))
        await AdsSettingState.search_keywords.set()
        await query.message.edit_text('Фразы сохранены\n\nВыберите пункт', reply_markup=markup)


def register_user_ads_settings_utils(dp: Dispatcher):
    dp.register_callback_query_handler(search_company_continue, lambda query: query.data.startswith('search:search_keywords'), state=AdsSettingState.search_keywords)

    dp.register_message_handler(process_generate_keywords, state=GenerateKeywordsState.search)
    dp.register_callback_query_handler(process_generate_keywords_choice_phrase, lambda query: query.data.startswith('choice_phrase'), state=GenerateKeywordsState.confirm)
    dp.register_callback_query_handler(process_generate_keywords_save, lambda query: query.data.startswith('generate'), state=GenerateKeywordsState.confirm)

    dp.register_message_handler(process_insert_phrases, state=InsertKeywordsState.insert)
    dp.register_callback_query_handler(process_insert_phrases_save, lambda query: query.data.startswith('insert_phrases'), state=InsertKeywordsState.confirm)


