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
tg_channels = [{'label': 'Мануфацус', 'url': 'https://t.me/mnfcs'}]
# check_flood = AntiFlood(redis_host='localhost', redis_port=6379)
# check_flood = AntiFlood(redis_host=os.getenv("REDIS_HOST", "localhost"), redis_port=int(os.getenv("REDIS_PORT", 6379)))

# redis_storage = RedisStorage(redis_host=os.getenv("REDIS_HOST", "localhost"), redis_port=int(os.getenv("REDIS_PORT", 6379)))

redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", 6379)))
# Используем `AiogramRedisStorage` для FSM
redis_storage =AiogramRedisStorage(redis_client)

# Используем наш `RedisStorage` для произвольных данных (антифлуд, изображения и т. д.)
custom_redis = RedisStorage(
    redis_host=os.getenv("REDIS_HOST", "localhost"),
    redis_port=int(os.getenv("REDIS_PORT", 6379))
)

# инициализируем бота и диспетчера для работы с ним
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# dp = Dispatcher(storage=MemoryStorage())
dp = Dispatcher(storage=redis_storage)



