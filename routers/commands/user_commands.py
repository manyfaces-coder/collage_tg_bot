import os
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv, find_dotenv

from routers.common_functions import check_sub

router = Router(name=__name__)

load_dotenv(find_dotenv())
channel_id = int(os.getenv('channel_id'))
"""
пока ненужный файл, был создан при проверке работы функций из обучающих ресурсов
"""