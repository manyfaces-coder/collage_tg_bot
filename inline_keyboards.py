from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_inline_kb() -> InlineKeyboardMarkup:
    make_collage = InlineKeyboardButton(
        text="Сделать коллаж",
        callback_data='start_make_collage',
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
                  # callback_data=start_make_collage)
                  callback_data='make_simple_collage')

    buider.button(text="Коллаж с интервалами",
                  callback_data='make_interval_collage')

    buider.button(text='Назад ⤴',
                  callback_data='back_main_inline_kb')

    return buider.adjust(1).as_markup()


def input_intervals() -> InlineKeyboardMarkup:
    buider = InlineKeyboardBuilder()
    buider.button(text='Как написать интервалы?', callback_data='intervals_info')
    buider.button(text='Назад ⤴', callback_data='cancel_intervals')
    return buider.adjust(1).as_markup()


def agreement_with_intervals() -> InlineKeyboardMarkup:
    buider = InlineKeyboardBuilder()
    buider.button(text='Да', callback_data='intervals_accepted')
    buider.button(text='Нет', callback_data='reassign_intervals')
    return buider.as_markup()


def image_for_collage() -> InlineKeyboardMarkup:
    buider = InlineKeyboardBuilder()
    buider.button(text='Да', callback_data='image_accepted')
    buider.button(text='Нет', callback_data='reassign_image')
    return buider.as_markup()
