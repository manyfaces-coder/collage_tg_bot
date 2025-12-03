import os
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, InputMediaVideo
from dotenv import load_dotenv, find_dotenv

from instruction import HOW_IT_WORKS_TEXT, EXAMPLE_VIDEO_ID, BEFORE_IMAGE_ID, AFTER_IMAGE_ID
from bot_script_webhook import custom_redis
from inline_keyboards import main_inline_kb, input_intervals, admin_kb
from keyboards import main_contact_kb
from routers.commands.base_commands import check_sub

load_dotenv(find_dotenv())
router = Router()
channel_id = int(os.getenv('channel_id'))


# обработчик голосовых сообщений
@router.message(F.voice)
async def handle_video_message(message: types.Message):
    await message.answer("Да зачем мне эти штуки, я ниче кроме картинок не понимаю яжебот, лучше денег скинь:"
                         f" {os.getenv('CARD_NUMB')}")


@router.message(F.text == "❌ Отмена")
async def handle_admin_cancel_button(message: types.Message):
    await message.answer('Рассылка отменена!', reply_markup=main_contact_kb(message.from_user.id))


# обработчик любых сообщений кроме изображений
@router.message(~F.photo)
async def handle_unknown_message(message: types.Message):
    # if check_flood.is_flood(user_id=str(message.from_user.id), interval=5):
    # if await custom_redis.is_flood(user_id=str(message.from_user.id), interval=1):
    if await custom_redis.is_flood(user_id=str(message.from_user.id)):
        await message.answer(text='Вы слишком часто отправляете сообщения. Подождите немного!')
        return
    if await check_sub(message):
        markup = main_inline_kb()
        await message.answer(text='Я не понимаю, что вы хотите, пожалуйста выберите действие', reply_markup=markup)


@router.callback_query(F.data == 'back_main_inline_kb')
async def back_main_inline_kb(callback_query: CallbackQuery, state: FSMContext):
    """Обработка инлайн кнопки "Назад к главному выбору"""
    await state.clear()
    await custom_redis.delete_data(f"user_image:{callback_query.from_user.id}")  # Удаляем фото
    # await custom_redis.delete_data(f"user_state:{message.from_user.id}")  # Удаляем состояние
    await custom_redis.delete_data(f"user_state:{callback_query.from_user.id}")  # Удаляем состояние
    await callback_query.message.edit_text(
        text='Выберите действие', reply_markup=main_inline_kb()
    )


@router.callback_query(F.data == 'close_about_intervals')
async def close_about_intervals(callback_query: CallbackQuery):
    """Обработка инлайн кнопки "Назад к вводу интервалов"""
    await callback_query.message.edit_text(
        text='Введите два обычных целых числа через пробел или любой другой символ',
        reply_markup=input_intervals()
    )

@router.callback_query(F.data == "example_collage")
async def show_example(callback_query: types.CallbackQuery):
    await callback_query.answer()

    media = [
        InputMediaVideo(
            media=EXAMPLE_VIDEO_ID,
            caption=HOW_IT_WORKS_TEXT,
            parse_mode="HTML",
        ),
        InputMediaPhoto(media=BEFORE_IMAGE_ID),
        InputMediaPhoto(media=AFTER_IMAGE_ID),
    ]

    await callback_query.message.answer_media_group(media)