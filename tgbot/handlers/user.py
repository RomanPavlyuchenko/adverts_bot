import asyncio

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile
from httpx import AsyncClient
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.handlers.my_campaigns import command_my_campaigns, command_my_campaign_query
from tgbot.keyboards import kb_user
from tgbot.services import db_queries 
from tgbot.services.wb import wb, common, errors
from tgbot.services.texts import Texts
from tgbot.services.wb.wb_selenium import get_adverts
from tgbot.utils.wb_api import get_adverts_strange_method


async def user_start(msg: Message, db: AsyncSession, state: FSMContext):
    """Обработка команды старт"""
    await state.finish()
    user = await db_queries.get_user(db, msg.from_user.id)
    if not user:
        images = [InputMediaPhoto(InputFile("images/1.jpg")), InputMediaPhoto(InputFile("images/2.jpg"))]
        # images = [
        #     InputMediaPhoto("AgACAgIAAxkDAAMKYoO1LamGPUXHnIGHLrPS2tR8J3MAAgy9MRvXIxlIOpnHZZQOi_gBAAMCAAN5AAMkBA"),
        #     InputMediaPhoto("AgACAgIAAxkDAAMLYoO1LfYAASe3Lh8V1ALMJqyMoQoOAAILvTEb1yMZSMcPwS_zzjfiAQADAgADeQADJAQ")
        # ]
        await msg.answer(Texts.start)
        await msg.answer_media_group(images)
        await msg.answer("Оформить подписку", reply_markup=kb_user.subscribe())
        return
    await msg.answer("Выберите пункт меню", reply_markup=kb_user.menu)


# async def btn_subscribe(call: CallbackQuery):
#     """Обработка команды на покупку подписки"""
#     await call.answer()
#     period = "день" if call.data == "day" else "месяц"
#     await call.message.answer(f"Вы выбрали 1 {period} подписки")
#     await call.message.answer(Texts.subscribe, reply_markup=kb_user.paid())


# async def paid(call: CallbackQuery):
#     """Обработка команды 'Оплатил'. """
#     await call.answer()
#     await call.message.edit_reply_markup()
#     await call.message.answer(Texts.paid, reply_markup=kb_user.menu)


async def btn_check_price_in_search(call: CallbackQuery, db: AsyncSession, state: FSMContext):
    """Откликается на кнопку 'Поиск'"""
    await call.answer()
    user = await db_queries.get_user(db, call.from_user.id)
    if not user:
        await call.message.answer(Texts.start)
        return
    await call.message.edit_text("Введите поисковый запрос")
    await state.set_state("get_search_query")


async def get_search_query(msg: Message, state: FSMContext):
    """Получает поисковый запрос для проверки цены на рекламу"""
    await state.finish()
#     try:
#         #headers = common.get_headers()
#         proxies = {
#             "http://": "http://PxEhRH6U:2gQvQRGD@194.226.166.86:45170"
#         }
#         headers_ = '''accept: */*
# accept-encoding: gzip, deflate, br
# accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
# cache-control: no-cache
# origin: https://www.wildberries.ru
# pragma: no-cache
# sec-ch-ua: "Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"
# sec-ch-ua-mobile: ?0
# sec-ch-ua-platform: "Windows"
# sec-fetch-dest: empty
# sec-fetch-mode: cors
# sec-fetch-site: same-site
# user-agent: Mozilla/5.0 (Linux; Android 7.1.2; Redmi Note 5A Build/N2G47H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.111 Mobile Safari/537.36'''
#         headers_ = {i.split(': ')[0]: i.split(': ')[1] for i in headers_.split('\n')}
#         async with AsyncClient(headers=headers_, timeout=common.TIMEOUT, proxies="http://PxEhRH6U:2gQvQRGD@194.226.166.86:45170") as client:#, proxies=proxies
#             adverts, positions = await wb.get_adverts_by_query_search(client, msg.text.lower())
#     except Exception as e:
#         print(e)
#         await msg.answer("Не удалось обработать запрос. Возможно неверный поисковый запрос")
#         await state.finish()
#         return
#     result = get_adverts(msg.text.lower(), adverts, positions)

    result = get_adverts_strange_method(msg.text.lower())

    print(result)
    text = f"Ваш запрос: <b>{msg.text.lower()}</b>\n\nПозиции и цена:\n"  # <b>1-ая страница</b>\n"
    for i in result:
        text += f"{i['position']} - {i['cpm']} руб.\n"
    kb = kb_user.subscribe_to_update_price("text")
    await msg.answer(text, reply_markup=kb)
    await msg.answer("Узнать ставки", reply_markup=kb_user.menu)
    await state.finish()


async def btn_check_price_in_card(call: CallbackQuery, db: AsyncSession, state: FSMContext):
    """Реагирует на кнопку 'Карточка товара'"""
    await call.answer()
    user = await db_queries.get_user(db, call.from_user.id)
    if not user:
        await call.message.answer(Texts.start)
        return
    await call.message.answer("Введите артикул конкурента")
    await state.set_state("get_scu")


