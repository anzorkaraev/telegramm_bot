import time

from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from database.botbase import TicketsInfo, User
from loader import bot


@bot.message_handler(commands=['history'])
def get_history(message: Message, page: int = 0):
    """
    Обработчик. Выводит все запросы конкретного пользователя
    :param page:
    :param message:
    :return:
    """

    user_tickets = list(TicketsInfo.select().where(TicketsInfo.user == '715885177'))

    page_quantity = len(user_tickets)
    left = page - 1 if page != 0 else page_quantity - 1
    right = page + 1 if page != page_quantity - 1 else 0

    keyboard = InlineKeyboardMarkup(row_width=3)
    btn1 = InlineKeyboardButton('<--Пред.', callback_data=f'go {left}')
    btn2 = InlineKeyboardButton(f'{str(page + 1)}/{str(page_quantity)}', callback_data='_')
    btn3 = InlineKeyboardButton('След.-->', callback_data=f'go {right}')
    keyboard.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, 'Секунду...')
    time.sleep(1)
    if user_tickets:
        text = (
            f'Город отправления: <b>{user_tickets[page].origin}</b>\n'
            f'Город прибытия: <b>{user_tickets[page].destination}</b>\n'
            f'Дата отправления: <b>{user_tickets[page].depart_date}</b>\n'
            f'Дата возвращения: <b>{user_tickets[page].return_date}</b>\n'
        )
        bot.edit_message_text(message.chat.id, message.message_id, text, parse_mode='html', reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id, 'Вы не сделали ни одного запроса')


@bot.callback_query_handler(func=lambda call: call.data.startswith('go'))
def callback(call):
    if 'go' in call.data:
        page = int(call.data.split(' ')[1])
        bot.delete_message(call.message.chat.id, call.message.message_id)
        get_history(call.message, page=page)


if __name__ == '__main__':
    get_history()
