from peewee import IntegrityError
from telebot.types import Message

from database.botbase import User

from loader import bot


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    """
    Обработчик команды /start. Приветствует пользователя и создает запись в БД
    :param message:
    :return:
    """
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    try:
        User.create(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        bot.reply_to(message, f"Здравствуйте, {first_name}!\n Добро пожаловать в наш бот!\n"
                              f"Здесь вы сможете найти подходящий авиабилет!")
        bot.send_message(message.chat.id, "Чтобы начать поиск билета выберите одну "
                                          "из следующих команд:\n\n"
                                          "/low - поиск самого дешевого билета\n"
                                          "/high - поиск самого дорогого билета\n"
                                          "/custom - поиск билетов в заданном диапазоне\n"
                                          "/history - история запросов")
    except IntegrityError:
        bot.reply_to(message, f"Здравствуйте, {first_name}!\n Добро пожаловать в наш бот!\n"
                              f"Здесь вы сможете найти подходящий авиабилет!")
        bot.send_message(message.chat.id, "Чтобы начать поиск билета выберите одну "
                                          "из следующих команд:\n\n"
                                          "/low - поиск самого дешевого билета\n"
                                          "/high - поиск самого дорогого билета\n"
                                          "/custom - поиск билетов в заданном диапазоне\n"
                                          "/history - история запросов")


