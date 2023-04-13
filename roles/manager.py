import os
from asyncio import sleep
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from orders.start import start_reviews
from states.manager_states import *
from keyboards.manager_keyboards import *
from utils.add_reviews_funcs import *
from loader import bot

async def start_command_handler(msg: Message, state: FSMContext):
    await msg.delete()
    await state.finish()
    await msg.answer('Привет. Ты менеджер. Выбери действие.', reply_markup=start_kb)


async def avito_profile_id(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Отправьте id пользователя avito.', reply_markup=None)
    await AddReviews.profile_id.set()
    await state.update_data({'worked_msg_id':call.message.message_id})



async def add_reviews_handler(msg: Message, state: FSMContext):
    data = await state.get_data()
    data['profile_id'] = msg.text
    await state.update_data(data)
    await msg.edit_text('Отправьте ссылку на товар или услугу.', reply_markup=None)
    await AddReviews.link.set()


async def link_handler(msg: Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    link = msg.text
    if is_avaliable_link(link):
        await bot.edit_message_text(text='Теперь отправь мне excel таблицу с текстами отзывов.',
                                    chat_id=msg.from_id,
                                    message_id=data['worked_msg_id'])
        data['link'] = link
        await state.update_data(data)
        await AddReviews.next()
    else:
        await bot.edit_message_text(text='Ссылка не рабочая. Проверьте её и если она рабочая, то отравьте ещё раз',
                                    chat_id=msg.from_id,
                                    message_id=data['worked_msg_id'])


async def excel_handler(msg: Message, state: FSMContext):
    data = await state.get_data()
    if msg.content_type != 'document':
        try:
            await bot.edit_message_text(text='Отправь мне excel таблицу с текстами отзывов в первом столбце',
                                        chat_id=msg.from_id, message_id=data['worked_msg_id'])
        except:
            pass
    else:
        file = await msg.document.download(destination_file=msg.document.file_name)
        try:
            texts = get_column_data(file.name)
            os.remove(file.name)
            if len(texts) > 0:
                await bot.edit_message_text(text='Теперь укажи количество дней за которое нужно отправить все отзывы.',
                                            chat_id=msg.from_id,
                                            message_id=data['worked_msg_id'])
                data['texts'] = texts
                await state.update_data(data)
                await AddReviews.next()
            else:
                await bot.edit_message_text(text='Я не нашёл тексты для отзывов. Пожалуйста, проверьте, что первый '
                                                    'столбец таблицы заполнен с первой строки и содержит хотя бы один '
                                                    'текст.',
                                            chat_id=msg.from_id,
                                            message_id=data['worked_msg_id'])
        except:
            await bot.edit_message_text(text='Мне не удалось прочитать таблицу. Проверьте, что она открывается и '
                                                'пришлите ту, которую можно прочесть.',
                                        chat_id=msg.from_id,
                                        message_id=data['worked_msg_id'])
    await msg.delete()


async def amount_of_days_handler(msg: Message, state: FSMContext):
    days = msg.text
    await msg.delete()
    data = await state.get_data()
    if not msg.text.isdigit() or int(msg.text) <= 0:
        try:
            await bot.edit_message_text(text='Пожалуйста, отправьте мне число дней, за которое должны быть'
                                             'отправлены все отзывы',
                                        chat_id=msg.from_id,
                                        message_id=data['worked_msg_id'])
        except:
            pass
    else:
        data['amount_of_days'] = days
        await state.update_data()
        await AddReviews.next()
        reviews_count = len(data["texts"])
        data['reviews_count'] = reviews_count
        finish_date = get_date(int(days))
        data['finish_date'] = finish_date[0]
        await state.update_data(data)
        await bot.edit_message_text(text=f'Количество отзывов - {reviews_count}\n'
                                            f'Количество дней - {days}\n'
                                            f'Дата окончания - {finish_date[1]}',
                                    chat_id=msg.from_id,
                                    message_id=data['worked_msg_id'],
                                    reply_markup=сonfirmation_kb)


async def confirmation_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == 'сonfirm':
        await add_new_reviews(data)
        await bot.edit_message_text(text='Отзывы были добавлены в обработку. Вы можете увидеть статус этих отзывов'
                                            'в текущих отзывах',
                                    chat_id=call.from_user.id,
                                    message_id=data['worked_msg_id'])
    else:
        await bot.edit_message_text(text='Хорошо, я отменил добавление этих отзывов.',
                                    chat_id=call.from_user.id,
                                    message_id=data['worked_msg_id'])
    await state.finish()
    await sleep(2)
    await call.message.answer('Привет. Ты менеджер. Выбери действие.', reply_markup=start_kb)

async def current_feedback_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Выбери id заказа.', reply_markup=await current_orders_kb())


async def order_statistic(call: CallbackQuery, state: FSMContext):
    order = await orders_db.get_order(int(call.data.split('_')[-1]))
    text = f'Заказ №{order["order_id"]}\n' \
           f'Отзывы - {order["current_count"]}/{order["reviews_count"]}' \
           f'Дата окончания - {order["finish_date"]}'
    await call.message.edit_text(text, reply_markup=back_to_current_orders_kb)