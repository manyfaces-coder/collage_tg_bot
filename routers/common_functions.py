import os
from aiogram import Router, types, Bot
from dotenv import load_dotenv, find_dotenv


from inline_keyboards import subscribe_inline_keyboard, main_inline_kb

load_dotenv(find_dotenv())
bot = Bot(token=os.getenv('TOKEN'))
router = Router(name=__name__)
channel_id = int(os.getenv('channel_id'))


async def check_sub(channel_id, user_id, chat_id):
    # Проверяем, подписан ли пользователь на канал
    is_subscribed = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)

    if is_subscribed.status == 'member' or is_subscribed.status == 'creator':
        return True
    else:
        markup = subscribe_inline_keyboard(user_id)
        await bot.send_message(chat_id=chat_id, text="Для доступа к Боту подпишитесь на канал "
                               , reply_markup=markup)


@router.message()
async def handle_unknown_message(message: types.Message):
    if await check_sub(channel_id, message.from_user.id, message.chat.id):
        # await message.answer(text="Чтобы создать коллаж, введите команду /start и нажмите на появившуюся кнопку")
        markup = main_inline_kb()
        await message.answer(text='Я не понимаю, что вы хотите, пожалуйста выберите действие', reply_markup=markup)
