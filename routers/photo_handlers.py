import os
import tempfile
import time
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import RegexpMode
from aiogram.types import FSInputFile
import main_script
from inline_keyboards import main_inline_kb, ways_collages, input_intervals, agreement_with_intervals, image_for_collage
from bot_script_webhook import bot, custom_redis
from routers.commands.base_commands import check_sub
from concurrent.futures import ProcessPoolExecutor
import asyncio
import logging
from states import WaitUser
from bot_exceptions import CollageException, VerticalIntervalException, HorizontalIntervalException

router = Router(name=__name__)
logger = logging.getLogger("bot")  # Получаем глобальный логгер
pattern = r".*?(?!0)(\d+)(?!\d).+?(?!0)(\d+).*"


@router.callback_query(F.data == "start_make_collage")
async def request_image(callback_query: types.CallbackQuery, state: FSMContext):
    """Ожидание изображения от пользователя в состоянии"""
    if await check_sub(callback_query.message, callback_query.from_user.id):
        # Перевод пользователя в состояние ожидания изображения
        await state.set_state(WaitUser.user_image)
        await custom_redis.set_data(f"user_state:{callback_query.from_user.id}", {"step": "waiting_image"})
        # Добавление кнопки "Отмена" вместо предыдущего сообщения.
        buider = InlineKeyboardBuilder()
        buider.button(text='Отмена', callback_data='cancel_image')
        markup = buider.as_markup()
        # await callback_query.message.edit_caption("Пожалуйста, отправьте изображение.", reply_markup=markup)
        await callback_query.message.edit_text("Пожалуйста, отправьте изображение.", reply_markup=markup)



@router.message(F.photo, WaitUser.user_image)
async def expected_image_received(message: types.Message, state: FSMContext):
    """Обработчик получения изображения в состоянии ожидания"""
    message_dict = message.model_dump()  # Преобразуем в JSON-совместимый формат
    file_id = message.photo[-1].file_id  # Берем последнее фото (лучшее качество)
    await state.update_data(user_mes=message_dict)  # Обновляем данные пользователя в FSM
    await state.update_data(user_image=file_id)  # Сохраняем только file_id
    # await custom_redis.set_data(f"user_state:{message.from_user.id}", {"step": "got_image"})
    await custom_redis.set_data(f"user_image:{message.from_user.id}", {"file_id": file_id})
    # await state.set_state(WaitUser.use_intervals)  # Переход к следующему шагу
    await custom_redis.set_state(message.from_user.id, "WaitUser.use_intervals")
    await message.reply("Выберите, как хотите сделать коллаж:", reply_markup=ways_collages())



@router.message(F.photo)
async def image_received(message: types.Message, state: FSMContext):
    if await check_sub(message):
        message_dict = message.model_dump()  # Преобразуем в JSON-совместимый формат
        file_id = message.photo[-1].file_id  # Берем последний (наивысшее качество)

        # Сохраняем данные в FSM и Redis
        await state.update_data(user_mes=message_dict)
        await state.update_data(user_image=file_id)
        await custom_redis.set_data(f"user_image:{message.from_user.id}", {"file_id": str(file_id)})
        await custom_redis.set_data(f"user_state:{message.from_user.id}", {"step": "got_image"})

        await message.reply(text='Вы хотите сделать коллаж из этого изображения?',
                            reply_markup=image_for_collage())


@router.callback_query(F.data == "image_accepted")
async def image_accepted(callback_query: types.CallbackQuery):
    """Обработчик получения изображения после того, как пользователь прислал фото и ответил 'да'"""
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
        await state.update_data(use_intervals=True)
        await state.set_state(WaitUser.intervals)
        await callback_query.message.edit_text(
            text='Введите два обычных целых числа через пробел или любой другой символ',
            reply_markup=input_intervals())
    else:
        await callback_query.message.edit_text("Выбран коллаж по умолчанию")
        await state.update_data(use_intervals=False)
        data = await state.get_data()
        await state.clear()
        await make_collage(data)

async def download_photo(file_id: str) -> str:
    """Загружает фото во временную папку и возвращает путь к файлу."""
    photo = await bot.get_file(file_id)
    tmp_dir = tempfile.TemporaryDirectory()
    file_path = os.path.join(tmp_dir.name, 'photo.jpg')
    await bot.download(photo, file_path)
    return file_path, tmp_dir


