from telebot.handler_backends import State, StatesGroup


class HighPrice(StatesGroup):
    origin = State()
    destination = State()
    depart_date = State()
    return_date = State()
