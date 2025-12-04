import os

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from bot_script_webhook import ADMIN_ID
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
admin_command = os.getenv('admin_command')

def main_contact_kb(user_id: int):
    buttons = []
    # Предназначена для доступа к административной панели бота
    if int(user_id) == int(ADMIN_ID):
        buttons.append([
            KeyboardButton(
                text=admin_command,
            )
        ])

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
    )
    return keyboard


