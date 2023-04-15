from loguru import logger
from .mouse import emulate_mouse_movement


async def parse_page(page, data):
    # Получаем страницу и переходим на неё
    await page.goto(data['site'])
    logger.info('Зашёл')
    # Ждём какое-то время
    await emulate_mouse_movement(page, 3)

    # Получаем картинку и достаём ссылку на неё
    try:
        photo = await page.query_selector('[class^="image-frame-wrapper-"]')
        photo_link = await photo.query_selector('img')
        data['photo_link'] = await photo_link.get_attribute('src')
        # Находим индекс первого вхождения '/1/' в строке
        index = data['photo_link'].find('/1/') + 3
        # Обрезаем строку на 9 символа после '/1/'
        data['cut_photo_link'] = data['photo_link'][:index + 9]

        link = await page.query_selector('[data-marker="seller-link/link"]')
        account_id = await link.get_attribute('href')
        data['link_id'] = account_id.split('=')[-1]
        logger.debug(data)

    except:
        raise
    # Получаем текст товара и достаём ссылку на неё
    item_text = await page.query_selector('[data-marker="item-view/title-info"]')
    item_price = await page.query_selector('[itemprop="price"]')

    data['item_text'] = await item_text.inner_text()
    data['item_price'] = await item_price.inner_text()
