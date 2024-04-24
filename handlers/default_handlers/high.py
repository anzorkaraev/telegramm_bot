from telebot.types import Message

from keyboards.reply.high_ticket_choice import direction_choice
from loader import bot


@bot.message_handler(commands=['high'])
def bot_high(message: Message):
    """
    Обработчик команды /high. Запускает сценарий поиска самого дешевого билета
    :param message:
    :return:
    """
    bot.send_message(message.chat.id, 'Вам нужен билет в одну сторону или в обе?', reply_markup=direction_choice())
