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
from bot_script_webhook import bot
from routers.common_functions import check_sub

from states import WaitUser
from bot_exceptions import CollageException, VerticalIntervalException, HorizontalIntervalException

router = Router(name=__name__)

pattern = r".*?(?!0)(\d+)(?!\d).+?(?!0)(\d+).*"


@router.callback_query(F.data == "start_make_collage")
async def request_image(callback_query: types.CallbackQuery, state: FSMContext):
    """Ожидание изображения от пользователя в состоянии"""
    if await check_sub(callback_query.message, callback_query.from_user.id):
        # Перевод пользователя в состояние ожидания изображения
        await state.set_state(WaitUser.user_image)
        # Добавление кнопки "Отмена" вместо предыдущего сообщения.
        buider = InlineKeyboardBuilder()
        buider.button(text='Отмена', callback_data='cancel_image')
        markup = buider.as_markup()
        await callback_query.message.edit_text("Пожалуйста, отправьте изображение.", reply_markup=markup)


@router.message(F.photo, WaitUser.user_image)
async def expected_image_received(message: types.Message, state: FSMContext):
    """Обработчик получения изображения в состоянии ожидании изображения"""
    await state.update_data(user_mes=message)
    await state.update_data(user_image=message.photo)
    await state.set_state(WaitUser.use_intervals)
    await message.reply(
        text="Выберите, как хотите сделать коллаж:", reply_markup=ways_collages())


@router.message(F.photo)
async def image_received(message: types.Message, state: FSMContext):
    if await check_sub(message):
        await state.update_data(user_mes=message)
        await state.update_data(user_image=message.photo)
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
    """Основная функция обработки коллажа."""
    start_time = time.time()

    message = data['user_mes']
    file_id = data['user_image'][-1].file_id
    await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")

    try:
        # Загрузка фото
        photo, tmp_dir = await download_photo(file_id)
        # Обработка фото
        result_file_path = main_script.start_for_bot(vertical_interval, horizontal_interval, file_path=photo)
        # Отправка результата
        agenda = FSInputFile(result_file_path)
        await bot.send_photo(message.chat.id, agenda)
        os.remove(result_file_path)
        await message.reply("Изображение обработанно!\n\nЧто дальше?", reply_markup=main_inline_kb())

    except CollageException:
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
    finally:
        tmp_dir.cleanup()

    print("--- %s seconds ---" % (time.time() - start_time))



# Обработчик нажатия на кнопку "Отмена" когда ждем изображение от пользователя
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
    await state.update_data(agree_intervals=True)
    data = await state.get_data()
    await state.clear()
    await make_collage(data, vertical_interval=int(data["intervals"][0]), horizontal_interval=int(data["intervals"][1]))


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
                                           "\nЖду ваших интервалов ↓", reply_markup=markup)


@router.callback_query(F.data.in_({"intervals_accepted", "reassign_intervals", "cancel_image"}))
async def intervals_accepted(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('Произошла ошибка, попробуйте сначала')

