import asyncio
import json
import random
from datetime import datetime, timedelta

import pandas as pd
from loguru import logger

from avito_runner import start
from db.orders import ReviewsDB, OrdersDB

reviews_db = ReviewsDB()
orders_db = OrdersDB()


# правильное форматирование прокси при добавлении
#
def parse_proxy_string(proxy_str):
    parts = proxy_str.split(":")
    ip = parts[0]
    port = parts[1]
    proxy_username = parts[2]
    proxy_password = parts[3]
    return {
        "ip": ip,
        "port": port,
        "username": proxy_username,
        "password": proxy_password
    }


# правильное форматирование прокси при фетче из бд
#
def format_proxy(proxy_dict):
    ip = proxy_dict.get("ip")
    port = proxy_dict.get("port")
    proxy_username = proxy_dict.get("username")
    proxy_password = proxy_dict.get("password")
    return f"{ip}:{port}:{proxy_username}:{proxy_password}"


def create_review():
    pass


def get_date(n):
    today = datetime.today()
    result = today + timedelta(days=n)
    return (result, result.strftime('%d.%m.%Y'))


def get_column_data(file_path):
    data = pd.read_excel(file_path, header=None)
    return data[0].tolist()


async def add_new_reviews(data):
    order_id = await orders_db.new_order(data)
    data['order_id'] = order_id
    await reviews_db.add_reviews(data)


def is_avaliable_link(link):
    return True


async def assign_a_userbot(order_id, order_review_id):
    account_id = await orders_db.get_profile_id_from_order_id(order_id)  # получаем
    avito_users = await reviews_db.get_users_without_account_id(account_id)

    if not avito_users:
        logger.info(f"Found 0 userbots")
        return

    avito_user = random.choice(avito_users)
    logger.info(f"Order №{order_id} is assigned Userbot {avito_user}")
    await reviews_db.update_review(order_id=order_id, order_review_id=order_review_id, phone=avito_user['number'])


async def add_review(order_id, order_review_id):
    global avito_data
    await asyncio.sleep(2)
    print(order_id, order_review_id)

    account_id = await orders_db.get_profile_id_from_order_id(order_id)  # получаем
    avito_users = await reviews_db.get_users_without_account_id(account_id)
    if not avito_users:
        logger.info(f"Found 0 userbots")
        # return

    avito_user = random.choice(avito_users)
    reviews = await reviews_db.get_review(order_id=order_id, order_review_id=order_review_id)
    await reviews_db.update_review(order_id=order_id, order_review_id=order_review_id, phone=avito_user['number'])
    site = await orders_db.get_order_link(order_id=order_id)
    proxy = json.loads(avito_user['proxy'])

    # вынести в отдельный файл и ли в бд кинуть. Можно даже привязать один ua к пользователю, чтобы не менять каждый раз
    # этот код можно заменить fake_useragent просто с external датой
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.2; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
        'Mozilla/5.0 (Linux; U; Linux x86_64; ru-RU) Gecko/20130401 Firefox/72.8'
    ]
    user_agent = random.choice(user_agents)

    # запуск функции подготовки к отзыву
    try:
        avito_data = await start(avito_user['number'], avito_user['email'], avito_user['password'], site,
                                 reviews[0]['text'], proxy['ip'], proxy['port'],
                                 proxy['username'], proxy['password'],
                                 user_agent, only_parse=True)
        await asyncio.sleep(3)
    except Exception as e:
        logger.error(e)
        await reviews_db.update_status(number=avito_user['number'], status_id=3)
        return

    # регаем текущее время
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    date_time_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')

    await reviews_db.update_status(avito_user['number'], status_id=2)  # меняем статус работы в reviews_text на 2
    await reviews_db.update_last_review(avito_user['number'], timestamp=date_time_obj)  # меняем timestamp в бд
    await reviews_db.add_userbots_busy(avito_user['number'], account_id)  # добавляем номер акка в busy

# async def get_random_review_on_priority():
#     reviews =

# async def main():
#     tasks = [asyncio.create_task(add_review(2, 9)),
#              asyncio.create_task(add_review(3, 10))]
#     for task in tasks:
#         await task
#
#
# asyncio.run(main())
