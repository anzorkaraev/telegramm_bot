import json

import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

from loader import bot
from site_APi.request_to_api import get_weather


def weather(link: str, city: str):
    url = f'https://www.aviasales.com{link}'
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton('Погода', callback_data=city)
    btn2 = InlineKeyboardButton('Забронировать', url=url)
    keyboard.add(btn1, btn2)
    return keyboard


@bot.callback_query_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    dep_city_weather = get_weather(call.data)
    if dep_city_weather['cod'] != 200:
        bot.send_message(call.message.chat.id, '🫢 Что-то пошло не так!\n'
                                               'Возможно была допущена опечатка в названии города\n'
                                               'Проверьте данные и попробуйте ещё раз')
    else:
        icon = requests.get(f'https://openweathermap.org/img/wn/{dep_city_weather["weather"][0]["icon"]}@2x.png')

        text = (f'<b>Погда в {call.data}</b>\n'
                f'{round(dep_city_weather["main"]["temp"])}°\n'
                f'{dep_city_weather["weather"][0]["description"].capitalize()}\n'
                f'{round(dep_city_weather["main"]["temp_min"])}° / {round(dep_city_weather["main"]["temp_max"])}°')
        bot.send_message(call.message.chat.id, f"{text}", parse_mode='html')
