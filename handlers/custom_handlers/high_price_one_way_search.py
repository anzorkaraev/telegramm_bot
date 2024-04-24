from datetime import date, datetime

from database.botbase import TicketsInfo, User
from keyboards.inline.button_for_booking import reserve
from keyboards.inline.weather import weather

from loader import bot
from site_APi.request_to_api import get_iata_code, get_tickets_price
from states.high_price_one_way import HighPriceOneWay
from telebot.types import Message

from utils.bot_logger import BotLogger
from utils.checking_the_date import Date

logger = BotLogger('logs.log')


@bot.message_handler(func=lambda message: message.text == 'Только туда ➡️')
def search_ticket(message: Message) -> None:
    """
    Обработчик. Устанавливает первое состояние(origin), запрашивает город отправления
    :param message:
    :return:
    """
    bot.set_state(message.from_user.id, HighPriceOneWay.origin, message.chat.id)
    bot.send_message(message.chat.id, f'Город отправления')


@bot.message_handler(state=HighPriceOneWay.origin)
def get_origin(message: Message) -> None:
    """
    Обработчик. Запрашивает город прибытия, устанавливает второе состояние(destination). Получает и записывает
    данные о городе отправления в словарь
    :param message:
    :return:
    """
    bot.send_message(message.chat.id, 'Место назначения')
    bot.set_state(message.from_user.id, HighPriceOneWay.destination, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['origin'] = message.text


@bot.message_handler(state=HighPriceOneWay.destination)
def get_destination(message: Message) -> None:
    """
    Обработчик. Запрашивает дату отправления, устанавливает третье состояние(depart_date). Получает и записывает
    данные о месте назначения в словарь
    :param message:
    :return:
    """

    today = date.today()
    bot.send_message(message.chat.id, f'Введите дату отправления в формате <b>ДД ММ ГГГГ</b>\n'
                                      f'Через пробел!\n'
                                      f'\n'
                                      f'Сегодня {today.strftime("%d.%m.%Y")}', parse_mode='html')
    bot.set_state(message.from_user.id, HighPriceOneWay.depart_date, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['destination'] = message.text

        iata_city_code = get_iata_code(data['origin'], data['destination'])
        if len(iata_city_code) == 0:
            bot.send_message(message.chat.id, '🫢 Что-то пошло не так!\n'
                                              'Возможно в одном из указанных городов нет аэропорта,\n'
                                              'Либо была допущена опечатка в названии города\n'
                                              'Проверьте данные и попробуйте ещё раз')
            bot.delete_state(message.from_user.id, message.chat.id)
        data['origin_iata'] = iata_city_code['origin']['iata']
        data['destination_iata'] = iata_city_code['destination']['iata']


@bot.message_handler(state=HighPriceOneWay.depart_date)
def get_return_date(message: Message):
    try:
        day, month, year = message.text.split()
        dep_date = f'{year}-{month}-{day}'

        if Date.is_date_valid(dep_date):
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['depart_date'] = dep_date

                ticket_price = get_tickets_price(
                    orig=data['origin_iata'], dest=data['destination_iata'],
                    dep_date=data['depart_date'], way='true'
                )

                if ticket_price['success'] is not True:
                    bot.send_message(message.chat.id, '❎ По вашему запросу нет данных.\n'
                                                      'Попробуйте ещё раз')
                    bot.delete_state(message.from_user.id, message.chat.id)

                high_price_ticket = sorted(ticket_price['data'], key=lambda x: x['price'], reverse=True)
                logger.log_info(f'high one {high_price_ticket}')

                dep_date_text = datetime.strptime(
                    high_price_ticket[0]["departure_at"], '%Y-%m-%dT%H:%M:%S%z'
                )

                text = (
                    f'<b>{data["origin"].capitalize()} - {data["destination"].capitalize()}</b>\n\n'
                    f'Дата и время отправления 🕑 :\n{dep_date_text.date()} - {dep_date_text.time()}\n'
                    f'Цена 📈 : <b>{high_price_ticket[0]["price"]} {ticket_price["currency"]}</b>\n'
                    f'Номер рейса #️⃣ : {high_price_ticket[0]["flight_number"]}\n'
                    f'Кол-во остановок на пути ➡️⛔️: {high_price_ticket[0]["transfers"]}\n'
                )

                bot.send_message(message.chat.id, text, reply_markup=reserve(high_price_ticket[0]['link']),
                                 parse_mode='html')
                bot.send_message(message.chat.id,
                                 f'Хотите узнать какая погода в городе {data["destination"].capitalize()}?',
                                 reply_markup=weather(data['destination']))

                TicketsInfo.create(
                    user_id=User.get(user_id=message.from_user.id),
                    origin=data['origin'],
                    origin_iata=data['origin_iata'],
                    destination=data['destination'],
                    destination_iata=data['destination_iata'],
                    depart_date=data['depart_date']
                )
                bot.delete_state(message.from_user.id, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Упс🙊\n'
                                              'Кажется что-то пошло не так\n'
                                              'Попробуйте ещё раз')
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат\n'
                                          'Попробуйте ещё раз')


@bot.message_handler(state=HighPriceOneWay.api_request)
def ticket_request_h(message: Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        ticket_price = get_tickets_price(
            orig=data['origin_iata'], dest=data['destination_iata'],
            dep_date=data['depart_date'], way='true'
        )

        if ticket_price['success'] is not True:
            bot.send_message(message.chat.id, '❎ По вашему запросу нет данных.\n'
                                              'Попробуйте ещё раз')
            bot.delete_state(message.from_user.id, message.chat.id)

        high_price_ticket = sorted(ticket_price['data'], key=lambda x: x['price'], reverse=True)
        logger.log_info(f'high one {high_price_ticket}')

        dep_date_text = datetime.strptime(
            high_price_ticket[0]["departure_at"], '%Y-%m-%dT%H:%M:%S%z'
        )

        text = (
            f'<b>{data["origin"].capitalize()} - {data["destination"].capitalize()}</b>\n\n'
            f'Дата и время отправления 🕑 :\n{dep_date_text.date()} - {dep_date_text.time()}\n'
            f'Цена 📈 : <b>{high_price_ticket[0]["price"]} {ticket_price["currency"]}</b>\n'
            f'Номер рейса #️⃣ : {high_price_ticket[0]["flight_number"]}\n'
            f'Кол-во остановок на пути ➡️⛔️: {high_price_ticket[0]["transfers"]}\n'
        )

        bot.send_message(message.chat.id, text, reply_markup=reserve(high_price_ticket[0]['link']), parse_mode='html')
        bot.send_message(message.chat.id, f'Хотите узнать какая погода в городе {data["destination"].capitalize()}?',
                         reply_markup=weather(data['destination']))
        bot.delete_state(message.from_user.id, message.chat.id)


if __name__ == '__main__':
    search_ticket()
