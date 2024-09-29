import asyncio
import logging
import os
from re import Match

from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher, types, F, Router
from magic_filter import RegexpMode

from routers import router as main_router
from routers.photo_handlers import router

# load_dotenv(find_dotenv())
# bot = Bot(token=os.getenv('TOKEN'))
#
# dp = Dispatcher()
# dp.include_router(main_router)
# another_media = F.video | F.document | F.audio
# image_received = None


async def main():
    load_dotenv(find_dotenv())
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_router(main_router)

    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
