import asyncio
import logging

from aiogram.utils import executor
from aiohttp import web

from avito_runner import start
from flask_manager import app, index
from handlers import dp, init_all
from sched import sched

logging.basicConfig(filename='logs.log', level=logging.WARNING)


async def on_startup(_):
    init_all()

    print('Online!')

    app.router.add_route('*', '/', index)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='195.2.67.220', port=80)
    await asyncio.sleep(10)
    await site.start()
    asyncio.create_task(
            start(number='79897060940', mail='antondoksin281@gmail.com', password='Klo-56CxR',
                site='https://www.avito.ru/krasnodar/predlozheniya_uslug/krutoy_dizayn_vizitok_flaerov_listovok_bukletov_3050623811',
                review_text='Всё на высшем уровне, получилось так, как я хотел, только даже лучше. Андрей очень помог нам с дизайном флайеров!',
                ip='45.146.171.104',
                port='62564',
                proxy_username='sZmCpM1j',
                proxy_password='DBwZBaZa',
                user_agent='Mozilla/5.0 (X11; Linux i686; rv:112.0) Gecko/20100101 Firefox/112.0'))
#kulovboris10@gmail.com,Klm-dg67

async def on_shutdown(_):
    print('Bye!')


def main():
    executor.start_polling(dp, fast=True, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == '__main__':

    main()
