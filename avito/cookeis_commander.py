import json

from db.orders import ReviewsDB, OrdersDB

reviews_db = ReviewsDB()
orders_db = OrdersDB()


# пока что это всё работает через файлы, но надеюсь потом прикручу бд
async def save_cookies(data, context, cookies_name):
    cookies = await context.cookies()
    if cookies_name == 'session':
        await reviews_db.add_cookies(number=data['number'], session_cookies=cookies)
    elif cookies_name == 'google':
        await reviews_db.add_cookies(number=data['number'], google_cookies=cookies)
    elif cookies_name == 'avito':
        await reviews_db.add_cookies(number=data['number'], avito_cookies=cookies)

    # cookies = await context.cookies()
    # with open(filename, 'w') as f:
    #     f.write(json.dumps(cookies))


# можно загружать прямо из бд, вообще плевать
async def load_cookies(data, context):
    try:
        cookies = await reviews_db.get_cookies(number=data['number'])
        with open(f"{data['number']}.json", 'w') as f:
            f.write(json.dumps(cookies.pop('session_cookies')))

        await context.storage_state(path=f"{data['number']}.json")
        for i in cookies:
            print(i)
            print(cookies[i])
            await context.add_cookies(cookies=cookies[i])

    except:
        raise
        # with open(filename, 'r') as f:
    #     cookies = json.loads(f.read())
    #     await context.add_cookies(cookies)


# сохраняем все данные о сессии в общем виде
async def save_session(context, filename: str) -> None:
    state = await context.storage_state()
    with open(filename, 'w') as f:
        f.write(json.dumps(state))


# загружаем
# эта хуета принимает только путь к файлу, а дальше сама всё делает
async def load_session(context, filename: str) -> None:
    # with open(filename, 'r') as f:
    #     state = json.loads(f.read())
    #     print(state)
    await context.storage_state(path=filename)

# асинхронная загрузка куки из файлов, которая нахрен никому не нужна
# import aiofiles
# async with aiofiles.open('cookies/google_cookies.json', 'r') as f:
#     google_cookies = await f.read()
#     await page.goto('https://accounts.google.com/')
#     await page.context.add_cookies(json.loads(google_cookies))
# async with aiofiles.open('cookies/avito_cookies.json', 'r') as f:
#     avito_cookies = await f.read()
#     await page.goto('https://www.avito.ru/')
#     await page.context.add_cookies(json.loads(avito_cookies))
