import asyncio
from random import uniform


# чтобы он не проглатывал буквы ставим больше задержку, чтобы сервак успевал обрабатывать
# по возможности впихнуть сюда обработку последнего слова, чтобы он пробел не ставил
# на последний пробел похер, он всё равно находит варианты
async def writer(text_area, text):
    text = text.encode('utf-8')
    await text_area.type(text.decode('utf-8'), delay=uniform(50, 130))
    await asyncio.sleep(uniform(1, 2))
    await text_area.type(' ', delay=uniform(130, 200))

# async def check_writer(text_area, full_text):
#     cur_text = await page.