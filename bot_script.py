import asyncio
import logging
import os
from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher

from routers import router as main_router


async def main():
    load_dotenv(find_dotenv())
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_router(main_router)

    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
