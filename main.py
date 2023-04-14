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
    asyncio.create_task(start(number='89896372338', mail='milatre783@gmail.com', password='5Q3n5Us6x',
                              site='https://www.avito.ru/krasnodar/detskaya_odezhda_i_obuv/baletki_tufli_33_r_dve_pary_2944039264',
                              review_text='Балетки супер, у меня вот дочь маленькая капец какая, но даже она поняла какие эти балетки топ',
                              ip='77.91.91.137',
                              port='63910',
                              proxy_username='DjYgvRek',
                              proxy_password='jCcfW5CL',
                              user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'))
    await site.start()


async def on_shutdown(_):
    print('Bye!')


def main():
    executor.start_polling(dp, fast=True, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == '__main__':
    main()
