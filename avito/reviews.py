import asyncio

from loguru import logger

from .error_logger import error_log
from .mouse import emulate_mouse_movement
from .writer import writer


# site = 'https://www.avito.ru/moskva/sport_i_otdyh/begovye_lyzhi_atomic_redster_s9_carbon_2795133757'


async def message_confirmation(page, data):
    await page.goto('https://www.avito.ru/profile/messenger')
    await page.click('[data-marker="searchInput"]')
    text_area = await page.query_selector('input[type="search"]')

    try:
        for letter in data['item_text'].split(' '):
            await writer(text_area, letter)
            cell = await page.query_selector_all('[data-marker="channels/channel"]')

            if not cell:  # делаем ранний выход для читаемости кода
                # print('нет таблиц, продолжаю поиск')
                continue

            else:
                for cell_element in cell:  # Заходим в каждую табличку
                    # Ищем по тексту и цене
                    needed_text = await cell_element.query_selector('[data-marker="channels/item-title"]')
                    needed_price = await cell_element.query_selector('[data-marker="channels/item-price"]')

                    if not (needed_text and needed_price):
                        continue

                    else:
                        data['needed_text'] = await needed_text.inner_text()
                        data['needed_price'] = await needed_price.inner_text()
                        data['needed_price'] = data['needed_price'][:-2]  # убираем знак цены из цены

                        # Выбор чата
                        if data['needed_text'] == data['item_text'] and data['needed_price'] == data['item_price']:
                            await cell_element.click()
                            await asyncio.sleep(2)
                            # Нажатие кнопки
                            # Дописать проверку текста на кнопке
                            if not await page.query_selector('[data-marker="contextActions(0)/button"]'):
                                # logger.error('Consent button not found')
                                await error_log(data, 'Consent button not found')
                                return

                            await page.click('[data-marker="contextActions(0)/button"]')
                            # class="messages-history-scrollContent- для чека текста из чата (селектор всего чата)
                            # q = await page.query_selector('[class^="messages-history-scrollContent-"]')
                            # q = await q.context_text()

                            # Ожидаем появления элемента после клика
                            # Докинуть сюда обработку исключений, если будет выделываться
                            await page.wait_for_selector('selector_of_element_after_click', timeout=10000)

                            return
    except Exception as e:
        # logger.error(f'Review link not found {e}')
        # await error_log(data, f'Review link not found {e}')
        raise


async def review_preparation(context, page, data):
    try:
        await page.goto(data['site'])
    except Exception as e:
        # logger.error(f'{e}')
        await error_log(data, f'{e}')

    try:
        # Обязательно ждём всё, на что нажимаем, потому что это авито
        try:
            await page.wait_for_selector('[data-marker="rating-caption/rating"]')
        except Exception as e:
            print(e)
        # Проверяем наличие кнопки отзывы
        if await page.query_selector('[data-marker="rating-caption/rating"]'):
            # Переходим на отзывы по этому товару
            await page.goto(data['site'] + '#open-reviews-list')
            # Ждём открытия окна (сделай потом через ожидание селекторов)
            await asyncio.sleep(3)
            # Ждём открытие страницы
            try:
                async with context.expect_page(timeout=5000) as popup_info:
                    if await page.query_selector('button[data-marker="ratingSummary/addReviewButton"]'):
                        await page.click('button[data-marker="ratingSummary/addReviewButton"]')
                    else:
                        raise Exception
                popup = await popup_info.value
                await popup.wait_for_load_state(timeout=10000)
            except:
                # можно после этого проверять на оставленные отзывы
                # logger.error(f'Reviews button not found {e}')
                await error_log(data, f'Reviews button not found')

                return

            await asyncio.sleep(5)
            # Проверяем страницу на наличие блока на отзывы, на доп вериф
            # Вынести отдельной функцией
            root_element = await popup.query_selector('div[class^="styles-module-theme-CRreZ"]')
            root_element_text = await root_element.text_content()

            if root_element_text.lower().find('слишком много запросов') != -1:
                logger.error('Profile requires additional confirmation')
                data['acc_status'] = 'CLOSED'
                return

            # Возвращаем выпадашку. Окно, которое появляется при нажатии на кнопку 'Отзывы'
            # input('-review_preparation-end-')
            return popup
        else:
            # logger.error('Кнопка "Отзывы" не найдены')
            await error_log(data, 'Reviews button not found')
            return

    except Exception as e:
        # logger.error(f'Can\'t find button to leave feedback {e}')
        await error_log(data, rf'Can\'t find button to leave feedback {e}')


