import json

from db.orders import ReviewsDB, OrdersDB

reviews_db = ReviewsDB()
orders_db = OrdersDB()


async def save_cookies(data, context, cookies_name):
    try:
        cookies = await context.cookies()
        state = await context.storage_state()
        if cookies_name == 'session':
            await reviews_db.add_cookies(number=data['number'], session_cookies=state)
        elif cookies_name == 'google':
            await reviews_db.add_cookies(number=data['number'], google_cookies=cookies)
        elif cookies_name == 'avito':
            await reviews_db.add_cookies(number=data['number'], avito_cookies=cookies)
    except:
        raise

async def load_cookies(data, context):
    try:
        cookies = await reviews_db.get_cookies(number=data['number'])
        with open(f"{data['number']}.json", 'w') as f:
            f.write(json.dumps(cookies.pop('session_cookies')))

        await context.storage_state(path=f"{data['number']}.json")
        for i in cookies:
            await context.add_cookies(cookies=cookies[i])
    except:
        raise

#
# async def save_session(context, filename: str) -> None:
#
#     state = await context.storage_state()
#     with open(filename, 'w') as f:
#         f.write(json.dumps(state))
