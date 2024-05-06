from telebot.handler_backends import State, StatesGroup


class AllTickets(StatesGroup):
    origin = State()
    destination = State()
    depart_date = State()
    return_date = State()
