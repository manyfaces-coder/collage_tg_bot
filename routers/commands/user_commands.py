import os
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import KeyboardButton, KeyboardButtonRequestUser, KeyboardButtonRequestChat, ReplyKeyboardMarkup
from dotenv import load_dotenv, find_dotenv

from bot_script_webhook import ADMIN_ID
from routers.commands.base_commands import check_sub

router = Router(name=__name__)

load_dotenv(find_dotenv())
channel_id = int(os.getenv('channel_id'))
"""
пока ненужный файл, был создан при проверке работы функций из обучающих ресурсов
"""
