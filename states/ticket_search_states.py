from telebot.handler_backends import State, StatesGroup


class TicketsSearchState(StatesGroup):
    origin = State()
    destination = State()
    depart_date = State()
    return_date = State()
    api_request = State()