async def make_collage(data: dict, vertical_interval=30, horizontal_interval=30) -> None:
    """Основная функция обработки коллажа с многопроцессорностью."""

    message = data['user_mes']
    # message_id = message['message_id']
    chat_id = message['chat']['id']
    if chat_id:
        await bot.send_chat_action(chat_id=chat_id, action="upload_photo")
    file_id = data.get('user_image')
    if not file_id:
        redis_data = await custom_redis.get_data(f"user_image:{message['from_user']['id']}")
        if redis_data:
            file_id = redis_data["file_id"]

    if not file_id:
        # await message.reply("Ошибка: изображение не найдено.")
        await bot.send_message(chat_id=chat_id, text="Ошибка: изображение не найдено.")
        return

    await bot.send_chat_action(chat_id=chat_id, action="upload_photo")

    try:
        # Загрузка фото
        photo, tmp_dir = await download_photo(file_id)

        # Запускаем обработку
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor() as executor:
            result_file_path = await loop.run_in_executor(
                executor,
                main_script.start_for_bot,
                vertical_interval,
                horizontal_interval,
                photo,
            )

        # Отправка результата
        agenda = FSInputFile(result_file_path)
        # await bot.send_photo(message.chat.id, agenda)
        # await bot.send_photo(chat_id, agenda, caption="Изображение обработано!\n\nЧто дальше?", reply_markup=main_inline_kb())
        # os.remove(result_file_path)
        await bot.send_photo(chat_id, agenda)
        os.remove(result_file_path)

        # await message.reply("Изображение обработано!\n\nЧто дальше?", reply_markup=main_inline_kb())
        await bot.send_message(chat_id=chat_id, text="Изображение обработано!\n\nЧто дальше?", reply_markup=main_inline_kb())
        await custom_redis.reset_state(message["from_user"]["id"])

    except CollageException:
        # await message.reply("Изображение обработано!\n\nЧто дальше?", reply_markup=main_inline_kb())
        await bot.send_photo(chat_id=message.chat.id,
                             photo=FSInputFile(path='main_images/murzik.jpg'),
                             caption="Извините, произошла какая-то ошибка "
                                     "при обработке фото, мой кот тоже не в восторге :(")
    except VerticalIntervalException as exp:
        # await message.reply(str(exp))
        await bot.send_message(chat_id=chat_id, text=str(exp))

    except HorizontalIntervalException as exp:
        # await message.reply(str(exp))
        await bot.send_message(chat_id=chat_id, text=str(exp))
    except Exception as exp:
        logger.warning(f"Ошибка обработки изображения: {exp}")
        # await message.reply(f"Ошибка обработки")
        await bot.send_message(chat_id=chat_id, text=str(exp))
    finally:
        tmp_dir.cleanup()



# async def make_collage(data: dict, vertical_interval=30, horizontal_interval=30) -> None:
#     """Основная функция обработки коллажа."""
#     start_time = time.time()
#
#     message = data['user_mes']
#     file_id = data['user_image'][-1].file_id
#     await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
#
#     try:
#         # Загрузка фото
#         photo, tmp_dir = await download_photo(file_id)
#         # Обработка фото
#         result_file_path = main_script.start_for_bot(vertical_interval, horizontal_interval, file_path=photo)
#         # Отправка результата
#         agenda = FSInputFile(result_file_path)
#         await bot.send_photo(message.chat.id, agenda)
#         os.remove(result_file_path)
#         await message.reply("Изображение обработанно!\n\nЧто дальше?", reply_markup=main_inline_kb())
#
#     except CollageException:
#         await bot.send_photo(chat_id=message.chat.id,
#                              photo=types.FSInputFile(path='main_images/murzik.jpg'),
#                              caption="Извините, произошла какая-то ошибка "
#                                      "при оброботке фото, мой кот тоже не в "
#                                      "восторге :(")
#     except VerticalIntervalException as exp:
#         await message.reply(str(exp))
#
#     except HorizontalIntervalException as exp:
#         await message.reply(str(exp))
#
#     except Exception as exp:
#         await message.reply(str(exp))
#     finally:
#         tmp_dir.cleanup()
#
#     print("--- %s seconds ---" % (time.time() - start_time))


