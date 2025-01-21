import os
from aiogram import Router, types, F
from dotenv import load_dotenv, find_dotenv
from aiogram.enums import ChatMemberStatus

from inline_keyboards import subscribe_inline_keyboard, main_inline_kb
from bot_script_webhook import bot
from keyboards import main_contact_kb
from utils.db import update_bot_open_status

load_dotenv(find_dotenv())
router = Router()
channel_id = int(os.getenv('channel_id'))


# Проверка подписки только на мой канал, проверка постоянная и используется для оснвных функций бота
async def check_sub(message, user=None):
    try:
        if user is None:
            user = message.from_user.id
        # Проверяем, подписан ли пользователь на канал
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
            return True
        else:
            markup = subscribe_inline_keyboard(message.from_user.id)
            await bot.send_message(chat_id=message.chat.id, text="Для доступа к Боту подпишитесь на канал "
                                   , reply_markup=markup)
            await update_bot_open_status(telegram_id=message.chat.id, bot_open=False)
            return False

    except Exception as exp:
        print(f"Ошибка при проверке подписки: {exp}")
        await bot.send_message(chat_id=message.chat.id,
                               text="По какой-то причине не удалось проверить подписку на канал")
        return False


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
    if await check_sub(message):
        markup = main_inline_kb()
        await message.answer(text='Я не понимаю, что вы хотите, пожалуйста выберите действие', reply_markup=markup)
