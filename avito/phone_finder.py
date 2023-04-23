import asyncio

from loguru import logger

from .error_logger import error_log
from .mouse import emulate_mouse_movement
from .writer import writer


async def phone_checker(page, data):
    # Нажимаем на кнопку "Показать телефон"
    # это может палить пользователя, но это доп дебаг. Сделать здесь проверку на кнопку "Показать телефон"
    # чтобы страница не скакала потом вверх и вниз
    try:
        await page.goto(data['site'])
        # await page.wait_for_url(data['site'])
        await emulate_mouse_movement(page, 5)

        await page.wait_for_selector('button[data-marker="item-phone-button/card"]', timeout=10000)
        # я переделал под кнопку показать телефон сверху, хз как будет работать, но вроде не багует

        if await page.query_selector('button[data-marker="item-phone-button/card"]'):
            # logger.info(await page.query_selector_all('button[data-marker="item-phone-button/card"]'))
            try:

                await page.click('[data-marker="item-phone-button/header"]')
            except:
                # await page.reload()
                # await page.wait_for_url(data['site'])
                await page.click('[data-marker="item-phone-button/card"]')
            # Ожидание на странице (для лучшего эффекта сюда бы ещё эмулятор мышки запихнуть)
            await page.wait_for_timeout(6)
            
            cont = await page.content()
            with open('cont4.html','w') as f:
                f.write(cont)

            try:
                await page.wait_for_selector('[data-marker="item-popup/overlay"]')
                w = await page.query_selector('[data-marker="item-popup/overlay"]')
                
                # if await page.query_selector('[data-marker="item-popup/popup"]'):
                    # popup_overlay = await page.query_selector('[data-marker="item-popup/popup"]')
                # else:
                    # popup_overlay = await page.query_selector('[data-marker="phone-popup/popup"]')
                
                q = w.text_content()
                print(q)

                if q.lower().find('это временный номер') != -1:
                    data['phone_status'] = 'Temporary'
                    logger.debug(data)
                    return
                else:
                    data['phone_status'] = 'Permanent'
                    logger.debug(data)
                    return
            except Exception as e:
                logger.warning(e)

        else:
            logger.warning('The user only accepts messages')
            await page.wait_for_selector('[data-marker="messenger-button/button"]')
            await page.click('[data-marker="messenger-button/button"]')
            textarea = await page.query_selector('[data-marker="reply/input"]')
            for word in data['send_message'].split(' '):
                await writer(textarea, word)
        await page.wait_for_timeout(3)
        return


    except Exception as e:
        cont = await page.content()
        with open('cont.html','w') as f:
            f.write(cont)

        await error_log(data, f'Failed to click on the "Open Phone" button, {e}')
        return
