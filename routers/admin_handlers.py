from states import Broadcast
from aiogram import Router, F, types
from dotenv import load_dotenv, find_dotenv
from aiogram.fsm.context import FSMContext
from bot_script_webhook import ADMIN_ID
from keyboards import cancel_btn
from inline_keyboards import admin_kb
from aiogram.types import CallbackQuery
from utils.db import get_all_users
from aiogram.enums import ContentType
from utils.utils import broadcast_message

from admin_functions import administrator_request, answer_for_admin

load_dotenv(find_dotenv())

router = Router(name=__name__)


@router.message(F.from_user.id.in_({ADMIN_ID}), F.text == administrator_request)
async def secret_admin_message(message: types.Message):
    await message.reply(answer_for_admin)


# Получить список админских действий (админ панель)
@router.message((F.from_user.id == ADMIN_ID) & (F.text == '⚙️ АДМИНКА'))
async def admin_handler(message: types.Message):
    await message.answer('Вам открыт доступ в админку! Выберите действие👇', reply_markup=admin_kb())


# Получить список пользователей
@router.callback_query((F.from_user.id == ADMIN_ID) & (F.data == 'admin_users'))
async def admin_users_handler(call: CallbackQuery):
    await call.answer('Готовлю список пользователей')
    users_data = await get_all_users()

    text = f'В базе данных {len(users_data)}. Вот информация по ним:\n\n'

    for user in users_data:
        text += f'<code>{user["telegram_id"]} - {user["first_name"]}</code>\n'

    await call.message.answer(text, reply_markup=admin_kb())


@router.callback_query((F.from_user.id == ADMIN_ID) & (F.data == 'admin_broadcast'))
async def admin_broadcast_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(
        'Отправьте любое сообщение, а я его перехвачу и перешлю всем пользователям с базы данных',
        reply_markup=cancel_btn()
    )
    await state.set_state(Broadcast.start_broadcast)


# Рассылка запущена
@router.message(F.content_type.in_({'text', 'photo', 'document', 'video', 'audio'}), Broadcast.start_broadcast)
async def universe_broadcast(message: types.Message, state: FSMContext):
    users_data = await get_all_users()

    # Определяем параметры для рассылки в зависимости от типа сообщения
    content_type = message.content_type

    if content_type == ContentType.TEXT and message.text == '❌ Отмена':
        await state.clear()
        await message.answer('Рассылка отменена!', reply_markup=admin_kb())
        return

    await message.answer(f'Начинаю рассылку на {len(users_data)} пользователей.')

    good_send, bad_send = await broadcast_message(
        users_data=users_data,
        text=message.text if content_type == ContentType.TEXT else None,
        photo_id=message.photo[-1].file_id if content_type == ContentType.PHOTO else None,
        document_id=message.document.file_id if content_type == ContentType.DOCUMENT else None,
        video_id=message.video.file_id if content_type == ContentType.VIDEO else None,
        audio_id=message.audio.file_id if content_type == ContentType.AUDIO else None,
        caption=message.caption,
        content_type=content_type
    )

    await state.clear()
    await message.answer(f'Рассылка завершена. Сообщение получило <b>{good_send}</b>, '
                         f'НЕ получило <b>{bad_send}</b> пользователей.', reply_markup=admin_kb())
