from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def further_button():
    """
    Reply кнопка для продолжения сценария после выбора даты
    :return:
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton('Дальше ➡️'))
    return markup
