from telebot.handler_backends import State, StatesGroup


class LowPriceTwoWay(StatesGroup):
    origin = State()
    destination = State()
    depart_date = State()
    return_date = State()
    api_request = State()
