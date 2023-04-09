import asyncio
import random

from loguru import logger
from playwright.async_api import Playwright
from playwright.async_api import async_playwright

from avito.auth import first_login, login_with_cookies
from avito.cookeis_commander import save_cookies, load_cookies
from avito.error_logger import error_log
from avito.mouse import emulate_mouse_movement
from avito.parse import parse_page
from avito.profile_commander import check_contact_snippet
from avito.proxy import check_ip_address, create_proxy_settings
from avito.reviews import set_review
from db.orders import ReviewsDB

reviews_db = ReviewsDB()

def get_random_viewport_size():
    sizes = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        {'width': 1440, 'height': 900},
        {'width': 1280, 'height': 720}
    ]
    return random.choice(sizes)


async def main(number: str, mail: str, password: str, site: str, review_text: str, ip: str, port: str,
               proxy_username: str,
               proxy_password: str, p: Playwright, user_agent: str):
    if not ip or not port:
        raise Exception("Invalid proxy ip or port")

    await create_proxy_settings(ip, port, proxy_username, proxy_password)
    size = get_random_viewport_size()
    browser_type = p.firefox
    browser = await browser_type.launch(headless=False, timeout=50000)
    context = await browser.new_context(user_agent=user_agent, viewport=size)
    page = await context.new_page()
    width, height = await page.evaluate("() => [window.innerWidth, window.innerHeight]")
    data = dict(number=number,
                mail=mail,
                password=password,
                site=site,
                review_text=review_text,
                ip=ip,
                port=port,
                proxy_username=proxy_username,
                proxy_password=proxy_password,
                acc_status='OPEN',
                screen={'width': width, 'height': height},
                errors=[])
    await reviews_db.update_status(number=data['number'], status_id=1)

    try:
        if browser.is_connected():
            logger.info('Browser launched')
        else:
            raise
    except Exception as e:
        await error_log(data, f'Error browser launched, {e}')

    try:
        session_ip = await check_ip_address(ip)
        if ip == session_ip['ip']:
            logger.info('Proxy launched successfully')
        else:
            raise
    except Exception as e:
        await error_log(data, f'Proxy checking error, {e}')

    try:
        await load_cookies(data, context)
        logger.info('Session data loaded (session, google, avito)')
    except Exception as e:
        await error_log(data, 'fError setting session state, {e}')

    try:
        await login_with_cookies(data, context)  # логин по куки
    except Exception as e:
        await error_log(data, f'Error with login_with_cookies, {e}')

    try:
        await first_login(data, context, page)  # логин по гуглу
    except Exception as e:
        await error_log(data, f'Error with first_login, {e}')

    # input('Press Enter to continue')
    await asyncio.sleep(4)
    try:
        await parse_page(page, data)  # парсим страницу

    except Exception as e:
        await error_log(data, f'Error page parsing, {e}')

    try:
        await emulate_mouse_movement(page, duration=4)  # эмулируем человеческую мышь
    except Exception as e:
        await error_log(data, f'Error emulate_mouse_movement, {e}')

    try:
        await check_contact_snippet(page, data)  # проверяем ждущие отзывы (вынести в отдельную функцию

    except Exception as e:
        await error_log(data, f'Error check_contact_snippet, {e}')

    return browser, context, page, data


async def start(number, mail: str, password: str, site: str, review_text: str, ip: str, port: str, proxy_username: str,
                proxy_password: str, user_agent: str, only_parse=False):
    async with async_playwright() as p:
        browser, context, page, data = await main(number, mail, password, site, review_text, ip, port,
                                                  proxy_username,
                                                  proxy_password, p,
                                                  user_agent)  # ошибки обрабатываются внутри
        if not only_parse:
            # await phone_checker(page, data)  # подготовка к отзыву, смотрим телефон
            try:
                if not only_parse:  # код для проверки обработки ошибок
                    raise
                delay_minutes = random.randint(5, 5)  # вот здесь изменять время задержки
                # Устанавливаем задержку перед запуском задачи
                await asyncio.sleep(delay_minutes * 60)
                await set_review(context, page, data)  # оставляем отзыв ошибки обрабатываются внутри
            except Exception as e:
                logger.error(e)
                await reviews_db.update_status(number=data['number'], status_id=3)

        # закинуть это в отдельную функцию, мб даже просто в main
        print(123123)
        if len(data['errors']) > 5:
            logger.error("Too many errors")
            await reviews_db.update_status(number=data['number'], status_id=3)
            raise
        try:
            await save_cookies(data=data, context=context,
                               cookies_name='session')  # загружаем сессию в бд, в формате json
        except Exception as e:
            await error_log(data, f'Error saving data, {e}')
    return data

#
# async def reviewer(number, mail: str, password: str, site: str, review_text: str, ip: str, port: str,
#                    proxy_username: str,
#                    proxy_password: str, user_agent: str):
#     async with async_playwright() as p:
#         browser, context, page, data = await main(number, mail, password, site, review_text, ip, port, proxy_username,
#                                                   proxy_password, p,
#                                                   user_agent)
#
#         await set_review(context, page, data)  # оставляем отзыв
#
#         if len(data['errors']) > 5:
#             logger.error("Too many errors")
#             await reviews_db.update_status(number=data['number'], status_id=2)
#             return
#         try:
#             await save_cookies(data=data, context=context,
#                                cookies_name='session')  # загружаем сессию в бд, в формате json
#         except Exception as e:
#             await error_log(data, f'Error saving data {e}')
#     print(data)
#     return data
