import os
import tempfile

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import RegexpMode
from re import Match

import main_script
from inline_keyboards import main_inline_kb
from routers.common_functions import bot
from states import Form
from aiogram.types import BufferedInputFile

# from aiogram.dispatcher.filters.state import State, StatesGroup


router = Router(name=__name__)


#
# @router.callback_query(F.data == "start_make_collage")
# async def request_image(message: types.Message):
#     await message.reply()#запросить изображение

# Определение состояний


@router.callback_query(F.data == "start_make_collage")
async def request_image(callback_query: types.CallbackQuery, state: FSMContext):
    # await callback_query.answer(callback_query.id)
    print(state)
    print(await state.get_state())
    print("---------")
    await callback_query.answer()
    await state.set_state(Form.user_image)
    # await state.(Form.waiting_for_image)
    print(state)
    print(await state.get_state())
    buider = InlineKeyboardBuilder()
    # await Form.waiting_for_image.set()  # Перевод пользователя в состояние ожидания изображения
    # Добавление кнопки "Отмена" вместо предыдущего сообщения.
    buider.button(text='Отмена', callback_data='cancel_image')
    # markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text='Отмена', callback_data='cancel_image'))
    markup = buider.as_markup()
    # await callback_query.edi(text="Пожалуйста, отправьте изображение.", reply_markup=markup)
    await callback_query.message.edit_text("Пожалуйста, отправьте изображение.", reply_markup = markup)

#Обработчик получения изображения
@router.message(F.photo, Form.user_image)
# @router.message(state=Form.waiting_for_image)
async def image_received(message: types.Message, state: FSMContext):
    if await state.get_state() == Form.user_image:
        await state.update_data(user_image=message.photo)
        await state.clear()  # Выход из состояния
        print('Zdes')
        print(Form.user_image.state)
        print(Form.user_image.state.format())
        print(message.photo)
        # print(max(message.photo, key=lambda x: x.file_size))
        file_id = message.photo[-1].file_id
        photo = await bot.get_file(file_id)

        # Обработка изображения


        # Скачиваем файл фотографии в временный файл
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, 'photo.jpg')
            print(f"FILE_PATH = {file_path}")
            await bot.download(photo, file_path)

            # Передаем путь к файлу в функцию photo_collage
            result_file_path = main_script.start(file_path=file_path)

            # Отправляем обработанный файл пользователю
            from aiogram.types import FSInputFile
            """
            FSInputFile нужен для отправки файлов, которые хранятся на файловой системе, 
            а не в памяти. Это полезно, когда вам нужно отправить большие файлы, которые 
            не могут поместиться в память
            """
            agenda = FSInputFile(result_file_path)
            await bot.send_photo(message.chat.id, agenda)

        await message.reply("Изображение обработанно со стандартными интервалами")



# Обработчик нажатия на кнопку "Отмена"
@router.callback_query(lambda c: c.data == 'cancel_image')
# @router.callback_query(lambda c: c.data == 'cancel_image', state=Form.waiting_for_image)
async def cancel_image(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()  # Очистка состояния
    await callback_query.message.edit_text("Отправка изображения отменена.", reply_markup=main_inline_kb())

# Обработчик для текста или других типов сообщений в состоянии ожидания изображения
@router.message(~F.photo, Form.user_image)
async def not_image(message: types.Message, state: FSMContext):
    if await state.get_state() == Form.user_image:
        buider = InlineKeyboardBuilder()
        # Предупреждаем пользователя вместе с кнопкой "Отмена"
        buider.button(text='Отмена', callback_data='cancel_image')
        markup = buider.as_markup()
        await message.reply("Пожалуйста, отправьте изображение, а не текст или другой тип файла.", reply_markup=markup)
    else:
        pass

# @router.message(F.photo, ~F.caption)
# async def handle_photo(message: types.Message):
#     hg = await message.get_file()
#     print("message.get_file()")
#     print(hg)
#     await message.reply("I saw your picture, but add the intervals, please")


# @router.message(F.photo, F.caption)
# async def handle_photo_caption(message: types.Message):
#     # await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_PHOTO)
#         # message.reply_document.UPLOAD_PHOTO
#     # action_sender = ChatActionSender(
#     #     bot=message.bot,
#     #     chat_id=message.chat.id,
#     #     action=ChatAction.UPLOAD_PHOTO
#     # )
#     answer = "I saw your picture and the caption"
#     global image_received
#     image_received = 1
#     # await message.reply("I saw your picture and the caption")
#     await message.reply_photo(
#         photo=message.photo[-1].file_id,
#         caption=answer + f"Width = {message.photo[-1].width}\nHeight = {message.photo[-1].height}"
#     )

# @router.callback_query(F.data == "получить интервалы")
@router.message(F.text.regexp(r"(\d+)", mode=RegexpMode.FINDALL).as_("intervals"))
async def handle_numbers(message: types.Message, intervals: Match[list[int]]):
    global image_received
    if image_received != None:
        await message.reply(f"Your intervals: first={intervals[0]}\nsecond={intervals[1]}")
        image_received = None
    else:
        await message.reply("To specify the intervals, send an image")