import logging

from aiogram.utils import executor

from handlers import dp, init_all

logging.basicConfig(filename='logs.log', level=logging.WARNING)


async def on_startup(_):
    init_all()
    print('Online!')


async def on_shutdown(_):
    print('Bye!')


def main():
    executor.start_polling(dp, fast=True, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == '__main__':
    main()
