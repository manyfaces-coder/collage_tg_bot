import logging
import os

from aiogram.types import BotCommand, BotCommandScopeDefault
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from bot_script_webhook import bot, dp, BASE_URL, WEBHOOK_PATH, HOST, PORT, ADMIN_ID
from routers import router
from utils.db import initialize_database, get_db_pool
import shutil
import socket
import asyncio

SERVERS = (os.getenv("SERVERS").replace(" ", "")).split(',')

# Функция для установки командного меню для бота
async def set_commands():
    # Создаем список команд, которые будут доступны пользователям
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='help', description='Помощь')]
    # Устанавливаем эти команды как дефолтные для всех пользователей
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# Функция, которая будет вызвана при запуске бота
async def on_startup() -> None:
    global pool  # Делаем pool глобальным, чтобы использовать его в других функциях
    # Устанавливаем командное меню
    await set_commands()

    # Создаем базу данных и таблицу с пользователями, если таблицы не было
    pool = await get_db_pool()  # Создаем пул соединений
    await initialize_database(pool)  # Передаем pool в initialize_database()

    # Устанавливаем вебхук для приема сообщений через заданный URL
    await bot.set_webhook(f"{BASE_URL}{WEBHOOK_PATH}")

    # Отправляем сообщение администратору о том, что бот был запущен
    await bot.send_message(chat_id=ADMIN_ID, text='Бот запущен!')


async def is_any_server_alive():
    """ Проверяем, доступны ли другие серверы в сети. """
    for server in SERVERS:
        try:
            reader, writer = await asyncio.open_connection(server, 8080)
            writer.close()
            await writer.wait_closed()
            print(f"✅ Сервер {server} доступен")
            return True
        except Exception:
            print(f"❌ Сервер {server} недоступен.")

    await bot.send_message(chat_id=ADMIN_ID, text='⚠️ Ни один сервер не отвечает. Вебхуки удалены.')
    return False


# Функция, которая будет вызвана при остановке бота
async def on_shutdown() -> None:

    # Отправляем сообщение администратору о том, что бот был остановлен
    # await bot.send_message(chat_id=ADMIN_ID, text='Бот остановлен!')
    # Удаляем вебхук и, при необходимости, очищаем ожидающие обновления
    # await bot.delete_webhook(drop_pending_updates=True)
    if await is_any_server_alive():
        print("🔄 Есть работающие серверы, не удаляем вебхук.")
    else:
        print("🛑 Все серверы выключены, удаляем вебхук!")
        await bot.delete_webhook(drop_pending_updates=True)
    # await db_backup()
    await bot.send_message(chat_id=ADMIN_ID, text=f'Бот {socket.gethostname()} остановлен!')
    # Закрываем сессию бота, освобождая ресурсы
    await bot.session.close()
    # Очищаем папку с готовыми изображениями
    shutil.rmtree('final', ignore_errors=True)
    os.makedirs('final', exist_ok=True)


# Основная функция, которая запускает приложение
def main() -> None:
    # Подключаем маршрутизатор (роутер) для обработки сообщений
    dp.include_router(router)

    # Регистрируем функцию, которая будет вызвана при старте бота
    dp.startup.register(on_startup)

    # Регистрируем функцию, которая будет вызвана при остановке бота
    dp.shutdown.register(on_shutdown)

    # Создаем веб-приложение на базе aiohttp
    app = web.Application()

    # Настраиваем обработчик запросов для работы с вебхуком
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,  # Передаем диспетчер
        bot=bot  # Передаем объект бота
    )
    # Регистрируем обработчик запросов на определенном пути
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Настраиваем приложение и связываем его с диспетчером и ботом
    setup_application(app, dp, bot=bot)

    # Запускаем веб-сервер на указанном хосте и порте
    web.run_app(app, host=HOST, port=PORT)


# Точка входа в программу
if __name__ == "__main__":
    # Настраиваем логирование (информация, предупреждения, ошибки) и выводим их в консоль
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)  # Создаем логгер для использования в других частях программы
    main()  # Запускаем основную функцию