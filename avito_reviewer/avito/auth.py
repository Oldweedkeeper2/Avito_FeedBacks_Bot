import asyncio

import loguru
from playwright_stealth import stealth_async

from .cookeis_commander import save_cookies, load_cookies


# можно сохранять прямо в бд, вообще плевать
# добавлять ли тут эмуляторы мышки

async def google_login(context, page, mail, password):
    button_class = "VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 qIypjc TrZEUc lw1w4b"

    # Вводим email и нажимаем "Далее"
    await page.goto('https://accounts.google.com/')
    page_text = await page.content()

    # Проверьте, содержит ли текст фразу "Добро пожаловать"
    if page_text.find("Добро пожаловать") != -1:
        return
    elif page_text.find("устаревший или непопулярный браузер") != -1:
        raise Exception('outdated browser')

    # input('Остановка для регистрации руками это в auth.py')
    await page.fill('input[type="email"]', mail)
    await page.click(f'button[class="{button_class}"]')

    # Вводим пароль и нажимаем "Далее"
    await page.wait_for_selector('input[type="password"]')
    await page.fill('input[type="password"]', password)
    await page.click(f'button[class="{button_class}"]')

    await asyncio.sleep(3)  # Тут мы ждём подтверждения входа с телефона, если есть

    await save_cookies(context)  # Сохраняем куки (пока в файл)


async def avito_login(context, page):
    try:
        await stealth_async(page)
        await page.goto('https://www.avito.ru/#login?authsrc=h')
        await page.wait_for_url('https://www.avito.ru/#login?authsrc=h')
        button = await page.query_selector('button[data-marker="social-network-item(gp)"]')
        await button.click()
    except:
        loguru.logger.error('Error nen')
    # try:
    #     phone_code = input('введите код из смс это в auth.py')
    #     await page.fill('input[name="code"]', phone_code)
    #     await page.click('button[type="submit"]')
    #     await asyncio.sleep(3)  # Тут мы ждём код с телефона
    #
    # except:
    #     logger.error('Error when trying to authorize through the code')
    ''' 
    это кнопки выбора аккаунта, если нужно будет
            all_pages = context.pages
            popup_page = all_pages[-1]
            await popup_page.wait_for_selector(f'div[data-identifier="{mail}"]')
            await popup_page.click(f'div[data-identifier="{mail}"]')
    '''

    # Сохраняем куки (пока в файл)
    await save_cookies(context, 'cookies/avito_cookies_1.json')


async def first_login(context, page, mail, password):
    # Авторизация в гугле
    try:
        await google_login(context, page, mail, password)
    except Exception:
        pass
    # Авторизация в авито/ эта шляпа иногда может выдавать белый экран в открывашке, лечится релоадом и ожиданием всего
    try:
        await avito_login(context, page)
    except Exception as e:
        print(e)
        raise


async def login_with_cookies(context, page, mail, password):
    # пока достаём из файла, пишем имя файла, позже будем передавать mail и password

    # гугл срать хотел на то, что я ему куки заливаю
    await load_cookies(context, 'avito_reviewer/cookies/google_cookies_1.json')
    await load_cookies(context, 'avito_reviewer/cookies/avito_cookies_1.json')

# asyncio.run(first_login())
