import os
from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery
from dotenv import load_dotenv, find_dotenv

from inline_keyboards import main_inline_kb, ways_collages, input_intervals
from routers.common_functions import check_sub
from aiogram.fsm.context import FSMContext

load_dotenv(find_dotenv())
channel_id = int(os.getenv('channel_id'))

router = Router(name=__name__)
load_dotenv(find_dotenv())
bot = Bot(token=os.getenv('TOKEN'))


# Проверка на бота
@router.message(F.from_user.is_bot == True)
async def handle_bots(message: types.Message):
    return


# Использована команда /start
@router.message(CommandStart())
async def handle_start(message: types.Message):
    # если пользователь подписан
    print("НАЖАЛ СТАРТ")
    if await check_sub(channel_id, message.from_user.id, message.chat.id):
        await message.answer(text=f"Привет, {message.from_user.full_name}!", reply_markup=main_inline_kb())


@router.message(Command("help", prefix="/"))
async def handle_help(message: types.Message):
    if await check_sub(channel_id, message.from_user.id, message.chat.id):
        await message.answer(text=f"Задайте вопрос ему: @oljick13")


@router.callback_query(F.data == "next_inline_kb")
async def handle_already_sub_edited(callback_query: CallbackQuery):
    if await check_sub(channel_id, user_id=callback_query.from_user.id, chat_id=callback_query.message.chat.id):
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


@router.callback_query(F.data == "start_choose_collage")
async def choose_collage(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        text="Выберите, как хотите сделать коллаж:", reply_markup=ways_collages())


# обработка инлайн кнопки "Назад к главному выбору"
@router.callback_query(F.data == 'back_main_inline_kb')
async def back_main_inline_kb(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text(
        text='Выберите действие', reply_markup=main_inline_kb()
    )


@router.callback_query(F.data == 'close_about_intervals')
async def close_about_intervals(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        text='Введите два обычных целых числа через пробел или любой другой символ',
        reply_markup=input_intervals()
    )
