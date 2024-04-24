from telebot.handler_backends import State, StatesGroup


class HighPriceOneWay(StatesGroup):
    origin = State()
    destination = State()
    depart_date = State()
    api_request = State()