async def smart_search(page, data):
    try:
        if await page.query_selector('input[type="text"]'):
            # print(data['item_text'].split(' '))
            for word in data['item_text'].split(' '):
                # Вводим поиск название товара
                textarea = await page.query_selector('input[type="text"]')
                await writer(textarea, word)
                # Ждём ответа поиска
                await asyncio.sleep(4)
                # Проверяем наличие названия табличек
                await find_cell(page, data)

        else:
            # если нет строки поиска
            await find_cell(page, data)
    except:
        # logger.error('Can't find review link')
        # await error_log(data, "Can't find review link")
        raise


async def find_cell(page, data):
    try:
        cell = await page.query_selector_all('[class^="styles-item-"]')
        if cell:
            # Заходим в каждую табличку
            for cell_element in cell:

                # Ищем ссылку
                link = await cell_element.query_selector('img')
                link_src = await link.get_attribute('src')

                # Проверяем на схожесть
                if link_src.startswith(data['cut_photo_link']):
                    # print(f'нашёл {link_src} у {cell_element}')
                    await cell_element.click()
                    # По необходимости вынести отдельной функцией
                    # Ставим радиокнопку на "сделка состоялась"
                    await asyncio.sleep(4)
                    await page.click('label[data-marker="field/dealStage/1"]')
                    await asyncio.sleep(2)
                    # Нажимаем на кнопку "Продолжить"
                    await page.click('button[data-marker="field/customButton/"]')
                    await asyncio.sleep(2)
                    await page.evaluate('window.scrollTo(0,document.body.scrollHeight)')

                    # Жмём на запись комментария
                    # Ставим звёзды товару (цифра у star показывает количество звёзд)
                    stars = await page.query_selector('div[data-marker="field/score"]')
                    await stars.hover()
                    await asyncio.sleep(2)
                    await page.click('div[data-marker="field/score/star5"]')
                    await asyncio.sleep(2)

                    # stars = await page.query_selector('div[data-marker="field/score"]')
                    text_area = await page.query_selector('textarea[data-marker="field/comment/textarea"]')
                    await asyncio.sleep(4)
                    # Набираем текст комментария
                    # Если мы слишком долго ждём, то может слететь и куки и всё на свете (не уверен)
                    await writer(text_area, data['review_text'])
                    # await stars.click('div[data-marker="field/score/star5"]')
                    await asyncio.sleep(3)
                    input('stopping')
                    await page.click('button[data-marker="field/customButton/"]')

                    await asyncio.sleep(3)
                    # выдаёт вторую кнопку, если продавец отрицает сделку
                    if await page.query_selector('button[data-marker="field/customButton/"]'):
                        await page.click('[data-marker="field/score/star5"]')
                        await page.click('button[data-marker="field/customButton/"]')

                    # проверить на "Спасибо за отзыв"
                    input('stopping2')
                    thx_element = await page.query_selector('div[class^="styles-module-theme-CRreZ"]')
                    thx_element_text = await thx_element.text_content()

                    if thx_element_text.lower().find('спасибо за отзыв') != -1:
                        logger.info(thx_element_text.lower())

                    await asyncio.sleep(4)
                    await page.screenshot(path="screenshot.png")
                    logger.info('review sent')
                    await asyncio.sleep(3)

                    # Закрываем
                    break

                else:
                    pass
    except Exception:
        # logger.error('Error submitting feedback')
        raise


async def set_review(context, page, data):
    try:
        await message_confirmation(page, data)
    except Exception as e:
        await error_log(data, f'Review link not found, {e}')

    await emulate_mouse_movement(page, 3)
    try:
        page = await review_preparation(context, page, data)
        if page:
            await smart_search(page, data)
    except Exception as e:
        await error_log(data, f'Error submitting feedback, {e}')
        raise
