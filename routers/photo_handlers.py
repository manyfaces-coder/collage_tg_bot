import os
import re
import tempfile

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import RegexpMode
from re import Match

import main_script
from inline_keyboards import main_inline_kb, ways_collages, input_intervals, agreement_with_intervals, image_for_collage
from routers.common_functions import bot
from states import WaitUser
from bot_exceptions import CollageException, VerticalIntervalException, HorizontalIntervalException

router = Router(name=__name__)

pattern = r".*?(?!0)(\d+)(?!\d).+?(?!0)(\d+).*"


# Ожидание изображения от пользователя в состоянии
@router.callback_query(F.data == "start_make_collage")
async def request_image(callback_query: types.CallbackQuery, state: FSMContext):
    # Перевод пользователя в состояние ожидания изображения
    await state.set_state(WaitUser.user_image)
    # Добавление кнопки "Отмена" вместо предыдущего сообщения.
    buider = InlineKeyboardBuilder()
    buider.button(text='Отмена', callback_data='cancel_image')
    markup = buider.as_markup()
    await callback_query.message.edit_text("Пожалуйста, отправьте изображение.", reply_markup=markup)


# Обработчик получения изображения
@router.message(F.photo, WaitUser.user_image)
async def expected_image_received(message: types.Message, state: FSMContext):
    await state.update_data(user_mes=message)
    await state.update_data(user_image=message.photo)
    print(await state.get_state())
    await state.set_state(WaitUser.use_intervals)
    await message.reply(
        text="Выберите, как хотите сделать коллаж:", reply_markup=ways_collages())


@router.message(F.photo)
async def image_received(message: types.Message, state: FSMContext):
    await state.update_data(user_mes=message)
    await state.update_data(user_image=message.photo)
    await message.reply(text='Вы хотите сделать коллаж из этого изображения?',
                        reply_markup=image_for_collage())


