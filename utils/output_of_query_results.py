from datetime import date, datetime

from telebot.types import Message

from keyboards.inline.weather import weather
from loader import bot
from site_APi.request_to_api import get_tickets_price


def finding_one_way_ticket(
        message: Message = None, origin_i: str = None, destination_i: str = None, origin: str = None,
        destination: str = None, dep_date: date = None,
        ):
    ticket_price = get_tickets_price(
        orig=origin_i, dest=destination_i,
        dep_date=dep_date, way='true'
    )

    if ticket_price == 'error':
        bot.send_message(message.chat.id, 'Вышло время ожидания ответа от сервера.\n'
                                          'Возможно у вас плохое соединение с сетью Интернет\n'
                                          'Попробуйте ещё раз')
        bot.delete_state(message.from_user.id, message.chat.id)

    elif ticket_price['success'] is not True or len(ticket_price['data']) == 0:
        bot.send_message(message.chat.id, 'По вашему запросу нет данных.\n'
                                          'Попробуйте ещё раз')
        bot.delete_state(message.from_user.id, message.chat.id)

    else:
        dep_date_text = datetime.strptime(
            ticket_price["data"][0]["departure_at"], '%Y-%m-%dT%H:%M:%S%z'
        )

        text = (
            f'<b>{origin.capitalize()} - {destination.capitalize()}</b>\n\n'
            f'Дата и время отправления:\n<u>{dep_date_text.date()} - {dep_date_text.time()}</u>\n'
            f'Цена: <b>{ticket_price["data"][0]["price"]} {ticket_price["currency"]}</b>\n'
            f'Номер рейса: {ticket_price["data"][0]["flight_number"]}\n'
            f'Кол-во остановок на пути: {ticket_price["data"][0]["transfers"]}\n'
        )

        bot.send_message(
            message.chat.id, text,
            reply_markup=weather(ticket_price["data"][0]['link'], destination),
            parse_mode='html'
        )


def finding_two_way_ticket(
        message: Message = None, origin_i: str = None, destination_i: str = None, origin: str = None,
        destination: str = None, dep_date: date = None, ret_date: date = None
        ):
    ticket_price = get_tickets_price(
                        orig=origin_i, dest=destination_i,
                        dep_date=dep_date, ret_date=ret_date
                    )

    if ticket_price == 'error':
        bot.send_message(message.chat.id, 'Вышло время ожидания ответа от сервера.\n'
                                          'Возможно у вас плохое соединение с сетью Интернет\n'
                                          'Попробуйте ещё раз')
        bot.delete_state(message.from_user.id, message.chat.id)

    elif ticket_price['success'] is not True or len(ticket_price['data']) == 0:
        bot.send_message(message.chat.id, '❎ По вашему запросу нет данных.\n'
                                          'Попробуйте ещё раз')
        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        count = 1
        for ind in range(len(ticket_price['data'])):
            dep_date_text = datetime.strptime(
                ticket_price["data"][ind]["departure_at"], '%Y-%m-%dT%H:%M:%S%z'
            )
            ret_date_text = datetime.strptime(
                ticket_price["data"][ind]["return_at"], '%Y-%m-%dT%H:%M:%S%z'
            )

            text = (
                f'<b>{origin.capitalize()} - {destination.capitalize()}</b>\n\n'
                f'Билет №{count}\n'
                f'Дата и время отправления:\n<u>{dep_date_text.date()} - {dep_date_text.time()}</u>\n'
                f'Дата и время возвращения:\n<u>{ret_date_text.date()} - {ret_date_text.time()}</u>\n'
                f'Цена: <b>{ticket_price["data"][ind]["price"]} {ticket_price["currency"]}</b>\n'
                f'Номер рейса: {ticket_price["data"][ind]["flight_number"]}\n'
                f'Кол-во остановок на пути: {ticket_price["data"][ind]["transfers"]}\n'
                f'Кол-во остановок на обратном пути: {ticket_price["data"][ind]["return_transfers"]}'
            )
            count += 1

            bot.send_message(
                message.chat.id, text,
                reply_markup=weather(ticket_price["data"][ind]['link'], destination),
                parse_mode='html'
            )
