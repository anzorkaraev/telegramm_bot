from peewee import IntegrityError
from telebot.types import Message

from database.botbase import User
from keyboards.reply.start_the_search import start_search

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
        bot.reply_to(message, f"Здравствуйте, {first_name}!\nДобро пожаловать в наш бот!\n"
                              f"Здесь вы сможете найти подходящий авиабилет!", reply_markup=start_search())
    except IntegrityError:
        bot.reply_to(message, f"Здравствуйте, {first_name}!\nДобро пожаловать в наш бот!\n"
                              f"Здесь вы сможете найти подходящий авиабилет!", reply_markup=start_search())
