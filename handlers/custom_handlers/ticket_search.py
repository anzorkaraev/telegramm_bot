from datetime import date, datetime

from telegram_bot_calendar import WMonthTelegramCalendar

from database.botbase import TicketsInfo, User
from keyboards.inline.button_for_booking import reserve
from keyboards.reply.further import further_button

from loader import bot
from site_APi.request_to_api import get_iata_code, get_tickets_price, get_weather
from states.ticket_search_states import TicketsSearchState
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils.bot_logger import BotLogger


logger = BotLogger('logs.log')


@bot.message_handler(func=lambda message: message.text == 'В обе стороны 🔁')
def search_ticket(message: Message) -> None:
    """
    Обработчик. Устанавливает первое состояние(origin), запрашивает город отправления
    :param message:
    :return:
    """
    bot.set_state(message.from_user.id, TicketsSearchState.origin, message.chat.id)
    bot.send_message(message.chat.id, f'Город отправления')


@bot.message_handler(state=TicketsSearchState.origin)
def get_origin(message: Message) -> None:
    """
    Обработчик. Запрашивает город прибытия, устанавливает второе состояние(destination). Получает и записывает
    данные о городе отправления в словарь
    :param message:
    :return:
    """
    bot.send_message(message.chat.id, 'Место назначения')
    bot.set_state(message.from_user.id, TicketsSearchState.destination, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['origin'] = message.text


@bot.message_handler(state=TicketsSearchState.destination)
def get_destination(message: Message) -> None:
    """
    Обработчик. Запрашивает дату отправления, устанавливает третье состояние(depart_date). Получает и записывает
    данные о месте назначения в словарь
    :param message:
    :return:
    """
    depart_calendar = WMonthTelegramCalendar(calendar_id=1, min_date=date.today(), locale='ru').build()

    bot.send_message(message.chat.id, 'Дата отправления\n')
    bot.send_message(message.chat.id, 'Выберите дату 🗓', reply_markup=depart_calendar)
    bot.set_state(message.from_user.id, TicketsSearchState.depart_date, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['destination'] = message.text


@bot.callback_query_handler(func=WMonthTelegramCalendar.func(calendar_id=1))
def get_depart_date(callback: CallbackQuery):
    logger.log_info(f'call {callback}')
    """
    Обработчик обратного запроса.  Получает и записывает
    дату отправления в словарь
    :param callback:
    :return:
    """
    result, key, step = WMonthTelegramCalendar().process(callback.data)
    if not result and key:
        bot.edit_message_text(f"Select {step}",
                              callback.message.chat.id,
                              callback.message.message_id,
                              reply_markup=key)
    elif result:
        mess = bot.edit_message_text(f"{result}",
                                     callback.message.chat.id,
                                     callback.message.message_id)

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
            data['depart_date'] = mess.text
            logger.log_info(f'первый {data}')
        bot.register_next_step_handler(callback.message, return_date_request(callback.message))


@bot.message_handler(state=TicketsSearchState.depart_date)
def return_date_request(message: Message) -> None:
    """
    Обработчик. Запрашивает дату возвращения, устанавливает четвёртое состояние(return_date)
    :param message:
    :return:
    """
    return_calendar = WMonthTelegramCalendar(calendar_id=2, min_date=date.today(), locale='ru').build()

    bot.send_message(message.chat.id, 'Дата возвращения\n')
    bot.send_message(message.chat.id, 'Выберите дату 🗓', reply_markup=return_calendar)
    bot.set_state(message.from_user.id, TicketsSearchState.return_date, message.chat.id)


@bot.callback_query_handler(func=WMonthTelegramCalendar.func(calendar_id=2), state=TicketsSearchState.return_date)
def get_return_date(callback: CallbackQuery):
    """
     Обработчик обратного запроса.  Получает и записывает
    дату возвращения в словарь
    :param callback:
    :return:
    """
    result, key, step = WMonthTelegramCalendar().process(callback.data)
    if not result and key:
        bot.edit_message_text(f"Select {step}",
                              callback.message.chat.id,
                              callback.message.message_id,
                              reply_markup=key)
    elif result:
        mess = bot.edit_message_text(f"{result}",
                                     callback.message.chat.id,
                                     callback.message.message_id)

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
            data['return_date'] = mess.text
            logger.log_info(f'return {data}')
        bot.register_next_step_handler(callback.message, create_database_entry(callback.message))


@bot.message_handler(state=TicketsSearchState.return_date)
def create_database_entry(message: Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        logger.log_info(f'blyad {data}')
        iata_city_code = get_iata_code(data['origin'], data['destination'])
        if len(iata_city_code) == 0:
            bot.send_message(message.chat.id, '🫢 Что-то пошло не так!\n'
                                              'Возможно в одном из указанных городов нет аэропорта,\n'
                                              'Либо была допущена опечатка в названии города\n'
                                              'Проверьте данные и попробуйте ещё раз')
            bot.delete_state(message.from_user.id, message.chat.id)
        data['origin_iata'] = iata_city_code['origin']['iata']
        data['destination_iata'] = iata_city_code['destination']['iata']

        TicketsInfo.create(
            user_id=User.user_id,
            origin=data['origin'],
            origin_iata=data['origin_iata'],
            destination=data['destination'],
            destination_iata=data['destination_iata'],
            depart_date=data['depart_date'],
            return_date=data['return_date']
        )

    bot.set_state(message.from_user.id, TicketsSearchState.api_request, message.chat.id)


@bot.message_handler(state=TicketsSearchState.api_request)
def ticket_request(message: Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        ticket_price = get_tickets_price(
            orig=data['origin_iata'], dest=data['destination_iata'],
            dep_date=data['depart_date'], ret_date=data['return_date']
        )

        if ticket_price['success'] is not True:
            bot.send_message(message.chat.id, '❎ По вашему запросу нет данных.\n'
                                              'Попробуйте ещё раз')
            bot.delete_state(message.from_user.id, message.chat.id)

        low_price_ticket = sorted(ticket_price['data'], key=lambda x: x['price'])

        dep_date_text = datetime.strptime(
            low_price_ticket[0]["departure_at"], '%Y-%m-%dT%H:%M:%S%z'
        )
        ret_date_text = datetime.strptime(
            low_price_ticket[0]["return_at"], '%Y-%m-%dT%H:%M:%S%z'
        )

        text = (
            f'{data["origin"].capitalize()} - {data["destination"].capitalize ()}\n\n'
            f'Дата и время отправления 🕑 :\n{dep_date_text.date()} - {dep_date_text.time()}\n'
            f'Дата и время возвращения 🕗 :\n{ret_date_text.date()} - {ret_date_text.time()}\n'
            f'Цена 📈 : {low_price_ticket[0]["price"]} {ticket_price["currency"]}\n'
            f'Номер рейса #️⃣ : {low_price_ticket[0]["flight_number"]}\n'
            f'Кол-во остановок на пути ➡️⛔️: {low_price_ticket[0]["transfers"]}\n'
            f'Кол-во остановок на обратном пути ⛔️⬅️: {low_price_ticket[0]["return_transfers"]}'
        )

        bot.send_message(message.chat.id, text, reply_markup=reserve(low_price_ticket[0]['link']))
        # bot.send_message(message.chat.id, f'Хотите узнать какая погода в городе {data["destination"].capitalize()}?',
        #                  reply_markup=weather())
        bot.delete_state(message.from_user.id, message.chat.id)


# def weather():
#     keyboard = InlineKeyboardMarkup(row_width=2)
#     btn1 = InlineKeyboardButton('Текущая погода', callback_data='city')
#     btn2 = InlineKeyboardButton('❌', callback_data='close')
#     keyboard.add(btn1, btn2)
#     return keyboard
#
#
# @bot.callback_query_handler(func=lambda call: True, state=TicketsSearchState.api_request)
# def callback(call: CallbackQuery):
#     if call.data == 'close':
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#     if call.data == 'city':
#         with bot.retrieve_data(call.message.from_user.id, call.message.chat.id) as data:
#             dep_city_weather = get_weather(data['destination'])
#             if dep_city_weather['cod'] != 200:
#                 bot.send_message(call.message.chat.id, '🫢 Что-то пошло не так!\n'
#                                                        'Возможно была допущена опечатка в названии города\n'
#                                                        'Проверьте данные и попробуйте ещё раз')
#             text = (f'{round(dep_city_weather["main"]["temp"])}°\n'
#                     f'{dep_city_weather["weather"][0]["description"].capitalize()}\n'
#                     f'{round(dep_city_weather["main"]["temp_min"])}° / {round(dep_city_weather["main"]["temp_max"])}°')
#             bot.edit_message_text(f"{text}", call.message.chat.id, call.message.message_id)


if __name__ == '__main__':
    search_ticket()
