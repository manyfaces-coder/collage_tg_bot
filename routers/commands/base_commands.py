import os
from aiogram import Router, types, F
from aiogram.enums import ChatMemberStatus
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery
from dotenv import load_dotenv, find_dotenv
# from bot_script_webhook import check_flood
from bot_script_webhook import custom_redis
from bot_script_webhook import tg_channels, bot
from inline_keyboards import main_inline_kb, channels_kb, subscribe_inline_keyboard

from utils.db import get_user_by_id, add_user, update_bot_open_status, get_db_pool

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

    # Получаем пул соединений
    pool = await get_db_pool()

    # Получаем данные пользователя
    user_data = await get_user_by_id(pool, user_id)

    # if check_flood.is_flood(user_id=str(message.from_user.id), interval=5):
    if await custom_redis.is_flood(user_id=str(message.from_user.id), interval=1):
        await message.answer(text='Вы слишком часто отправляете сообщения. Подождите немного!')
        return

    if user_data is None:
        # Если пользователя нет в базе данных
        await add_user(pool, telegram_id=user_id, username=message.from_user.username,
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


# обработчик команды /help
@router.message(Command("help", prefix="/"))
async def handle_help(message: types.Message):
    await message.answer(text=f"Задайте вопрос ему: @oljick13")


@router.callback_query(F.data == 'check_subscription')
async def check_subs_funk(callback_query: CallbackQuery):
    """Проверяет подписки только для новых пользователей по списку каналов (нужно для старта и рекламы)"""
    for channel in tg_channels:
        label = channel.get('label')
        channel_url = channel.get('url')
        user_id = callback_query.from_user.id
        check = await is_user_subscribed(channel_url, user_id)
        if check is False:
            await callback_query.message.edit_text(f"❌ вы не подписались на канал 👉 {label}",
                                                   reply_markup=channels_kb(tg_channels))
            return False

        # Получаем пул соединений
        pool = await get_db_pool()

    await update_bot_open_status(pool, telegram_id=callback_query.from_user.id, bot_open=True)

    await callback_query.message.edit_text(
        text=f"Давай сделаем коллаж", reply_markup=main_inline_kb()
    )

    await callback_query.answer(text=("СПАСИБО 🤝"), show_alert=True, cache_time=10)




async def check_sub(message, user=None):
    """Проверка подписки только на главный канал, проверка постоянная и используется для оснвных функций бота"""
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


async def is_user_subscribed(channel_url: str, telegram_id: int) -> bool:
    """Проверка подписки на список каналов"""
    try:
        # Получаем username канала из URL, пример (https://t.me/mnfcs)
        channel_username = channel_url.split('/')[-1]

        # Получаем информацию о пользователе в канале
        member = await bot.get_chat_member(chat_id=f"@{channel_username}", user_id=telegram_id)

        # Проверяем статус пользователя
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
            return True
        else:
            return False
    except Exception as e:
        # Если возникла ошибка (например, пользователь не найден или бот не имеет доступа к каналу)
        print(f"Ошибка при проверке подписки: {e}")
        return False


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


