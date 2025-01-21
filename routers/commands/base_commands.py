import os
from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery
from dotenv import load_dotenv, find_dotenv

from bot_script_webhook import tg_channels
from inline_keyboards import main_inline_kb, input_intervals, channels_kb
from routers.common_functions import check_sub
from aiogram.fsm.context import FSMContext

from utils.db import get_user_by_id, add_user, update_bot_open_status
from utils.utils import is_user_subscribed

load_dotenv(find_dotenv())
channel_id = int(os.getenv('channel_id'))

router = Router(name=__name__)
load_dotenv(find_dotenv())


# Проверка на бота
@router.message(F.from_user.is_bot == True)
async def handle_bots(message: types.Message):
    return


@router.message(CommandStart())
async def handle_start(message: types.Message):
    user_id = message.from_user.id
    user_data = await get_user_by_id(user_id)

    if user_data is None:
        # Если пользователя нет в базе данных
        await add_user(telegram_id=user_id, username=message.from_user.username,
                       first_name=message.from_user.first_name)
        bot_open = False

    else:
        # Получение статуса bot_open для пользователя
        bot_open = user_data.get('bot_open', False)  # Второй параметр по умолчанию False

    if bot_open:
        # Если пользователь подписался на каналы
        await message.answer(text=f"Давай сделаем коллаж", reply_markup=main_inline_kb())

    else:
        # Иначе показываем клавиатуру с каналами для подписки
        # markup = subscribe_inline_keyboard(message.from_user.id)
        await message.answer(
            f'Привет, {message.from_user.full_name}!\n\n'
            'Для работы с ботом необходимо подписаться на канал:',
            reply_markup=channels_kb(tg_channels)

        )


@router.callback_query(F.data == 'check_subscription')
async def check_subs_funk(callback_query: CallbackQuery):
    for channel in tg_channels:
        label = channel.get('label')
        channel_url = channel.get('url')
        user_id = callback_query.from_user.id
        check = await is_user_subscribed(channel_url, user_id)
        if check is False:
            await callback_query.message.edit_text(f"❌ вы не подписались на канал 👉 {label}",
                                                   reply_markup=channels_kb(tg_channels))
            return False

    await update_bot_open_status(telegram_id=callback_query.from_user.id, bot_open=True)

    await callback_query.message.edit_text(
        text=f"Давай сделаем коллаж", reply_markup=main_inline_kb()
    )

    await callback_query.answer(text=("СПАСИБО 🤝"), show_alert=True, cache_time=10)


# обработчик команды /help
@router.message(Command("help", prefix="/"))
async def handle_help(message: types.Message):
    await message.answer(text=f"Задайте вопрос ему: @oljick13")


# обработчик инлайн кнопки "Я подписался"
@router.callback_query(F.data == "next_inline_kb")
async def handle_already_sub_edited(callback_query: CallbackQuery):
    if await check_sub(callback_query.message, user=callback_query.from_user.id):
        await update_bot_open_status(telegram_id=callback_query.from_user.id, bot_open=True)
        await callback_query.answer(
            text=(
                "СПАСИБО 🤝"
            ),
            show_alert=True,
            cache_time=10
        )
        await callback_query.message.edit_text(
            text=f"Давай сделаем коллаж", reply_markup=main_inline_kb()
        )


# обработка инлайн кнопки "Назад к главному выбору"
@router.callback_query(F.data == 'back_main_inline_kb')
async def back_main_inline_kb(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text(
        text='Выберите действие', reply_markup=main_inline_kb()
    )


# обработка инлайн кнопки "Назад к главному выбору"
@router.callback_query(F.data == 'close_about_intervals')
async def close_about_intervals(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        text='Введите два обычных целых числа через пробел или любой другой символ',
        reply_markup=input_intervals()
    )
