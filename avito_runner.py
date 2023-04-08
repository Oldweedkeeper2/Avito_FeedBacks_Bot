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
from avito.phone_finder import phone_checker
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
    except:
        await error_log(data, 'Error browser launched')

    try:
        session_ip = await check_ip_address(ip)
        if ip == session_ip['ip']:
            logger.info('Proxy launched successfully')
        else:
            raise
    except:
        await error_log(data, 'Proxy checking error')

    try:
        await load_cookies(data, context)
        logger.info('Session data loaded (session, google, avito)')
    except Exception as e:
        print(e, '1')
        await error_log(data, 'Error setting session state')

    try:
        await login_with_cookies(data, context)  # логин по куки
    except Exception as e:
        print(e, '2')
        await error_log(data, 'Error with login_with_cookies')

    try:
        await first_login(data, context, page)  # логин по гуглу
    except Exception as e:
        print(e, '3')
        await error_log(data, 'Error with first_login')

    # input('Press Enter to continue')
    await asyncio.sleep(4)
    try:
        await parse_page(page, data)  # парсим страницу

    except Exception as e:
        print(e, '4')
        await error_log(data, 'Error page parsing')

    try:
        await emulate_mouse_movement(page, duration=4)  # эмулируем человеческую мышь
    except Exception as e:
        print(e, '5')
        await error_log(data, 'Error emulate_mouse_movement')

    # try:
    #     await check_contact_snippet(page, data)  # проверяем ждущие отзывы (вынести в отдельную функцию
    #
    # except Exception as e:
    #     print(e, '6')
    #     await error_log(data, 'Error check_contact_snippet')

    return browser, context, page, data


async def start(number, mail: str, password: str, site: str, review_text: str, ip: str, port: str, proxy_username: str,
                proxy_password: str, user_agent: str):
    async with async_playwright() as p:
        browser, context, page, data = await main(number, mail, password, site, review_text, ip, port,
                                                  proxy_username,
                                                  proxy_password, p,
                                                  user_agent)
        try:
            await check_contact_snippet(page, data)  # проверяем ждущие отзывы (вынести в отдельную функцию

        except Exception as e:
            print(e, '6')
            await error_log(data, 'Error check_contact_snippet')

        await phone_checker(page, data)  # подготовка к отзыву, смотрим телефон

        # закинуть это в отдельную функцию, мб даже просто в main
        if len(data['errors']) > 5:
            logger.error("Too many errors")
            await reviews_db.update_status(number=data['number'], status_id=2)
            return
    try:
        await save_cookies(data=data, context=context,
                           cookies_name='session')  # загружаем сессию в бд, в формате json
    except Exception as e:
        await error_log(data, f'Error saving data {e}')
    print(data)
    return data


async def reviewer(number, mail: str, password: str, site: str, review_text: str, ip: str, port: str,
                   proxy_username: str,
                   proxy_password: str, user_agent: str):
    async with async_playwright() as p:
        browser, context, page, data = await main(number, mail, password, site, review_text, ip, port, proxy_username,
                                                  proxy_password, p,
                                                  user_agent)

        # try:
        #     await check_contact_snippet(page, data)  # проверяем ждущие отзывы (вынести в отдельную функцию
        #     input('qq')
        # except Exception as e:
        #     print(e, '6')
        #     await error_log(data, 'Error check_contact_snippet')

        await set_review(context, page, data)  # оставляем отзыв

        if len(data['errors']) > 5:
            logger.error("Too many errors")
            await reviews_db.update_status(number=data['number'], status_id=2)
            return
    try:
        await save_cookies(data=data, context=context,
                           cookies_name='session')  # загружаем сессию в бд, в формате json
    except Exception as e:
        await error_log(data, f'Error saving data {e}')
    print(data)
    return data


async def parse_profile_link(number, mail: str, password: str, site: str, review_text: str, ip: str, port: str,
                             proxy_username: str,
                             proxy_password: str, user_agent: str):
    async with async_playwright() as p:
        browser, context, page, data = await main(number, mail, password, site, review_text, ip, port, proxy_username,
                                                  proxy_password, p,
                                                  user_agent)

        if len(data['errors']) > 5:
            logger.error("Too many errors")
            await reviews_db.update_status(number=data['number'], status_id=2)
            return
    try:
        await save_cookies(data=data, context=context,
                           cookies_name='session')  # загружаем сессию в бд, в формате json
    except Exception as e:
        await error_log(data, f'Error saving data {e}')
    print(data)
    return data

# if __name__ == '__main__':
#     mail = "AndoimGavrilov671@gmail.com"
#     password = "ad5jQClii5IC"
#     site = 'https://www.avito.ru/moskva/detskaya_odezhda_i_obuv/romper_dlya_devochki_2894148448'
#     review_text = 'У меня девочка 5 лет, ромпер подошёл!'
#
#     ip = ''
#     port = ''
#     proxy_username = ''
#     proxy_password = ''
#
#     user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'
#     # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
#
#     asyncio.run(start(mail, password, site, review_text, ip, port, proxy_username, proxy_password, user_agent))
#
#     # asyncio.run(reviewer(mail, password, site, review_text, ip, port, proxy_username, proxy_password, user_agent))
