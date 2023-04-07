from aiogram import Bot, Dispatcher, types
from dotenv import find_dotenv, load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

load_dotenv(find_dotenv())
token = os.getenv('BOT_TOKEN')

bot = Bot(token, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
