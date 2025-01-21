from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from bot_script_webhook import ADMIN_ID


def main_contact_kb(user_id: int):
    buttons = [
        [
            # KeyboardButton(
            #     text="",
            # )
        ]
    ]
    # Предназначена для доступа к административной панели бота
    if int(user_id) == int(ADMIN_ID):
        buttons.append([
            KeyboardButton(
                text="⚙️ АДМИНКА",
            )
        ])

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
        # input_field_placeholder="По кому получим ID?"
    )

    return keyboard


# Для отмены рассылки
def cancel_btn():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Или нажмите на 'ОТМЕНА' для отмены",
    )

