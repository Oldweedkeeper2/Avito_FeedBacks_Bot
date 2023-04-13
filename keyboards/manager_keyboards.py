from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from db.orders import OrdersDB

ordersDB = OrdersDB()

start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить отзывы', callback_data='add_feedbacks')],
    [InlineKeyboardButton(text='Отзывы в работе', callback_data='current_feedbacks')]
])


сonfirmation_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить', callback_data='сonfirm')],
    [InlineKeyboardButton(text='Отменить', callback_data='cancel')]
])

async def current_orders_kb():
    orders_ids = await ordersDB.get_current_orders_ids()
    markup = InlineKeyboardMarkup(row_width=2)
    for order_id in orders_ids:
        id = order_id['order_id']
        markup.add(InlineKeyboardButton(text=str(id), callback_data=f'current_order_{id}'))
    return markup


back_to_current_orders_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data='current_feedbacks')]])
