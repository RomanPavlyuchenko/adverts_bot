import asyncio
import logging
from datetime import date, timedelta
from enum import Enum

from aiogram import Bot
from pyqiwip2p import AioQiwiP2P
from pyqiwip2p.AioQiwip2p import Bill
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.keyboards.kb_user import menu
from tgbot.services.db_queries import add_user


class BillStatus(Enum):
    WAITING = "WAITING"
    PAID = "PAID"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


RELATION_STATUS = {"REJECTED": BillStatus.REJECTED, "WAITING": BillStatus.WAITING,
                   "PAID": BillStatus.PAID, "EXPIRED": BillStatus.EXPIRED}


class Payment:
    def __init__(self, amount: int, period: int, comment: str, qiwi: AioQiwiP2P):
        self._amount = amount
        # self._user_id = user_id
        self._qiwi = qiwi
        self._comment = comment
        self.period = period
        self.bill: Bill | None = None

    async def create_bill(self) -> str:
        self.bill = await self._qiwi.bill(amount=self._amount, currency="RUB", comment=self._comment, lifetime=15)
        return self.bill.pay_url

    async def get_payment_status(self) -> BillStatus:
        bill = await self._qiwi.check(bill_id=self.bill.bill_id)
        return RELATION_STATUS[bill.status]


async def check_payment_process(user_id: int, db: AsyncSession, bot: Bot, payment: Payment):
#     while True:
#         await asyncio.sleep(2 * 60)
#         status = await payment.get_payment_status()
#         # logging.info('Запустился чек транзы')
#         if status == BillStatus.PAID:
#             subscribe = date.today() + timedelta(days=payment.period)
#             # logging.info(subscribe)
#             await add_user(db, user_id, payment.period)
#             # logging.info('Прошла запись')
#             await bot.send_message(user_id, f"Оплата прошла успешно. Ваша подписка активна до {subscribe}")
#             await bot.send_document(open('/root/bots/bot_adverts/docs/Пользовательское_соглашение.pdf', 'rb'))
#             await bot.send_message(user_id, 'https://t.me/robo_wb/1226')
#             await bot.send_video(user_id, open('/root/bots/bot_adverts/video/', 'rb'),
#                                  caption='''Видео инструкция по использованию бота,
                                 
# Примечание: Бот меняет ставки раз в 5 минут. Удаляет не нужные ключевые фразы раз в 15 минут.''', width=1920, height=1080)
#             await bot.send_message()
#             # await bot.send_message(user_id, "https://t.me/robo_wb/573 - инструкция")
#             await bot.send_message(user_id, "Выберите команду", reply_markup=menu)
#             await bot.send_message(195798144, f"{user_id}:{status}:{payment.period} {payment.amount}")

#             return
#         if status == BillStatus.EXPIRED:
#             await bot.send_message(user_id, "Истекло время оплаты. Чтобы начать заново нажмите /start")
#             return
#         if status == BillStatus.REJECTED:
#             await bot.send_message(user_id, "Платеж отклонен. Чтобы начать заново нажмите /start")
#             return
    subscribe = date.today() + timedelta(days=1)
    await add_user(db, user_id, payment)
    await bot.send_document(open('/root/bots/bot_adverts/docs/Пользовательское_соглашение.pdf', 'rb'))
    await bot.send_message(user_id, 'https://t.me/robo_wb/1226')
    await bot.send_video(user_id, open('/root/bots/bot_adverts/video/', 'rb'),
                            caption='''Видео инструкция по использованию бота,
                            
Примечание: Бот меняет ставки раз в 5 минут. Удаляет не нужные ключевые фразы раз в 15 минут.''', width=1920, height=1080)
    await bot.send_message()
    # await bot.send_message(user_id, "https://t.me/robo_wb/573 - инструкция")
    await bot.send_message(user_id, "Выберите команду", reply_markup=menu)

