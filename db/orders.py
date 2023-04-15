import json
import math

import asyncpg as pg
from asyncpg import Connection

from avito.review_randomizer import get_review_dates


class DB:
    @staticmethod
    async def connection(user='postgres', password='123', host='localhost', port='5432',
                         database='avito_reviews_db') -> Connection:
        return await pg.connect(user=user, password=password, host=host, port=port, database=database)


class OrdersDB(DB):

    async def new_order(self, data):  # добавление нового заказа в orders
        conn = await self.connection()
        order_id = await conn.fetchval(
            "INSERT INTO orders(link, reviews_count, avito_profile_id, finish_date) VALUES($1, $2, $3, $4) RETURNING order_id",
            data['link'], data['reviews_count'], data['profile_id'], data['finish_date'])
        return order_id

    async def get_profile_id_from_order_id(self, order_id):  # профиль id сюда
        conn = await self.connection()
        try:
            id = await conn.fetchval("SELECT avito_profile_id FROM orders WHERE order_id = $1", order_id)
            return id
        finally:
            await conn.close()

    async def get_order_link(self, order_id):
        conn = await self.connection()
        try:
            link = await conn.fetchval("SELECT link FROM orders WHERE order_id = $1", order_id)
            return link
        finally:
            await conn.close()


    async def get_order(self, order_id):
        conn = await self.connection()
        try:
            query = "SELECT * FROM orders WHERE order_id = $1"
            order = await conn.fetch(query, order_id)
            return order[0]
        finally:
            await conn.close()


    async def get_current_orders_ids(self):
        conn = await self.connection()
        try:
            query = "SELECT order_id FROM orders WHERE current_count < reviews_count"
            orders_ids = await conn.fetch(query)
            return orders_ids
        finally:
            await conn.close()


