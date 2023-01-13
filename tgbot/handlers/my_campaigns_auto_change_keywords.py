from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Dispatcher
from tgbot.services.db_queries import get_campaigns_by_user_id, get_campaign_by_id, update_campaign, get_wbaccount
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.states.my_campaign_state import MyCampaignState
from tgbot.states.user_state import AdsSettingState, GenerateKeywordsState, InsertKeywordsState
from tgbot.utils import all_texts
from tgbot.utils.all_markups import my_campaign_markup
from tgbot.utils.utils import generate_keywords, get_exist_phrases_and_excluded
from tgbot.utils.wb_api import set_excluded_words


async def my_campaign_search_company_continue(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """Реагираует на кнопку включения автокор фраз (Сгенерировать, Существющие, Вписать)"""
    try:
        async with state.proxy() as data:
            company_id = data['campaign_id']
            data['company_id'] = company_id
            company_type = data['company_type']
            wbacc = await get_wbaccount(db, data['phone'])
            args = {'phone': data['phone'], 'company_type': data['company_type'],
                    'company_id': company_id, 'wb_user_id': data['wb_user_id'], 'campaign_id': company_id, 'WBToken': wbacc.wbtoken, 'supplier': wbacc.supplier_id}
        phrases, excluded = get_exist_phrases_and_excluded(args)
        async with state.proxy() as data:
            data['phrases'] = phrases
            data['excluded'] = excluded
        if query.data.split(':')[1] == 'generate_keywords':
            await MyCampaignState.generate_keywords.set()
            await query.message.edit_text('Введите название товара')
        if query.data.split(':')[1] == 'load_exist_keywords':

            if phrases:

                await query.message.edit_text('Выберите фразы:')
                for i in phrases:
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton(f'Выбрать', callback_data=f'choice_phrase:{i}'))
                    await query.message.answer(f'{phrases[i]["keyword"]} {phrases[i]["count"]}', reply_markup=markup)
                s = 'Сохранить выбор?'
            else:
                s = 'Активных фраз нет'
            await MyCampaignState.keywords_confirm.set()
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(f'Сохранить', callback_data=f'generate:save'))
            await query.message.answer(s, reply_markup=markup)
        if query.data.split(':')[1] == 'enter_keywords':
            await MyCampaignState.insert_keywords.set()
            await query.message.edit_text('Выпишите фразы в столбик')
        if query.data.split(':')[1] == 'auto_change_phrases_on':
            args = {'auto_change_phrases': True}
            await update_campaign(db, company_id, args)
            campaign = await get_campaign_by_id(db, company_id)
            await MyCampaignState.choice_campaign.set()
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
        if query.data.split(':')[1] == 'auto_change_phrases_off':
            args = {'auto_change_phrases': False}
            await update_campaign(db, company_id, args)
            await MyCampaignState.choice_campaign.set()
            campaign = await get_campaign_by_id(db, company_id)
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
        if query.data.split(':')[1] == 'back':
            async with state.proxy() as data:
                phrases = data.get('choice')
                phrases_default = data.get('phrases')
                excluded = data['excluded']
                campaign_id = data['campaign_id']
            if phrases:
                phrases = ';'.join(phrases)
                args['phrases'] = phrases
                if company_type == 'search':
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
                        await update_campaign(db, campaign_id, {'phrases': phrases})
                        set_excluded_words(args, result_excluded)
                    except Exception as e:
                        print('excluded', e)
            await MyCampaignState.choice_campaign.set()
            campaign = await get_campaign_by_id(db, company_id)
            await query.message.edit_text(all_texts.campaign_keywords_saved + '\n\n' + all_texts.my_campaign_text(campaign), reply_markup=my_campaign_markup(campaign))
    except Exception as e:
        print(e)


async def my_campaign_process_generate_keywords(message: Message, state: FSMContext):
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
    await MyCampaignState.keywords_confirm.set()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f'Выбрать еще', callback_data=f'generate:more'))
    markup.add(InlineKeyboardButton(f'Сохранить', callback_data=f'generate:save'))
    await message.answer(s, reply_markup=markup)


async def my_campaign_process_generate_keywords_choice_phrase(query: CallbackQuery, db: AsyncSession, state: FSMContext):
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


async def my_campaign_process_generate_keywords_save(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """После выбора фраз. Сохраняет выбранные фразы/генерирует новые"""
    action = query.data.split(':')[1]

    if action == 'more':
        await MyCampaignState.generate_keywords.set()
        await query.message.edit_text('Введите название товара')
    if action == 'save':
        try:
            async with state.proxy() as data:
                phrases = data['choice']
                campaign_id = data['campaign_id']
            await update_campaign(db, campaign_id, {'phrases': ';'.join(phrases)})
        except Exception as e:
            print('my_campaign_process_generate_keywords_save', e)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f'Сгенерировать ключевые фразы', callback_data=f'my_campaign:generate_keywords'))
        markup.add(InlineKeyboardButton(f'Выгрузить существующие', callback_data=f'my_campaign:load_exist_keywords'))
        markup.add(InlineKeyboardButton(f'Вписать фразы', callback_data=f'my_campaign:enter_keywords'))
        markup.add(InlineKeyboardButton(f'Назад', callback_data=f'my_campaign:back'))
        await MyCampaignState.keywords.set()
        await query.message.edit_text('Фразы сохранены.\n\nКорректировка ключевых фраз\n\nВыберите пункт', reply_markup=markup)


async def my_campaign_process_insert_phrases(message: Message, state: FSMContext):
    """Ввод фраз в столбик"""
    phrases = message.text.strip().split('\n')
    phrases1 = []
    for i in phrases:
        phrases1.append(i.strip())
    async with state.proxy() as data:
        try:
            data['choice'] += phrases1
        except:
            data['choice'] = phrases1
    await MyCampaignState.keywords_confirm.set()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f'Вписать еще', callback_data=f'insert_phrases:more'))
    markup.add(InlineKeyboardButton(f'Сохранить', callback_data=f'insert_phrases:save'))
    await message.answer('Фразы добавлены', reply_markup=markup)


async def my_campaign_process_insert_phrases_save(query: CallbackQuery, db: AsyncSession, state: FSMContext):
    """После вписанных фраз. Сохраняет фразы/просит вписать еще"""
    action = query.data.split(':')[1]

    if action == 'more':
        await MyCampaignState.insert_keywords.set()
        await query.message.edit_text('Выпишите фразы в столбик')
    if action == 'save':
        try:
            async with state.proxy() as data:
                phrases = data['choice']
                campaign_id = data['campaign_id']
            await update_campaign(db, campaign_id, {'phrases': ';'.join(phrases)})
        except Exception as e:
            print(e)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f'Сгенерировать ключевые фразы', callback_data=f'my_campaign:generate_keywords'))
        markup.add(InlineKeyboardButton(f'Выгрузить существующие', callback_data=f'my_campaign:load_exist_keywords'))
        markup.add(InlineKeyboardButton(f'Вписать фразы', callback_data=f'my_campaign:enter_keywords'))
        markup.add(InlineKeyboardButton(f'Назад', callback_data=f'my_campaign:back'))
        await MyCampaignState.keywords.set()
        await query.message.edit_text('Фразы сохранены.\n\nКорректировка ключевых фраз\n\nВыберите пункт', reply_markup=markup)