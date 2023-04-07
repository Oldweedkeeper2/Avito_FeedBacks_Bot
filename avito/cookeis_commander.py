import json


# пока что это всё работает через файлы, но надеюсь потом прикручу бд
async def save_cookies(context, filename: str):
    # await add_cookies
    cookies = await context.cookies()
    with open(filename, 'w') as f:
        f.write(json.dumps(cookies))


# можно загружать прямо из бд, вообще плевать
async def load_cookies(context, filename: str):
    with open(filename, 'r') as f:
        cookies = json.loads(f.read())
    await context.add_cookies(cookies)


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
