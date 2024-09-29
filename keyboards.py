from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ButtonText:
    START = "Создать коллаж"
    HELP = "/help"
    EXAMPLE = "Показать пример"


# def get_on_start_kb():
#     button_start = KeyboardButton(text=ButtonText.START)
#     button_help = KeyboardButton(text=ButtonText.HELP)
#     button_example = KeyboardButton(text=ButtonText.EXAMPLE)
#     buttons_first_row = [button_start, button_help]
#     buttons_second_row = [button_example]
#     markup = ReplyKeyboardMarkup(
#         keyboard=[buttons_first_row, buttons_second_row],
#         resize_keyboard=True,
#     )
#     return markup

#TODO никак не используем клавиатуру
def get_on_start_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=ButtonText.START), KeyboardButton(text=ButtonText.HELP))
    builder.row(KeyboardButton(text=ButtonText.EXAMPLE))
    return builder.as_markup(resize_keyboard=True)
