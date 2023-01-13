import asyncio
from aiogram import Dispatcher, Bot
from sqlalchemy.orm.session import sessionmaker

from tgbot.services.db_queries import get_all_messages, delete_message


async def check_new_messages(bot: Bot, session_factory: sessionmaker):
    async with session_factory() as session:
        new_messages = await get_all_messages(session)
        for i in new_messages:
            try:
                await bot.send_message(i.cid, i.text)
                await delete_message(session, i.message_id)
            except Exception as e:
                print(e)
