from loguru import logger

from .mouse import emulate_mouse_movement


async def see_more_snippet(page, selector: str):
    async def get_table(page):
        visible_elements = await page.query_selector_all(selector)
        visible_elements = visible_elements[-1]
        return visible_elements, await visible_elements.text_content()

    prev_element, prev_text = await get_table(page)
    # print(prev_element, prev_text)
    while True:
        await prev_element.scroll_into_view_if_needed()
        cur_element, cur_text = await get_table(page)
        await emulate_mouse_movement(page=page, duration=2)
        if cur_text == prev_text:
            break
        prev_text = cur_text
        prev_element = cur_element


# можно сделать переход на отзывы через нажатие на звёздочку, но через поиск более человечно.
async def check_contact_snippet(page, data):
    # проверка товаров "Ждут оценки"
    data_awaited = {}
    data_posted = {}
    await page.goto('https://www.avito.ru/profile/contacts?page_from=profile_menu')
    try:
        await see_more_snippet(page, 'div[class^="ProfileContactSnippet-root-"]')
    except Exception as e:
        # print("Error", e)
        pass
    await page.wait_for_selector('div[class^="ProfileContactSnippet-root-"]')
    review_awaited = await page.query_selector_all('div[class^="ProfileContactSnippet-root-"]')
    try:
        for count, element in enumerate(review_awaited):
            awaited_user = await element.query_selector(f'span[data-marker="contact({count})/userTitle"]')
            if awaited_user:
                awaited_user = await awaited_user.inner_text()

            awaited_title = await element.query_selector(f'span[data-marker="contact({count})/itemTitle"]')
            if awaited_title:
                awaited_title = await awaited_title.inner_text()

            awaited_price = await element.query_selector(f'span[data-marker="contact({count})/itemPrice"]')
            if awaited_price:
                awaited_price = await awaited_price.inner_text()

            data_awaited[f'review_awaited_{count}'] = {'user_title': awaited_user, 'item_text': awaited_title,
                                                       'prise_text': awaited_price}
    except Exception as e:
        # logger.error(f'{e}, Something this')
        pass
    # проверка товаров "Оставленные"
    try:
        await emulate_mouse_movement(page, 3)
        await page.goto('https://www.avito.ru/profile/reviews')
        try:
            await see_more_snippet(page, 'div[class^="ReviewSnippet-body-"]')
        except Exception as e:
            # print("Error2", e)
            pass
        review_posted = await page.query_selector_all('div[class^="ReviewSnippet-body-"]')
        for count, element in enumerate(review_posted):
            posted_status = await element.query_selector(f'span[data-marker^="review({count})/status"]')
            if posted_status:
                posted_status = await posted_status.inner_text()

            posted_stage = await element.query_selector(f'span[data-marker^="review({count})/stage"]')
            if posted_stage:
                posted_stage = await posted_stage.inner_text()

            posted_title = await element.query_selector(f'span[data-marker^="review({count})/itemTitle"]')
            if posted_title:
                posted_title = await posted_title.inner_text()

            posted_text = await element.query_selector(f'span[data-marker^="review({count})/text-section/text"]')
            if posted_text:
                posted_text = await posted_text.inner_text()
            data_posted[f'review_posted_{count}'] = {'review_status': posted_status, 'review_stage': posted_stage,
                                                     'review_item': posted_title, 'review_text': posted_text}
    except Exception as e:
        # logger.error(f'{e}, Or mb Something this')
        pass

    data['review_awaited'] = data_awaited
    data['review_posted'] = data_posted

    await emulate_mouse_movement(page, 3)
