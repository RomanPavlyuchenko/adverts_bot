
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat
from aiogram.utils.exceptions import ChatNotFound
from pyqiwip2p import AioQiwiP2P

from tgbot.config import Settings
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.ads_setting import register_ads_setting
from tgbot.handlers.ads_setting_utils import register_user_ads_settings_utils
from tgbot.handlers.my_campaigns import register_user_my_campaigns
from tgbot.handlers.user import register_user
from tgbot.handlers.payment import register_payment
from tgbot.middlewares.db import DbMiddleware
from tgbot.services.db_connection import create_session_factory, init_models
from tgbot.services.db_queries import get_users, get_campaigns_by_user_id, add_wbacc_to_user
from tgbot.services.logger import setup_logger
from tgbot.services.scheduler import add_jobs, update_wb_token
from tgbot.utils.bot_send_message import check_new_messages
from tgbot.utils.utils import campaign_is_active, auth


def register_all_middlewares(dp):
    dp.setup_middleware(DbMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_payment(dp)
    register_user(dp)
    register_ads_setting(dp)
    register_user_ads_settings_utils(dp)
    register_user_my_campaigns(dp)


async def set_commands(dp: Dispatcher):
    config = dp.bot.get('config')
    admin_ids = config.tg.admins
    await dp.bot.set_my_commands(
        commands=[BotCommand('start', 'Старт'), BotCommand('my_campaigns', 'Мои кампании'), BotCommand('choice_acc', 'Выбрать рабочий аккаунт')]  # , BotCommand("my_tracking", "Мои отслеживания"),
                  # BotCommand("delete_tracking", "Удалить отслеживание")]
    )
    commands_for_admin = [
        BotCommand('start', 'Старт'),
        BotCommand('my_campaigns', 'Мои кампании'),
        BotCommand('choice_acc', 'Выбрать рабочий аккаунт'),
        # BotCommand("help", "Руководство пользователя"),
        BotCommand("add_user", "Добавить пользователя бота"),
        BotCommand("sending", "Рассылка сообщения пользователям"),
        BotCommand("count", "Количество пользователей"),
        BotCommand("delete_user", "Удалить пользователя"),

        # BotCommand("my_tracking", "Мои отслеживания"),
        # BotCommand("delete_tracking", "Удалить отслеживание"),
    ]
    for admin_id in admin_ids:
        try:
            await dp.bot.set_my_commands(
                commands=commands_for_admin,
                scope=BotCommandScopeChat(admin_id)
            )
        except ChatNotFound as er:
            logging.error(f'Установка команд для администратора {admin_id}: {er}')


async def main():
    # setup_logger("INFO")
    config = Settings()
    database_url = f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.name}"

    logging.info("Starting Bot")

    # if config.tg.use_redis:
    #     storage = RedisStorage()
    # else:
    storage = MemoryStorage()

    bot = Bot(token=config.tg.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    qiwi = AioQiwiP2P(auth_key=config.tg.qiwi_token)
    #await init_models(database_url)
    bot['config'] = config
    bot["session_factory"] = session_factory = create_session_factory(database_url)
    bot["qiwi"] = qiwi
    await update_wb_token(session_factory)
    bot.set_current(bot)
    bot_info = await bot.get_me()
    logging.info(f'<yellow>Name: <b>{bot_info["first_name"]}</b>, username: {bot_info["username"]}</yellow>')

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)
    await set_commands(dp)
    scheduler = add_jobs(bot, session_factory)
    # start
    # init campagins
    async with session_factory() as session:

        users = await get_users(session)
        for user in users:
            # await bot.send_message(user.id, f'test', reply_markup=btn_query_my_campaigns())
            campaigns = await get_campaigns_by_user_id(session, user.id)
            if campaigns:
                for campaign in campaigns:
                    campaign_is_active.add_campaign(campaign.campaign_id, campaign.is_active, campaign.place)

        #print('satrt bot campaign_is_active', campaign_is_active.campaigns)
    try:
        scheduler.start()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        session = await bot.get_session()
        await session.close()
        # await bot.session.close()


if __name__ == '__main__':
    setup_logger("INFO")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