@router.callback_query(F.data == "image_accepted")
async def image_accepted(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(text="Выберите, как хотите сделать коллаж:",
                                           reply_markup=ways_collages())


@router.callback_query(F.data == "reassign_image")
async def reassign_image(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(text='Выберите действие',
                                           reply_markup=main_inline_kb())


@router.callback_query(F.data.in_({"make_simple_collage", "make_interval_collage"}))
async def interval_solution(callback_query: types.CallbackQuery, state: FSMContext):
    # если нажимают на кнопку выбора интервала, после того, как сбросилось состояние,
    # например, бота выключали и включили снова
    if (await state.get_data()).get("user_image") is None or (await state.get_data()).get("user_mes") is None:
        await callback_query.message.edit_text('Произошла ошибка, попробуйте сначала')
        return
    if callback_query.data == 'make_interval_collage':
        print('INTERVALS')
        await state.update_data(use_intervals=True)
        await state.set_state(WaitUser.intervals)
        await callback_query.message.edit_text(
            text='Введите два обычных целых числа через пробел или любой другой символ',
            reply_markup=input_intervals())
    else:
        await state.update_data(use_intervals=False)
        data = await state.get_data()
        print(f'user_image – {data.get("user_image")}')
        print(f'user_mes – {data.get("user_mes")}')
        print(f'intervals – {data.get("intervals")}')
        await state.clear()
        await make_collage(data)


async def make_collage(data: dict, vertical_interval=30, horizontal_interval=30) -> None:
    print('user_image' in data.keys())
    print("DATA")
    print(data.keys())
    message = data['user_mes']
    await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")

    file_id = data['user_image'][-1].file_id
    photo = await bot.get_file(file_id)

    # Обработка изображения
    # Скачиваем файл фотографии в временный файл
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, 'photo.jpg')
        print(f"FILE_PATH = {file_path}")
        result_file_path = False
        await bot.download(photo, file_path)

        from aiogram.types import FSInputFile
        """
        FSInputFile нужен для отправки файлов, которые хранятся на файловой системе, 
        а не в памяти. Это полезно, когда вам нужно отправить большие файлы, которые 
        не могут поместиться в память
        """

        # Передаем путь к файлу в функцию photo_collage
        try:
            result_file_path = main_script.start_for_bot(vertical_interval, horizontal_interval, file_path=file_path)
        except CollageException as exp:
            await bot.send_photo(chat_id=message.chat.id,
                                 photo=types.FSInputFile(path='main_images/murzik.jpg'),
                                 caption="Извините, произошла какая-то ошибка "
                                         "при оброботке фото, мой кот тоже не в "
                                         "восторге :(")

        except VerticalIntervalException as exp:
            await message.reply(str(exp))

        except HorizontalIntervalException as exp:
            await message.reply(str(exp))

        except Exception as exp:
            await message.reply(str(exp))

        # Отправляем обработанный файл пользователю
        if result_file_path:
            print(f"result_file_path {result_file_path}")
            agenda = FSInputFile(result_file_path)
            await bot.send_photo(message.chat.id, agenda)

            await message.reply("Изображение обработанно!\n"
                                "\nЧто дальше?", reply_markup=main_inline_kb())


# Обработчик нажатия на кнопку "Отмена" когда ждем изображение от пользователя
# @router.callback_query(lambda c: c.data == 'cancel_image')
@router.callback_query(lambda c: c.data == 'cancel_image', WaitUser.user_image)
async def cancel_image(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()  # Очистка состояния
    await callback_query.message.edit_text("Отправка отменена.", reply_markup=main_inline_kb())


# Обработчик нажатия на кнопку "Отмена" когда ждем интервалов от пользователя
@router.callback_query(lambda c: c.data == 'cancel_intervals')
async def cancel_intervals(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(WaitUser.use_intervals)  # Очистка состояния
    await callback_query.message.edit_text("Отправка отменена.", reply_markup=ways_collages())


# Обработчик для текста или других типов сообщений в состоянии ожидания изображения
@router.message(~F.photo, WaitUser.user_image)
async def not_image(message: types.Message, state: FSMContext):
    buider = InlineKeyboardBuilder()
    # Предупреждаем пользователя вместе с кнопкой "Отмена"
    buider.button(text='Отмена', callback_data='cancel_image')
    markup = buider.as_markup()
    await message.reply("Пожалуйста, отправьте изображение, а не текст или другой тип файла.", reply_markup=markup)


# Обработчик сообщений в режиме ожидания интервалов (надо добавить проверку через regexp)
@router.message(WaitUser.intervals, F.text.regexp(pattern, mode=RegexpMode.FINDALL).as_("found_intervals"))
async def get_intervals(message: types.Message, state: FSMContext, found_intervals):
    await state.update_data(intervals=found_intervals[0])
    vertical_interval = int(found_intervals[0][0])
    horizontal_interval = int(found_intervals[0][1])
    print(vertical_interval, horizontal_interval)
    await state.set_state(WaitUser.agree_intervals)
    print(await state.get_state())
    await message.reply(f'Интервалы по вертикали: {vertical_interval}\n'
                        f'Интервалы по горизонтали:  {horizontal_interval}'
                        f'\nОставляем так?', reply_markup=agreement_with_intervals())  # ДОБАВИТЬ КНОПКИ И ОБРАБОТЧИК


@router.callback_query(F.data == 'intervals_accepted', WaitUser.agree_intervals)
async def intervals_accepted(message: types.Message, state: FSMContext):
    await state.update_data(agree_intervals=True)
    data = await state.get_data()
    await state.clear()
    await make_collage(data, vertical_interval=int(data["intervals"][0]), horizontal_interval=int(data["intervals"][1]))


@router.callback_query(F.data == 'reassign_intervals', WaitUser.agree_intervals)
async def reassign_intervals(callback_query: types.CallbackQuery):
    print(F.data)
    await callback_query.message.edit_text(
        text='Введите два обычных целых числа через пробел или любой другой символ',
        reply_markup=input_intervals())


@router.message(WaitUser.intervals)
async def not_intervals(message: types.Message, state: FSMContext):
    await message.reply("Пожалуйста, отправьте интервалы, а не просто текст или какой-либо файл.",
                        reply_markup=input_intervals())


# Обработчик нажатия на кнопку "Об интервалах"
@router.callback_query(F.data == 'intervals_info')
async def intervals_info(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    buider = InlineKeyboardBuilder()
    # Предупреждаем пользователя вместе с кнопкой "Отмена"
    buider.button(text='Назад ⤴', callback_data='close_about_intervals')
    markup = buider.as_markup()
    await callback_query.message.edit_text("– интервалы ≠ 0\n \n– интервалы - целые числа\n"
                                           "\n – интервалы не могут быть cлишком большими\n"
                                           " числами относительно размера вашего изображения\n"
                                           "\nЖду ваших интервалов ↓", reply_markup=markup)


@router.callback_query(F.data.in_({"intervals_accepted", "reassign_intervals", "cancel_image"}))
async def intervals_accepted(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('Произошла ошибка, попробуйте сначала')

