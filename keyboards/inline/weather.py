from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

from loader import bot
from site_APi.request_to_api import get_weather
from utils.bot_logger import BotLogger

logger = BotLogger('logs.log')


def weather(city):
    logger.log_info(city)
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton('Хочу 👍', callback_data=city)
    btn2 = InlineKeyboardButton('Не хочу ❌', callback_data='close')
    keyboard.add(btn1, btn2)
    return keyboard


@bot.callback_query_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    logger.log_info(f'weather {call.data}')
    if call.data == 'close':
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        dep_city_weather = get_weather(call.data)
        if dep_city_weather['cod'] != 200:
            bot.send_message(call.message.chat.id, '🫢 Что-то пошло не так!\n'
                                                   'Возможно была допущена опечатка в названии города\n'
                                                   'Проверьте данные и попробуйте ещё раз')
        text = (f'{round(dep_city_weather["main"]["temp"])}°\n'
                f'{dep_city_weather["weather"][0]["description"].capitalize()}\n'
                f'{round(dep_city_weather["main"]["temp_min"])}° / {round(dep_city_weather["main"]["temp_max"])}°')
        bot.edit_message_text(f"{text}", call.message.chat.id, call.message.message_id)