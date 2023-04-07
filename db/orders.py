import asyncpg as pg
from asyncpg import Connection


class DB:
    @staticmethod
    async def connection(user='postgres', password='backwater', host='localhost', port='5432',
                         database='avito_reviews_db') -> Connection:
        return await pg.connect(user=user, password=password, host=host, port=port, database=database)


class OrdersDB(DB):

    async def new_order(self, data):
        conn = await self.connection()
        order_id = await conn.fetchval(
            "INSERT INTO orders(link, reviews_count, avito_profile_link, finish_date) VALUES($1, $2, $3, $4) RETURNING order_id",
            data['link'], data['reviews_count'], data['profile_link'], data['finish_date'])
        return order_id

    async def get_profile_link_from_order_id(self, order_id):
        conn = await self.connection()
        try:
            link = await conn.fetchval("SELECT avito_profile_link FROM orders WHERE order_id = $1", order_id)
            return link
        finally:
            await conn.close()


class ReviewsDB(DB):

    async def get_reviews(self, *_, order_id=None, status='all', user_phone=None):  # получить отзывы
        conn = await self.connection()

        try:
            query = "SELECT * FROM reviews_texts"
            if order_id is not None:
                if user_phone is not None:
                    raise ValueError("Either order_id or user_phone should be passed")
                query += f" WHERE order_id = {order_id}"
            elif user_phone is not None:
                query += f" WHERE user_phone = {user_phone}"
            if status != 'all':
                query += f" AND status_id = (SELECT status_id FROM statuses WHERE name = '{status}')"
            return await conn.fetch(query)
        finally:
            await conn.close()

    async def update_review(self, order_id, order_review_id=None, phone=None, status=None):
        conn = await self.connection()

        try:
            if phone is not None:
                query = f"UPDATE reviews_texts SET user_phone = '{phone}' WHERE order_id = {order_id}" \
                        f" AND order_review_id = {order_review_id}"
                await conn.execute(query)
                query = f"SELECT avito_profile_link FROM orders WHERE order_id = {order_id}"
                account_link = await conn.fetchval(query)
                query = f"INSERT INTO userbots_accounts_busy (number, account_link) VALUES ('{phone}', '{account_link}')"
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

    async def add_reviews(self, data):  #
        conn = await self.connection()
        async with conn.transaction():
            order_review_id = await conn.fetchval('SELECT MAX(order_review_id) FROM reviews_texts WHERE order_id = $1',
                                                  data['order_id'])
            if order_review_id is None:
                order_review_id = 0

            for text in data['texts']:
                order_review_id += 1
                await conn.execute('INSERT INTO reviews_texts (order_id, order_review_id, text) VALUES ($1, $2, $3)',
                                   data['order_id'], order_review_id, text)

    async def get_users_without_account_link(self, link):
        conn = await self.connection()

        try:
            query = "SELECT * FROM avito_users WHERE NOT EXISTS (SELECT * FROM userbots_accounts_busy " \
                    "WHERE number = avito_users.number AND account_link = $1)"
            numbers = await conn.fetch(query, link)
            return numbers
        finally:
            await conn.close()



    async def add_cookies(self, number, session_cookies=None, avito_cookies=None, google_cookies=None):
        conn = await self.connection()
        try:
            if session_cookies is not None:
                await conn.execute(
                    "INSERT INTO cookies(number, session_cookies) VALUES ($1, $2) ON CONFLICT (number) DO UPDATE SET session_cookies = $2",
                    number, session_cookies
                )
            if avito_cookies is not None:
                await conn.execute(
                    "INSERT INTO cookies(number, avito_cookies) VALUES ($1, $2) ON CONFLICT (number) DO UPDATE SET avito_cookies = $2",
                    number, avito_cookies
                )
            if google_cookies is not None:
                await conn.execute(
                    "INSERT INTO cookies(number, google_cookies) VALUES ($1, $2) ON CONFLICT (number) DO UPDATE SET google_cookies = $2",
                    number, google_cookies
                )
        finally:
            await conn.close()