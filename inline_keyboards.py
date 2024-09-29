from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

random_site_cb_data = "random_site_cb_data"
start_make_collage = "start_make_collage"
next_inline_kb = "next_inline_kb"
start_choose_collage = "start_choose_collage"


def build_info_kb() -> InlineKeyboardMarkup:
    tg_channel_btn = InlineKeyboardButton(
        text="Канал",
        url='https://t.me/mnfcs'
    )

    btn_random_site = InlineKeyboardButton(
        text="random site",
        callback_data=random_site_cb_data,
    )

    row = [tg_channel_btn]
    rows = [row,
            [btn_random_site]]
    markup_inline = InlineKeyboardMarkup(inline_keyboard=rows)

    return markup_inline

def main_inline_kb()-> InlineKeyboardMarkup:
    make_collage = InlineKeyboardButton(
        text="Сделать коллаж",
        callback_data=start_choose_collage,
    )

    example_collage = InlineKeyboardButton(
        text="Как это работает?",
        url="https://t.me/mnfcs/199"
    )
    rows = [[make_collage, example_collage]]

    main_markup_inline = InlineKeyboardMarkup(inline_keyboard=rows)

    return main_markup_inline

def subscribe_inline_keyboard(user_id) -> InlineKeyboardMarkup:
    buider = InlineKeyboardBuilder()
    buider.button(text="Телеграм канал",
         url='https://t.me/mnfcs')
    buider.button(text="Я подписался",
        callback_data='next_inline_kb', user_id=user_id)

    return buider.as_markup()

def ways_collages() -> InlineKeyboardMarkup:
    buider = InlineKeyboardBuilder()

    buider.button(text="Коллаж без интервалов",
                  callback_data=start_make_collage)

    buider.button(text="Задать интервалы",
                  url='https://t.me/asdasdasdasd')


    return buider.adjust(1).as_markup()


