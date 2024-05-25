from datetime import date

from database.botbase import User

from loader import bot
from site_APi.request_to_api import get_iata_code
from states.all_tickets import AllTickets
from telebot.types import Message

from utils.checking_the_date import Date
from utils.create_database_entry import database_entry
from utils.output_of_query_results import finding_one_way_ticket, finding_two_way_ticket


@bot.message_handler(commands=['all'])
def search_ticket(message: Message) -> None:
    """
    Обработчик. Устанавливает первое состояние(origin), запрашивает город отправления
    :param message:
    :return:
    """
    bot.set_state(message.from_user.id, AllTickets.origin, message.chat.id)
    bot.send_message(message.chat.id, f'Введите город отправления и город прибытия\n'
                                      f'<b>Через пробел!</b>', parse_mode='html')


@bot.message_handler(state=AllTickets.origin)
def get_origin(message: Message) -> None:
    """
    Обработчик. Запрашивает город прибытия, устанавливает второе состояние(destination). Получает и записывает
    данные о городе отправления в словарь
    :param message:
    :return:
    """
    try:
        origin_city, destination_city = message.text.split(' ')
        iata_city_code = get_iata_code(origin_city, destination_city)

        if iata_city_code == 'error':
            bot.send_message(message.chat.id, 'Вышло время ожидания ответа от сервера.\n'
                                              'Возможно у вас плохое соединение с сетью Интернет\n'
                                              'Попробуйте ещё раз')
            bot.delete_state(message.from_user.id, message.chat.id)

        elif len(iata_city_code) == 0:
            bot.send_message(message.chat.id, 'Что-то пошло не так!\n'
                                              'Возможно в одном из указанных городов нет аэропорта,\n'
                                              'Либо была допущена опечатка в названии города\n'
                                              'Проверьте данные и попробуйте ещё раз')

        else:
            today = date.today()
            bot.send_message(message.chat.id,
                             f'Введите дату отправления в формате <b>ДД ММ</b> либо <b>ДД ММ ГГГГ</b>\n'
                             f'Через пробел!\n'
                             f'\n'
                             f'Сегодня {today.strftime("%d.%m.%Y")}', parse_mode='html')
            bot.set_state(message.from_user.id, AllTickets.depart_date, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['origin'] = origin_city.capitalize()
                data['origin_iata'] = iata_city_code['origin']['iata']
                data['destination'] = destination_city.capitalize()
                data['destination_iata'] = iata_city_code['destination']['iata']
    except ValueError:
        bot.send_message(message.chat.id, 'Для поиска билетов введите город прибытия')


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
        finding_one_way_ticket(
            message, origin_i=data['origin_iata'], destination_i=data['destination_iata'],
            origin=data['origin'], destination=data['destination'], dep_date=data['depart_date']
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

                finding_two_way_ticket(
                    message, origin_i=data['origin_iata'], destination_i=data['destination_iata'],
                    origin=data['origin'], destination=data['destination'], dep_date=data['depart_date'],
                    ret_date=data['return_date']
                )
                database_entry(
                    user=User.get(user_id=message.from_user.id), orig=data['origin'], orig_i=data['origin_iata'],
                    dest=data['destination'], dest_i=data['destination_iata'], dep_date=data['depart_date'],
                    ret_date=data['return_date']
                )
                bot.delete_state(message.from_user.id, message.chat.id)

            else:
                raise ValueError
        except ValueError:
            bot.send_message(message.chat.id, 'Неверный формат\n'
                                              'Попробуйте ещё раз')


if __name__ == '__main__':
    search_ticket()
