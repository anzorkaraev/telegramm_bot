from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def direction_choice():
    """
    Reply кнопка. Пользователь указывает нужен ли ему обратный билет
    :return:
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = KeyboardButton('Только туда ➡️')
    btn2 = KeyboardButton('Туда и обратно 🔁')
    markup.add(btn1, btn2)
    return markup
