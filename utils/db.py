import aiosqlite


async def initialize_database():
    # Подключаемся к базе данных (если база данных не существует, она будет создана)
    async with aiosqlite.connect("bot.db") as db:
        # Создаем таблицу users, если она не существует
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                bot_open BOOLEAN DEFAULT FALSE 
            )
        """)
        # bot_open доступен ли бот для пользователя
        # Сохраняем изменения
        await db.commit()


# добавление пользователя в базу данных
async def add_user(telegram_id: int, username: str, first_name: str):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("""
        INSERT INTO users (telegram_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_id) DO NOTHING
        """, (telegram_id, username, first_name))
        await db.commit()


# получениe всех пользователей с базы данных
async def get_all_users():
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT * FROM users")
        rows = await cursor.fetchall()

        # Преобразование результата в список словарей
        users = [
            {
                'telegram_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'bot_open': row[3]
            }
            for row in rows
        ]
        return users


# получениe одного пользователя по его ID
# функция возвращает или None, если пользователя нет или словарь с данными по
# пользователю, если он есть в базе данных.
async def get_user_by_id(telegram_id: int):
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cursor.fetchone()

        if row is None:
            return None

        # Преобразование результата в словарь
        user = {
            "telegram_id": row[0],
            "username": row[1],
            "first_name": row[2],
            "bot_open": row[3]
        }
        return user


# функция для изменения статуса bot_open
async def update_bot_open_status(telegram_id: int, bot_open: bool):
    print(f"UPDATE_BOT_OPEN_STATUS – {bot_open}")
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("""
            UPDATE users
            SET bot_open = ?
            WHERE telegram_id = ?
        """, (bot_open, telegram_id))
        await db.commit()
