import asyncio

from loguru import logger
from playwright_stealth import stealth_async

from flask_manager import phone_manager
from .cookeis_commander import save_cookies


# можно сохранять прямо в бд, вообще плевать
# добавлять ли тут эмуляторы мышки

async def google_login(data, context, page):
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
    await page.fill('input[type="email"]', data['mail'])
    await page.click(f'button[class="{button_class}"]')

    # Вводим пароль и нажимаем "Далее"
    await page.wait_for_selector('input[type="password"]')
    await page.fill('input[type="password"]', data['password'])
    await page.click(f'button[class="{button_class}"]')

    await asyncio.sleep(3)  # Тут мы ждём подтверждения входа с телефона, если есть

    await save_cookies(data, context, 'google')  # Сохраняем куки (пока в файл)

async def avito_login(data, context, page):
    global phone_code
    try:
        await stealth_async(page)
        content = await page.content()
        with open('content', 'w') as f:
            f.write(content)
        await page.goto('https://www.avito.ru')
        await asyncio.sleep(2)
        try:
            await page.goto('https://www.avito.ru/#login?authsrc=h')
            await asyncio.sleep(6)
        except:
            await page.goto('https://www.avito.ru/#login?authsrc=h')
            await page.wait_for_url('https://www.avito.ru/#login?authsrc=h')
        
        await asyncio.sleep(5)
        button = await page.query_selector('button[data-marker="social-network-item(gp)"]')
        if button is not None:
            await button.click()
        else:
            logger.warning('social-network-item is None')
        logger.info('Authorization avito in process..')
    except Exception as e:
        logger.error(f'Error Avito load, {e}')
    #try:
        #await page.wait_for_selector('[class^="index-services-menu-avatar-image-"]')
        #if not await page.query_selector('[class^="index-services-menu-avatar-image-"]'):
    try:
        await asyncio.sleep(10)
        p = phone_manager.phone_data.keys()
        for i in p:
            logger.debug(i)
        #comport = phone_manager.phone_data[data['number']]
        #logger.debug(phone_manager.code_data)
        phone_code = phone_manager.phone_data[data['number']]
        #logger.info(comport, phone_code)
        await page.wait_for_selector('input[name="code"]')
        await asyncio.sleep(3)
        # phone_code = input('phone_code: ')
        await page.fill('input[name="code"]', phone_code)
        await page.click('button[type="submit"]')

    except Exception as e:
        logger.warning(f'When entering the code, {e}')
        #else:
        #    logger.info(f'Already authorized')
    # except Exception as e:
      #  logger.warning(e)
    ''' 
    это кнопки выбора аккаунта, если нужно будет
            all_pages = context.pages
            popup_page = all_pages[-1]
            await popup_page.wait_for_selector(f'div[data-identifier="{mail}"]')
            await popup_page.click(f'div[data-identifier="{mail}"]')
    '''

    # Сохраняем куки (пока в файл)
    await save_cookies(data, context, 'avito')


async def first_login(data, context, page):
    # Авторизация в гугле
    try:
        await google_login(data, context, page)
    except Exception:
        raise
    logger.info('Google authorization completed')

    # Авторизация в авито/ эта шляпа иногда может выдавать белый экран в открывашке, лечится релоадом и ожиданием всего
    try:
        await avito_login(data, context, page)
    except Exception:
        return
    logger.info('Avito authorization completed')
