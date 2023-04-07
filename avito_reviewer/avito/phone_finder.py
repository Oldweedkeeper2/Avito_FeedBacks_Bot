import asyncio

from loguru import logger

from .mouse import emulate_mouse_movement
from .writer import writer


async def phone_checker(page, data):
    # Нажимаем на кнопку "Показать телефон"
    # это может палить пользователя, но это доп дебаг. Сделать здесь проверку на кнопку "Показать телефон"
    # чтобы страница не скакала потом вверх и вниз
    try:
        await page.goto(data['site'])
        await page.reload()
        await emulate_mouse_movement(page, 5)

        await page.wait_for_selector('button[data-marker="item-phone-button/card"]')
        if await page.query_selector('button[data-marker="item-phone-button/card"]'):
            # logger.info(await page.query_selector_all('button[data-marker="item-phone-button/card"]'))

            try:
                await page.click('[data-marker="item-phone-button/card"]')
            except:
                await page.reload()
                await emulate_mouse_movement(page, 5)
                await page.click('[data-marker="item-phone-button/card"]')

            # Ожидание на странице (для лучшего эффекта сюда бы ещё эмулятор мышки запихнуть)
            await asyncio.sleep(4)

            if await page.query_selector('[data-marker="item-popup/popup"]'):
                popup_overlay = await page.query_selector('[data-marker="item-popup/popup"]')
            else:
                popup_overlay = await page.query_selector('[data-marker="phone-popup/popup"]')

            q = await popup_overlay.text_content()
            if q.lower().find('это временный номер') != -1:
                data['phone_status'] = 'Временный'
                return
            else:
                data['phone_status'] = 'Постоянный'
                return
        else:
            logger.error('Пользователь принимает только сообщения')
            await page.click('[data-marker="messenger-button/button"]')
            textarea = await page.query_selector('[data-marker="reply/input"]')
            for word in data['send_message'].split(' '):
                await writer(textarea, word)
        await emulate_mouse_movement(page, 3)


    except:
        error_text = 'Не удалось нажать на кнопку "Открыть телефон"'
        logger.error(error_text)
        data['errors'] = data['errors'].append(error_text)
