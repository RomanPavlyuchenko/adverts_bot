import logging

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile
from sqlalchemy.ext.asyncio import AsyncSession
from tgbot.keyboards import kb_user
from tgbot.services.payment import Payment, check_payment_process


async def btn_subscribe(call: CallbackQuery, db: AsyncSession, state: FSMContext):
    await call.answer()
    qiwi = call.bot.get("qiwi")
    period = "день" if call.data == "day" else "месяц"
    payment = Payment(
        amount=900 if call.data == "day" else 2900,
        comment=f"Один {period} подписки на Рекламщика",
        period=1 if call.data == "day" else 30,
        qiwi=qiwi
    )
    payment_url = await payment.create_bill()
    await call.message.answer(f"Вы выбрали 1 {period} подписки. Для перехода к окну оплаты, нажмите \"Оплатить\".",
                              reply_markup=kb_user.pay(payment_url))
    await call.message.answer_document(open('/root/bots/bot_adverts/docs/Политика оплаты.pdf', 'rb'))
    await call.message.answer('Подтверждение оплаты занимает до 5 минут')
    await check_payment_process(call.from_user.id, db, call.bot, payment)


def register_payment(dp: Dispatcher):
    dp.register_callback_query_handler(btn_subscribe, lambda call: call.data == "day" or call.data == "month")

