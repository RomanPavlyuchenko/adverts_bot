from aiogram.types import ReplyKeyboardMarkup


back_message = '👈 Назад'
confirm_message = '✅ Подтвердить'
all_right_message = '✅ Все верно'
cancel_message = '🚫 Отменить'
change_message = '✍️  Изменить'
ready_message = '✅  Готово'


def cancel_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(cancel_message)
    return markup