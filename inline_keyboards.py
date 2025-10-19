from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os

def main_inline_kb() -> InlineKeyboardMarkup:
    make_collage = InlineKeyboardButton(
        text="Сделать коллаж",
        callback_data='start_make_collage',
    )

    example_collage = InlineKeyboardButton(
        text="Как это работает?",
        url=os.getenv('post_url')
    )
    rows = [[make_collage, example_collage]]

    main_markup_inline = InlineKeyboardMarkup(inline_keyboard=rows)

    return main_markup_inline


def subscribe_inline_keyboard(user_id) -> InlineKeyboardMarkup:
    buider = InlineKeyboardBuilder()
    buider.button(text="Телеграм канал",
                  url=os.getenv('post_url'))
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


def channels_kb(kb_list: list):
    inline_keyboard = []

    print(type(kb_list))
    for channel_data in kb_list:
        print(channel_data)
        label = channel_data.get('label')
        url = channel_data.get('url')

        # Проверка на наличие необходимых ключей
        if label and url:
            kb = [InlineKeyboardButton(text=label, url=url)]
            inline_keyboard.append(kb)

    # Добавление кнопки "Проверить подписку"
    inline_keyboard.append([InlineKeyboardButton(text="Проверить подписку", callback_data="check_subscription")])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def admin_kb():
    buider = InlineKeyboardBuilder()
    buider.button(text="👥 Пользователи", callback_data="admin_users")
    buider.button(text="📧 Рассылка", callback_data="admin_broadcast")

    return buider.as_markup()
