from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message

from loader import bot


def start_search():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Начать поиск'))
    return keyboard


@bot.message_handler(func=lambda message: message.text == 'Начать поиск')
def search(message: Message):
    bot.send_message(message.chat.id, "Чтобы начать поиск билета выберите одну "
                                      "из следующих команд:\n\n"
                                      "/low - поиск самого дешевого билета\n\n"
                                      "/high - поиск самого дорогого билета\n\n"
                                      "/custom - поиск билетов в заданном диапазоне\n\n"
                                      "/history - история запросов")
