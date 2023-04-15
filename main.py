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
    asyncio.create_task(sched())

async def on_shutdown(_):
    print('Bye!')


def main():
    executor.start_polling(dp, fast=True, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == '__main__':
    main()
