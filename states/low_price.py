from telebot.handler_backends import State, StatesGroup


class LowPrice(StatesGroup):
    origin = State()
    destination = State()
    depart_date = State()
    return_date = State()