class ReviewsDB(DB):

    async def get_users_without_account_id(self,
                                           account_id):  # выборка пользователей, которые не работали по-данному id человека.
        conn = await self.connection()

        try:
            query = "SELECT * FROM avito_users WHERE NOT EXISTS (SELECT * FROM userbots_accounts_busy " \
                    "WHERE number = avito_users.number AND account_id = $1)"
            numbers = await conn.fetch(query, account_id)
            return numbers
        finally:
            await conn.close()

    async def get_reviews(self, *_, order_id=None, status='all', number=None):  # получить отзывы
        """
        :param _:
        :param order_id: if number is None
        :param status: optional
        :param number: if order_id is None
        :return: * from reviews_texts
        """

        conn = await self.connection()

        try:
            query = "SELECT * FROM reviews_texts"
            if order_id is not None:
                if number is not None:
                    raise ValueError("Either order_id or number should be passed")
                query += f" WHERE order_id = {order_id}::text"
            elif number is not None:
                query += f" WHERE number = {number}::text"
            if status != 'all':
                query += f" AND status_id = (SELECT status_id FROM statuses WHERE name = '{status}')"
            return await conn.fetch(query)
        finally:
            await conn.close()

    async def get_review(self, *_, order_id, order_review_id):  # получить отзывы
        conn = await self.connection()

        try:
            query = "SELECT * FROM reviews_texts WHERE order_id = $1 AND order_review_id = $2"
            res = await conn.fetch(query, order_id, order_review_id)
        finally:
            await conn.close()

        return res

    async def update_review(self, order_id, order_review_id=None, phone=None, status=None):  # pylint: disable=T
        conn = await self.connection()

        try:
            if phone is not None:
                query = f"UPDATE reviews_texts SET number = '{phone}' WHERE order_id = {order_id}" \
                        f" AND order_review_id = {order_review_id}"
                await conn.execute(query)
                query = f"SELECT avito_profile_id FROM orders WHERE order_id = {order_id}"
                account_link = await conn.fetchval(query)
                query = f"INSERT INTO userbots_accounts_busy (number, account_id) VALUES ('{phone}', '{account_link}')"
                await conn.execute(query)
            elif status is not None:
                query = f"UPDATE reviews_texts SET status_id = (SELECT status_id FROM statuses WHERE name = '{status}')" \
                        f"WHERE order_id = {order_id} AND order_review_id = {order_review_id}"
                await conn.execute(query)
                query = f"SELECT status_id FROM reviews_texts WHERE order_id = {order_id}" \
                        f"AND order_review_id = {order_review_id}"
                status_id = await conn.fetchval(query)
                if status_id == 2:
                    query = f"UPDATE orders SET current_count = current_count + 1 WHERE order_id = {order_id}"
                    await conn.execute(query)
                    query = f"SELECT number FROM reviews_texts WHERE order_id = {order_id}" \
                            f"AND order_review_id = {order_review_id}"
                    number = await conn.fetchval(query)
                    query = f"UPDATE avito_users SET reviews_count = reviews_count + 1, last_review = NOW()" \
                            f"WHERE number = '{number}'"
                    await conn.execute(query)
        finally:
            await conn.close()

    async def add_reviews(self, data):  # добавить d reviews_text новые заказы (+1 к максимуму)
        conn = await self.connection()
        async with conn.transaction():
            order_review_id = await conn.fetchval('SELECT MAX(order_review_id) FROM reviews_texts WHERE order_id = $1',
                                                  data['order_id'])
            if order_review_id is None:
                order_review_id = 0

            date_res = get_review_dates(num_reviews=int(data['reviews_count']), num_days=int(data['amount_of_days']),
                                        max_per_day=math.ceil(int(data['reviews_count']) / int(data['amount_of_days'])))

            for text in data['texts']:
                order_review_id += 1
                await conn.execute(
                    'INSERT INTO reviews_texts (order_id, order_review_id, text, review_date) VALUES ($1, $2, $3, $4)',
                    data['order_id'], order_review_id, text, next(date_res))

    async def add_cookies(self, number, session_cookies=None, avito_cookies=None, google_cookies=None):  # добавить куки
        conn = await self.connection()
        try:
            if session_cookies is not None:
                session_cookies = json.dumps(session_cookies)
                await conn.execute(
                    "UPDATE avito_users SET session_cookies = $2 WHERE number=$1",
                    number, session_cookies
                )

            if avito_cookies is not None:
                avito_cookies = json.dumps(avito_cookies)
                await conn.execute(
                    "UPDATE avito_users SET avito_cookies = $2 WHERE number=$1",
                    number, avito_cookies
                )

            if google_cookies is not None:
                google_cookies = json.dumps(google_cookies)
                await conn.execute(
                    "UPDATE avito_users SET google_cookies = $2 WHERE number=$1",
                    number, google_cookies
                )
        finally:
            await conn.close()
            return

    async def get_cookies(self, number):  # получить куки
        conn = await self.connection()
        try:
            row = await conn.fetchrow(
                "SELECT session_cookies, avito_cookies, google_cookies FROM avito_users WHERE number=$1", number)
            if row:
                session_cookies, avito_cookies, google_cookies = row
                session_cookies = json.loads(session_cookies) if session_cookies is not None else None
                avito_cookies = json.loads(avito_cookies) if avito_cookies is not None else None
                google_cookies = json.loads(google_cookies) if google_cookies is not None else None
                return {'session_cookies': session_cookies, 'avito_cookies': avito_cookies,
                        'google_cookies': google_cookies}
            else:
                return None
        finally:
            await conn.close()

    async def update_status(self, number, status_id):
        conn = await self.connection()
        try:
            if status_id is not None:
                await conn.execute(
                    "UPDATE reviews_texts SET status_id = $2 WHERE number=$1",
                    number, status_id
                )
            else:
                return None
        finally:
            await conn.close()

    async def add_userbots_busy(self, number, account_id):
        conn = await self.connection()
        try:
            if number is not None:
                await conn.execute(
                    "INSERT INTO userbots_accounts_busy (number, account_id) VALUES ($1, $2)",
                    number, account_id
                )
            else:
                return None
        finally:
            await conn.close()

    # можно изменить следующие 4 функции на функцию update_userbots_profile, где ты будешь задавать то, что нужно изменить
    # и другие параметры (но мб не сильно удобно)

    async def check_problems_count(self, number):
        conn = await self.connection()
        try:
            if number is not None:
                await conn.execute(
                    "SELECT problems FROM avito_users WHERE number=$1",
                    number,
                )
        finally:
            await conn.close()

    async def update_reviews_count(self, number, count):
        conn = await self.connection()
        try:
            if number is not None and count is not None:
                await conn.execute(
                    "UPDATE avito_users SET reviews_count=reviews_count+$2 WHERE number=$1",
                    number, count
                )
        finally:
            await conn.close()

    async def update_problems_count(self, number, count):
        conn = await self.connection()
        try:
            if number is not None and count is not None:
                await conn.execute(
                    "UPDATE avito_users SET problems=$2 WHERE number=$1",
                    number, count
                )
        finally:
            await conn.close()

    async def update_last_review(self, number, timestamp):
        conn = await self.connection()
        try:
            if number is not None and timestamp is not None:
                await conn.execute(
                    "UPDATE avito_users SET last_review=$2 WHERE number=$1",
                    number, timestamp
                )
        finally:
            await conn.close()

    # 2 следующие функции про прокси
    async def update_proxy_for_account(self, number, proxy):

        conn = await self.connection()
        try:
            await conn.execute(
                "UPDATE avito_users SET proxy=$2 WHERE number=$1",
                number, json.dumps(proxy)
            )
        finally:
            await conn.close()

    async def get_proxy_for_account(self, number):

        conn = await self.connection()
        try:
            proxy = await conn.fetchval(
                "SELECT proxy FROM avito_users WHERE number=$1",
                number
            )
            if proxy is not None:
                return json.loads(proxy)
            else:
                return None
        finally:
            await conn.close()

    async def check_time_to_work(self, timestamp):

        conn = await self.connection()
        try:
            query = f"SELECT * FROM reviews_texts WHERE status_id=0 AND review_date<=CURRENT_TIMESTAMP"
            res = await conn.fetch(query)
        finally:
            await conn.close()

        return res
