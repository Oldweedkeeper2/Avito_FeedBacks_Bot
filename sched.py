import asyncio
import datetime

from loguru import logger

from db.orders import ReviewsDB, OrdersDB
from utils import add_review, assign_a_userbot

reviews_db = ReviewsDB()
orders_db = OrdersDB()


async def starter():
    response = await reviews_db.check_time_to_work(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(response)
    tasks = []
    for user in response:
        if user['number'] is not None:
            print('прошёл', user)
            tasks.append(
                asyncio.create_task(add_review(order_id=user['order_id'], order_review_id=user['order_review_id'])))

        else:
            print('не прошёл', user)
            await assign_a_userbot(order_id=user['order_id'], order_review_id=user['order_review_id'])
            print('го 2')
            tasks.append(
                asyncio.create_task(add_review(order_id=user['order_id'], order_review_id=user['order_review_id'])))

    for task in tasks:
        await task




async def scheduler():
    while True:
        logger.info('Schedule..')
        await starter()
        await asyncio.sleep(6)


asyncio.run(scheduler())
print()
