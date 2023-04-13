from aiogram.dispatcher.filters.state import State, StatesGroup


class AddReviews(StatesGroup):
    profile_id = State()
    link = State()
    excel = State()
    count_on_day = State()
    confirmation = State()
