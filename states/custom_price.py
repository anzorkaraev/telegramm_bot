from telebot.handler_backends import State, StatesGroup


class CustomPrice(StatesGroup):
    origin = State()
    destination = State()
    price_range = State()
    depart_date = State()
    return_date = State()