# #Многопроцессорная обработка
# async def make_collage(data: dict, vertical_interval=30, horizontal_interval=30) -> None:
#     """Основная функция обработки коллажа с многопроцессорностью."""
#
#
#     message = data['user_mes']
#     file_id = data['user_image'][-1].file_id
#     await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
#
#     try:
#         # Загрузка фото
#         photo, tmp_dir = await download_photo(file_id)
#
#         # Создаём пул процессов
#         # start_time = time.time()
#         loop = asyncio.get_running_loop()
#         with ProcessPoolExecutor() as executor:
#             # Вызываем функцию обработки в отдельном процессе
#             result_file_path = await loop.run_in_executor(
#                 executor,
#                 main_script.start_for_bot,  # Функция обработки
#                 vertical_interval,  # Аргументы функции
#                 horizontal_interval,
#                 photo,
#             )
#
#         # Отправка результата
#         agenda = FSInputFile(result_file_path)
#         await bot.send_photo(message.chat.id, agenda)
#         os.remove(result_file_path)
#         await message.reply("Изображение обработано!\n\nЧто дальше?", reply_markup=main_inline_kb())
#
#     except CollageException:
#         await bot.send_photo(chat_id=message.chat.id,
#                              photo=FSInputFile(path='main_images/murzik.jpg'),
#                              caption="Извините, произошла какая-то ошибка "
#                                      "при обработке фото, мой кот тоже не в восторге :(")
#     except VerticalIntervalException as exp:
#         await message.reply(str(exp))
#
#     except HorizontalIntervalException as exp:
#         await message.reply(str(exp))
#
#     except Exception as exp:
#         await message.reply(str(exp))
#     finally:
#         tmp_dir.cleanup()



# Обработчик нажатия на кнопку "Отмена" когда ждем изображение от пользователя
@router.callback_query(lambda c: c.data == 'cancel_image', WaitUser.user_image)
async def cancel_image(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()  # Очистка состояния
    await callback_query.message.edit_text("Отправка отменена", reply_markup=main_inline_kb())


# Обработчик нажатия на кнопку "Отмена" когда ждем интервалов от пользователя
@router.callback_query(lambda c: c.data == 'cancel_intervals')
async def cancel_intervals(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(WaitUser.use_intervals)  # Очистка состояния
    await callback_query.message.edit_text("Ввод интервалов отменен", reply_markup=ways_collages())


# Обработчик для текста или других типов сообщений в состоянии ожидания изображения
@router.message(~F.photo, WaitUser.user_image)
async def not_image(message: types.Message):
    buider = InlineKeyboardBuilder()
    # Предупреждаем пользователя вместе с кнопкой "Отмена"
    buider.button(text='Отмена', callback_data='cancel_image')
    markup = buider.as_markup()
    await message.reply("Пожалуйста, отправьте изображение, а не текст или другой тип файла.", reply_markup=markup)


# Обработчик сообщений в режиме ожидания интервалов (надо добавить проверку через regexp)
@router.message(WaitUser.intervals, F.text.regexp(pattern, mode=RegexpMode.FINDALL).as_("found_intervals"))
async def get_intervals(message: types.Message, state: FSMContext, found_intervals):
    if int(found_intervals[0][0]) > 100 or int(found_intervals[0][1]) > 100:
        await message.reply('🛑 Один из ваших интервалов больше 100 🛑\n'
                            'Пожалуйста введите интервалы заново')
    else:
        await state.update_data(intervals=found_intervals[0])
        vertical_interval = int(found_intervals[0][0])
        horizontal_interval = int(found_intervals[0][1])
        await state.set_state(WaitUser.agree_intervals)
        await message.reply(f'Интервалы по вертикали: {vertical_interval}\n'
                            f'Интервалы по горизонтали:  {horizontal_interval}'
                            f'\nОставляем так?',
                            reply_markup=agreement_with_intervals())  # ДОБАВИТЬ КНОПКИ И ОБРАБОТЧИК


@router.callback_query(F.data == 'intervals_accepted', WaitUser.agree_intervals)
async def intervals_accepted(callback_query: types.CallbackQuery, state: FSMContext):
    """Принимает интервалы, которые ввел пользователь"""
    await state.update_data(agree_intervals=True)
    data = await state.get_data()
    await state.clear()
    await callback_query.message.edit_text(f'Интервалы по вертикали: {int(data["intervals"][0])}\n'
                            f'Интервалы по горизонтали:  {int(data["intervals"][1])}')
    # await callback_query.message.delete()
    #удалить сообщение и отправить новое интервалы есть
    await make_collage(data, vertical_interval=int(data["intervals"][0]), horizontal_interval=int(data["intervals"][1]))


@router.callback_query(F.data.in_({"intervals_accepted", "reassign_intervals", "cancel_image"}))
async def processing_stateless_intervals(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('Произошла ошибка, попробуйте сначала')


@router.callback_query(F.data == 'reassign_intervals', WaitUser.agree_intervals)
async def reassign_intervals(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        text='Введите два обычных целых числа через пробел или любой другой символ',
        reply_markup=input_intervals())


@router.message(WaitUser.intervals)
async def not_intervals(message: types.Message):
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
    await callback_query.message.edit_text("👉 интервалы ≠ 0\n \n👉 интервалы - целые числа\n"
                                           "\n👉 интервалы не могут быть больше 100\n"
                                           "\nВведите ваши интервалы ↓", reply_markup=markup)

