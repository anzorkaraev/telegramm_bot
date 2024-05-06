from telebot.types import Message

from database.botbase import TicketsInfo
from loader import bot


@bot.message_handler(commands=['history'])
def get_history(message: Message):
    """
    Обработчик. Выводит все запросы конкретного пользователя
    :param message:
    :return:
    """
    user_tickets = TicketsInfo.select().where(TicketsInfo.user == message.from_user.id)
    if user_tickets:
        count = 1
        bot.send_message(message.chat.id, 'История ваших запросов')
        for ticket in user_tickets:
            text = (
                f'<b>Запрос {count}\n</b>'
                f'Город отправления: <b>{ticket.origin}</b>\n'
                f'Город прибытия: <b>{ticket.destination}</b>\n'
                f'Дата отправления: <b>{ticket.depart_date}</b>\n'
                f'Дата возвращения: <b>{ticket.return_date}</b>\n'
            )
            count += 1
            bot.send_message(message.chat.id, text, parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Вы не сделали ни одного запроса')


if __name__ == '__main__':
    get_history()
