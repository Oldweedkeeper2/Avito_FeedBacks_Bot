from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить отзывы', callback_data='add_feedbacks')],
    [InlineKeyboardButton(text='Отзывы в работе', callback_data='current_feedbacks')]
])


сonfirmation_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить', callback_data='сonfirm')],
    [InlineKeyboardButton(text='Отменить', callback_data='cancel')]
])