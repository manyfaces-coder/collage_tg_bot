from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv, find_dotenv
from aiogram.enums import ParseMode
import os


load_dotenv(find_dotenv())
ADMIN_ID = os.getenv('id_admin')
BOT_TOKEN = os.getenv("TOKEN")
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
WEBHOOK_PATH = f'/{BOT_TOKEN}'
BASE_URL = os.getenv("BASE_URL")

# инициализируем бота и диспетчера для работы с ним
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()