import os
from aiogram import Router, types, Bot, F
from dotenv import load_dotenv, find_dotenv

from inline_keyboards import subscribe_inline_keyboard, main_inline_kb
from bot_script_webhook import bot

load_dotenv(find_dotenv())
router = Router()
channel_id = int(os.getenv('channel_id'))


async def check_sub(message, user=None):
    if user is None:
        user = message.from_user.id
    # Проверяем, подписан ли пользователь на канал
    is_subscribed = await bot.get_chat_member(chat_id=channel_id, user_id=user)
    print(is_subscribed.status)
    if is_subscribed.status == 'member' or is_subscribed.status == 'creator' \
            or is_subscribed.status == 'administrator':
        return True
    else:
        markup = subscribe_inline_keyboard(message.from_user.id)
        await bot.send_message(chat_id=message.chat.id, text="Для доступа к Боту подпишитесь на канал "
                               , reply_markup=markup)


# обработчик голосовых сообщений
@router.message(F.voice)
async def handle_video_message(message: types.Message):
    await message.answer("Да зачем мне эти штуки, я ниче кроме картинок не понимаю яжебот, лучше денег скинь:"
                         f" {os.getenv('CARD_NUMB')}")


# обработчик любых сообщений кроме изображений
@router.message(~F.photo)
async def handle_unknown_message(message: types.Message):
    if await check_sub(message):
        markup = main_inline_kb()
        await message.answer(text='Я не понимаю, что вы хотите, пожалуйста выберите действие', reply_markup=markup)
