from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def reserve(link: str) -> InlineKeyboardMarkup:
    url = f'https://www.aviasales.com{link}'
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Забронировать', url=url))
    return markup

