import asyncio
import random
from datetime import datetime, timedelta

import pandas as pd
from loguru import logger

from avito_reviewer.main import start, reviewer
from db.orders import ReviewsDB, OrdersDB

reviews_db = ReviewsDB()
orders_db = OrdersDB()


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


def get_profile_link_from_product_link(product_link):
    return 'https://8285995'


async def add_review(order_id, order_review_id):
    mail = "AndoimGavrilov671@gmail.com"
    password = "ad5jQClii5IC"
    site = 'https://www.avito.ru/moskva/detskaya_odezhda_i_obuv/romper_dlya_devochki_2894148448'
    review_text = 'У меня девочка 5 лет, ромпер подошёл!'

    ip = ''
    port = ''
    proxy_username = ''
    proxy_password = ''
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

    # account_link = await orders_db.get_profile_link_from_order_id(order_id)
    # users = await reviews_db.get_users_without_account_link(account_link)
    # user = random.choice(users)
    avito_data = await start(mail, password, site, review_text, ip, port, proxy_username, proxy_password, user_agent)

    if len(avito_data['errors']) < 4:
        delay_minutes = random.randint(25, 49)

        # Устанавливаем задержку перед запуском задачи
        await asyncio.sleep(delay_minutes * 60)

        avito_data = await reviewer(mail, password, site, review_text, ip, port, proxy_username, proxy_password,
                                    user_agent)
        logger.error(rf"Find {len(avito_data['errors'])} errors")


# async def get_random_review_on_priority():
#     reviews =

asyncio.run(add_review(1, 2))
