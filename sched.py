import asyncio
import datetime

from loguru import logger

from db.orders import ReviewsDB, OrdersDB
from utils import add_review, assign_a_userbot
from flask_manager import phone_manager

reviews_db = ReviewsDB()
orders_db = OrdersDB()


async def starter():
    response = await reviews_db.check_time_to_work(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    tasks = []
    for user in response:
        if user['number'] is not None:
            # print('Номер есть', user['number'])
            tasks.append(
                asyncio.create_task(add_review(order_id=user['order_id'], order_review_id=user['order_review_id'])))

        else:
            # print('Номера нет', user['number'])
            await assign_a_userbot(order_id=user['order_id'], order_review_id=user['order_review_id'])
            tasks.append(
                asyncio.create_task(add_review(order_id=user['order_id'], order_review_id=user['order_review_id'])))

    for task in tasks:
        try:
            await task
        except Exception as e:
            logger.error(e)

async def sched():
    while True:
        logger.success('Schedule..')
        logger.debug(phone_manager.phone_data)
        logger.debug(phone_manager.code_data)
        asyncio.create_task(starter())
        await asyncio.sleep(6)


