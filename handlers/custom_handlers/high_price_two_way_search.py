from datetime import date, datetime

from database.botbase import TicketsInfo, User
from keyboards.inline.weather import weather
from keyboards.reply.start_the_search import start_search

from loader import bot
from site_APi.request_to_api import get_iata_code, get_tickets_price
from states.high_price_two_way import HighPriceTwoWay
from telebot.types import Message

from utils.checking_the_date import Date


@bot.message_handler(func=lambda message: message.text == 'Туда и обратно 🔁')
def search_ticket(message: Message) -> None:
    """
    Обработчик. Устанавливает первое состояние(origin), запрашивает город отправления
    :param message:
    :return:
    """
    bot.set_state(message.from_user.id, HighPriceTwoWay.origin, message.chat.id)
    bot.send_message(message.chat.id, f'Город отправления')


@bot.message_handler(state=HighPriceTwoWay.origin)
def get_origin(message: Message) -> None:
    """
    Обработчик. Запрашивает город прибытия, устанавливает второе состояние(destination). Получает и записывает
    данные о городе отправления в словарь
    :param message:
    :return:
    """
    iata_city_code = get_iata_code(message.text, 'Москва')
    if len(iata_city_code) == 0:
        bot.send_message(message.chat.id, '🫢 Что-то пошло не так!\n'
                                          'Возможно в одном из указанных городов нет аэропорта,\n'
                                          'Либо была допущена опечатка в названии города\n'
                                          'Проверьте данные и попробуйте ещё раз')
    else:
        bot.send_message(message.chat.id, 'Место назначения')
        bot.set_state(message.from_user.id, HighPriceTwoWay.destination, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['origin'] = message.text
            data['origin_iata'] = iata_city_code['origin']['iata']


@bot.message_handler(state=HighPriceTwoWay.destination)
def get_destination(message: Message) -> None:
    """
    Обработчик. Запрашивает дату отправления, устанавливает третье состояние(depart_date). Получает и записывает
    данные о месте назначения в словарь
    :param message:
    :return:
    """

    iata_city_code = get_iata_code('Москва', message.text)
    if len(iata_city_code) == 0:
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
        bot.set_state(message.from_user.id, HighPriceTwoWay.depart_date, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['destination'] = message.text
            data['destination_iata'] = iata_city_code['destination']['iata']


@bot.message_handler(state=HighPriceTwoWay.depart_date)
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
            bot.send_message(message.chat.id, f'Введите дату возвращения в формате <b>ДД ММ</b> '
                                              f'либо <b>ДД ММ ГГГГ</b>\n'
                                              f'Через пробел!\n'
                                              f'\n'
                                              f'Сегодня {today.strftime("%d.%m.%Y")}', parse_mode='html')
            bot.set_state(message.from_user.id, HighPriceTwoWay.return_date, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['depart_date'] = dep_date
        else:
            bot.send_message(message.chat.id, 'Упс🙊\n'
                                              'Кажется что-то пошло не так\n'
                                              'Попробуйте ещё раз')
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат\n'
                                          'Попробуйте ещё раз')


@bot.message_handler(state=HighPriceTwoWay.return_date)
def get_return_date(message: Message):
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

            if ticket_price['success'] is not True or len(ticket_price['data']) == 0:
                bot.send_message(message.chat.id, '❎ По вашему запросу нет данных.\n'
                                                  'Попробуйте ещё раз', reply_markup=start_search())
                bot.delete_state(message.from_user.id, message.chat.id)

            else:
                high_price_ticket = sorted(ticket_price['data'], key=lambda x: x['price'], reverse=True)

                dep_date_text = datetime.strptime(
                    high_price_ticket[0]["departure_at"], '%Y-%m-%dT%H:%M:%S%z'
                )
                ret_date_text = datetime.strptime(
                    high_price_ticket[0]["return_at"], '%Y-%m-%dT%H:%M:%S%z'
                )

                text = (
                    f'<b>{data["origin"].capitalize()} - {data["destination"].capitalize()}</b>\n\n'
                    f'Дата и время отправления 🕑 :\n{dep_date_text.date()} - {dep_date_text.time()}\n'
                    f'Дата и время возвращения 🕗 :\n{ret_date_text.date()} - {ret_date_text.time()}\n'
                    f'Цена 📈 : <b>{high_price_ticket[0]["price"]} {ticket_price["currency"]}</b>\n'
                    f'Номер рейса #️⃣ : {high_price_ticket[0]["flight_number"]}\n'
                    f'Кол-во остановок на пути ➡️⛔️: {high_price_ticket[0]["transfers"]}\n'
                    f'Кол-во остановок на обратном пути ⛔️⬅️: {high_price_ticket[0]["return_transfers"]}'
                )

                bot.send_message(
                    message.chat.id, text,
                    reply_markup=weather(high_price_ticket[0]['link'], data['destination']),
                    parse_mode='html'
                )
                bot.send_message(
                    message.chat.id,
                    f'Нажав на кнопку "Погода", вы можете узнать, '
                    f'какая погода в городе {data["destination"].capitalize()}',
                    reply_markup=start_search()
                )

            TicketsInfo.create(
                user_id=User.get(user_id=message.from_user.id),
                origin=data['origin'],
                origin_iata=data['origin_iata'],
                destination=data['destination'],
                destination_iata=data['destination_iata'],
                depart_date=data['depart_date'],
                return_date=data['return_date']
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
