import os

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from handlers.default_handlers.history import get_history
from loader import bot
from site_APi.request_to_api import get_weather


def weather(link: str, city: str):
    url = f'https://www.aviasales.com{link}'
    keyboard = InlineKeyboardMarkup(row_width=3)
    btn4 = InlineKeyboardButton('Погода', callback_data=city)
    btn5 = InlineKeyboardButton('Забронировать', url=url)
    keyboard.add(btn4, btn5)
    return keyboard


@bot.callback_query_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    dep_city_weather = get_weather(call.data)
    if 'go' in call.data:
        page = int(call.data.split(' ')[1])
        bot.delete_message(call.message.chat.id, call.message.message_id)
        get_history(call.message, page=page)

    elif dep_city_weather == 'error':
        bot.send_message(call.message.chat.id, 'Вышло время ожидания ответа от сервера.\n'
                                               'Возможно у вас плохое соединение с сетью Интернет\n'
                                               'Попробуйте ещё раз')

    elif dep_city_weather['cod'] != 200:
        bot.send_message(call.message.chat.id, '🫢 Что-то пошло не так!\n'
                                               'Возможно была допущена опечатка в названии города\n'
                                               'Проверьте данные и попробуйте ещё раз')

    else:
        with open(os.path.abspath(f'icons/{dep_city_weather["weather"][0]["icon"]}.png'), 'rb') as file:
            text = (
                f'<b>Погода в городе {call.data.capitalize()}</b>\n'
                f'<b>{dep_city_weather["weather"][0]["description"].capitalize()}</b>\n'
                f'Температура макс/мин: '
                f'<b>{round(dep_city_weather["main"]["temp_min"])}° / '
                f'{round(dep_city_weather["main"]["temp_max"])}°</b>\n'
                f'Температура: <b>{round(dep_city_weather["main"]["temp"])}°</b>\n'
                f'Ощущается как: <b>{round(dep_city_weather["main"]["feels_like"])}°</b>\n'
            )
            bot.send_photo(call.message.chat.id, file, caption=text, parse_mode='html')