async def get_scu_for_get_price(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("Артикул должен быть числом")
        return
    try:
        headers = common.get_headers()
        proxies = {
            "http": "http://Danilelmeyev:ZJDyT94Hpr@194.116.163.76:50100"
            # "https": "http://Danilelmeyev:ZJDyT94Hpr@194.116.163.76:50100"
        }
        proxies = 'http://Danilelmeyev:ZJDyT94Hpr@194.116.163.76:50100'
        async with AsyncClient(headers=headers, timeout=common.TIMEOUT, proxies=proxies) as client:
            result = await wb.get_adverts_by_scu(client, msg.text)
            print(result)
    except Exception as e:
        logger.error(e)
        return
    kb = kb_user.subscribe_to_update_price("scu")
    await msg.answer(result, reply_markup=kb)
    await msg.answer("Узнать ставки", reply_markup=kb_user.menu)
    await state.finish()


async def btn_subscribe_to_update(call: CallbackQuery, db: AsyncSession, state: FSMContext):
    """Реагирует на кнопку подписки на отслеживание цены"""
    await call.answer()
    text_or_scu = call.message.text.split("\n\n")[0].split(":")[1].strip()
    type_query = call.data.split(":")[-1].strip()
    # try:
    #     prices = await wb.get_position_with_price(query.lower())
    # except wb.BadRequestInWB:
    #     await call.message.answer("Не удалось обработать запрос")
    #     await call.message.edit_reply_markup()
    #     return 
    if type_query == "text":
        await db_queries.add_new_tracking(db, call.from_user.id, query_text=text_or_scu.lower())
    elif type_query == "scu":
        await db_queries.add_new_tracking(db, call.from_user.id, scu=int(text_or_scu))
    else:
        await call.message.answer("Не удалось добавить в список отслеживания. Попробуйте повторить запрос и потом \
                                  добавить в отслежвание")
        await state.finish()
        return
    await call.message.edit_text(call.message.text + "\n\nОтслеживается")
    await state.finish()


async def send_my_tracking(msg: Message, db: AsyncSession):
    """Реагирует на команду 'my_tracking'. Отправляет все отслеживания пользователя"""
    all_tracking = await db_queries.get_tracking_by_user_id(db, msg.from_user.id)
    if not all_tracking:
        await msg.answer("У вас нет ни одного отслеживания")
        return
    text = "Ваши отслеживания:\n"
    for tracking in all_tracking:
        text += f"{tracking.query_text if tracking.query_text else tracking.scu}\n"
    await msg.answer(text)
    await msg.answer("Узнать ставки", reply_markup=kb_user.menu)


# async def cmd_delete_tracking(msg: Message, state: FSMContext):
#     await msg.answer("Введите текст запроса, который больше не нужно отслеживать")
#     await state.set_state("get_tracking_text_for_delete")


# async def get_tracking_text_for_delete(msg: Message, db: AsyncSession, state: FSMContext):
#     await state.finish()
#     result = await db_queries.delete_tracking(db, msg.from_user.id, msg.text.lower())
#     if result:
#         await msg.answer("Готово")
#     else:
#         await msg.answer("Такого отслеживания нет. Чтобы посмотреть свои отлеживания введите команду /my_tracking")
#     await msg.answer("Выберите дейтсвие", reply_markup=kb_user.menu)


async def btn_unsubscribe(call: CallbackQuery, db: AsyncSession):
    """Кнопка для отмены отслеживания"""
    await call.answer()
    query = call.message.text.split("\n\n")[0].split(":")[1].strip()
    type_query = call.data.split(":")[-1]
    if type_query == "scu":
        await db_queries.delete_tracking(db, call.from_user.id, scu=int(query))
    else: 
        await db_queries.delete_tracking(db, call.from_user.id, query_text=query.lower())
    await call.message.delete_reply_markup()
    await call.message.answer("Выберите дейтсвие", reply_markup=kb_user.menu)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(command_my_campaigns, commands=["my_campaigns"], state='*')
    dp.register_callback_query_handler(command_my_campaign_query, lambda query: query.data.startswith("query_my_campaigns"), state='*')
    # dp.register_callback_query_handler(btn_subscribe, lambda call: call.data == "day" or call.data == "month")
    # dp.register_callback_query_handler(paid, lambda call: call.data == "paid")
    dp.register_callback_query_handler(btn_check_price_in_search, text="ads_in_search")
    dp.register_message_handler(get_search_query, state="get_search_query")
    dp.register_callback_query_handler(btn_check_price_in_card, text="ads_in_card")
    dp.register_message_handler(get_scu_for_get_price, state="get_scu")
    dp.register_callback_query_handler(btn_unsubscribe, lambda call: call.data.startswith("unsubscribe"), state="*")
    dp.register_callback_query_handler(btn_subscribe_to_update, lambda call: call.data.startswith("subscribe"), state="*")
    # dp.register_callback_query_handler(select_position_to_update, state="select_position_to_update")
    # dp.register_message_handler(get_count, state="get_count")
    dp.register_message_handler(send_my_tracking, commands=["my_tracking"])


    # dp.register_message_handler(cmd_delete_tracking, commands=["delete_tracking"])
    # dp.register_message_handler(get_tracking_text_for_delete, state="get_tracking_text_for_delete")
