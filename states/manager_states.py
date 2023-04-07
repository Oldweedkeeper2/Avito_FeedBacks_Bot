from aiogram.dispatcher.filters.state import State, StatesGroup


class AddReviews(StatesGroup):
    link = State()
    excel = State()
    count_on_day = State()
    confirmation = State()
