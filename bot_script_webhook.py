from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv, find_dotenv
from aiogram.enums import ParseMode
import os
from aiogram.fsm.storage.memory import MemoryStorage
import redis.asyncio as redis
from aiogram.fsm.storage.redis import RedisStorage as AiogramRedisStorage

from utils.redis_storage import RedisStorage


load_dotenv(find_dotenv())
ADMIN_ID = int(os.getenv('id_admin'))
BOT_TOKEN = os.getenv("TOKEN")
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
# WEBHOOK_PATH = f'/{BOT_TOKEN}'
WEBHOOK_PATH = '/'
BASE_URL = os.getenv("BASE_URL")
tg_channels = [{'label': 'Канал', 'url': f'{os.getenv("main_chanel")}'}]
REDIS_URL = os.getenv("REDIS_URL") or f"redis://{os.getenv('REDIS_HOST','localhost')}:{int(os.getenv('REDIS_PORT',6379))}/0"

redis_client = redis.from_url(REDIS_URL, decode_responses=True)
# Используем `AiogramRedisStorage` для FSM
redis_storage =AiogramRedisStorage(redis_client)

# Используем наш `RedisStorage` для произвольных данных (антифлуд, изображения и т. д.)
custom_redis = RedisStorage(redis_url=REDIS_URL, key_prefix="bot")  # твой класс

# инициализируем бота и диспетчера для работы с ним
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# dp = Dispatcher(storage=MemoryStorage())
dp = Dispatcher(storage=redis_storage)



