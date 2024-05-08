from datetime import date, datetime

from database.botbase import User
from keyboards.inline.weather import weather

from loader import bot
from site_APi.request_to_api import get_iata_code, get_tickets_price
from states.all_tickets import AllTickets
from telebot.types import Message

from utils.checking_the_date import Date
from utils.create_database_entry import database_entry


@bot.message_handler(commands=['all'])
def search_ticket(message: Message) -> None:
    """
    Обработчик. Устанавливает первое состояние(origin), запрашивает город отправления
    :param message:
    :return:
    """
    bot.set_state(message.from_user.id, AllTickets.origin, message.chat.id)
    bot.send_message(message.chat.id, f'Город отправления')


@bot.message_handler(state=AllTickets.origin)
def get_origin(message: Message) -> None:
    """
    Обработчик. Запрашивает город прибытия, устанавливает второе состояние(destination). Получает и записывает
    данные о городе отправления в словарь
    :param message:
    :return:
    """
    iata_city_code = get_iata_code(message.text, 'Москва')

    if iata_city_code == 'error':
        bot.send_message(message.chat.id, 'Вышло время ожидания ответа от сервера.\n'
                                          'Возможно у вас плохое соединение с сетью Интернет\n'
                                          'Попробуйте ещё раз')
        bot.delete_state(message.from_user.id, message.chat.id)

    elif len(iata_city_code) == 0:
        bot.send_message(message.chat.id, '🫢 Что-то пошло не так!\n'
                                          'Возможно в одном из указанных городов нет аэропорта,\n'
                                          'Либо была допущена опечатка в названии города\n'
                                          'Проверьте данные и попробуйте ещё раз')

    else:
        bot.send_message(message.chat.id, 'Место назначения')
        bot.set_state(message.from_user.id, AllTickets.destination, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['origin'] = message.text.capitalize()
            data['origin_iata'] = iata_city_code['origin']['iata']


@bot.message_handler(state=AllTickets.destination)
def get_destination(message: Message) -> None:
    """
    Обработчик. Запрашивает дату отправления, устанавливает третье состояние(depart_date). Получает и записывает
    данные о месте назначения в словарь
    :param message:
    :return:
    """
    iata_city_code = get_iata_code('Москва', message.text)

    if iata_city_code == 'error':
        bot.send_message(message.chat.id, 'Вышло время ожидания ответа от сервера.\n'
                                          'Возможно у вас плохое соединение с сетью Интернет\n'
                                          'Попробуйте ещё раз')
        bot.delete_state(message.from_user.id, message.chat.id)

    elif len(iata_city_code) == 0:
        bot.send_message(message.chat.id, '🫢 Что-то пошло не так!\n'
                                          'Возможно в одном из указанных городов нет аэропорта,\n'
                                          'Либо была допущена опечатка в названии города\n'
                                          'Проверьте данные и попробуйте ещё раз')
    else:
        today = date.today()
        bot.send_message(message.chat.id, f'Введите дату отправления в формате <b>ДД ММ</b> либо <b>ДД ММ ГГГГ</b>\n'
                                          f'Через пробел!\n'
                                          f'\n'
                                          f'Сегодня {today.strftime("%d.%m.%Y")}', parse_mode='html')
        bot.set_state(message.from_user.id, AllTickets.depart_date, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['destination'] = message.text.capitalize()
            data['destination_iata'] = iata_city_code['destination']['iata']


@bot.message_handler(state=AllTickets.depart_date)
def get_depart_date(message: Message) -> None:
    """
    Обработчик. Запрашивает дату возвращения, устанавливает четвёртое состояние(return_date)
    :param message:
    :return:
    """
    try:
        day, month, year = Date.splitting_the_date(message.text)
        dep_date = f'{year}-{month}-{day}'

        if Date.is_date_valid(dep_date):
            today = date.today()
            bot.send_message(message.chat.id, f'Если вам нужен билет в обратную сторону, '
                                              f'введите дату возвращения в формате <b>ДД ММ</b>'
                                              f' либо <b>ДД ММ ГГГГ</b>\n'
                                              f'Через пробел!\n'
                                              f'В противном случае введите слово <b>Нет</b>\n'
                                              f'\n'
                                              f'Сегодня {today.strftime("%d.%m.%Y")}', parse_mode='html')
            bot.set_state(message.from_user.id, AllTickets.return_date, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['depart_date'] = dep_date
        else:
            bot.send_message(message.chat.id, 'Упс🙊\n'
                                              'Кажется что-то пошло не так\n'
                                              'Попробуйте ещё раз')
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат\n'
                                          'Попробуйте ещё раз')


@bot.message_handler(state=AllTickets.return_date)
def get_return_date(message: Message):
    if message.text.lower() == 'нет':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['return_date'] = None
        ticket_price = get_tickets_price(
            orig=data['origin_iata'], dest=data['destination_iata'],
            dep_date=data['depart_date'], way='true'
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

                text = (
                    f'<b>{data["origin"].capitalize()} - {data["destination"].capitalize()}</b>\n\n'
                    f'Билет №{count}\n'
                    f'Дата и время отправления 🕑 :\n{dep_date_text.date()} - {dep_date_text.time()}\n'
                    f'Цена 📈 : <b>{ticket_price["data"][ind]["price"]} {ticket_price["currency"]}</b>\n'
                    f'Номер рейса #️⃣ : {ticket_price["data"][ind]["flight_number"]}\n'
                    f'Кол-во остановок на пути ➡️⛔️: {ticket_price["data"][ind]["transfers"]}\n'
                )
                count += 1

                bot.send_message(
                    message.chat.id, text,
                    reply_markup=weather(ticket_price["data"][ind]['link'], data['destination']),
                    parse_mode='html'
                )
            bot.send_message(
                message.chat.id,
                f'Нажав на кнопку "Погода", вы можете узнать, '
                f'какая погода в городе {data["destination"].capitalize()}'
            )
        database_entry(
            user=User.get(user_id=message.from_user.id), orig=data['origin'], orig_i=data['origin_iata'],
            dest=data['destination'], dest_i=data['destination_iata'], dep_date=data['depart_date'],
            ret_date=data['return_date']
        )
        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        try:
            day, month, year = Date.splitting_the_date(message.text)
            ret_date = f'{year}-{month}-{day}'

            if Date.is_date_valid(ret_date):
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['return_date'] = ret_date

                ticket_price = get_tickets_price(
                    orig=data['origin_iata'], dest=data['destination_iata'],
                    dep_date=data['depart_date'], ret_date=data['return_date']
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
                            f'<b>{data["origin"].capitalize()} - {data["destination"].capitalize()}</b>\n\n'
                            f'Билет №{count}\n'
                            f'Дата и время отправления 🕑 :\n{dep_date_text.date()} - {dep_date_text.time()}\n'
                            f'Дата и время возвращения 🕗 :\n{ret_date_text.date()} - {ret_date_text.time()}\n'
                            f'Цена 📈 : <b>{ticket_price["data"][ind]["price"]} {ticket_price["currency"]}</b>\n'
                            f'Номер рейса #️⃣ : {ticket_price["data"][ind]["flight_number"]}\n'
                            f'Кол-во остановок на пути ➡️⛔️: {ticket_price["data"][ind]["transfers"]}\n'
                            f'Кол-во остановок на обратном пути ⛔️⬅️: {ticket_price["data"][ind]["return_transfers"]}'
                        )
                        count += 1

                        bot.send_message(
                            message.chat.id, text,
                            reply_markup=weather(ticket_price["data"][ind]['link'], data['destination']),
                            parse_mode='html'
                        )
                    bot.send_message(
                        message.chat.id,
                        f'Нажав на кнопку "Погода", вы можете узнать, '
                        f'какая погода в городе {data["destination"].capitalize()}'
                    )

                database_entry(
                    user=User.get(user_id=message.from_user.id), orig=data['origin'], orig_i=data['origin_iata'],
                    dest=data['destination'], dest_i=data['destination_iata'], dep_date=data['depart_date'],
                    ret_date=data['return_date']
                )
                bot.delete_state(message.from_user.id, message.chat.id)

            else:
                bot.send_message(message.chat.id, 'Упс🙊\n'
                                                  'Кажется что-то пошло не так\n'
                                                  'Попробуйте ещё раз')
        except ValueError:
            bot.send_message(message.chat.id, 'Неверный формат\n'
                                              'Попробуйте ещё раз')


if __name__ == '__main__':
    search_ticket()
