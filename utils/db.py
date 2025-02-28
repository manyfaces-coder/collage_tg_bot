import asyncpg
import os

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "bot_db")
DB_USER = os.getenv("POSTGRES_USER", "bot_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "bot_password")

async def get_db_pool():
    """Создает пул соединений с PostgreSQL"""
    return await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT
    )


async def initialize_database(pool):
    """Создает таблицы, если их нет"""
    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                bot_open BOOLEAN DEFAULT FALSE
                )
            """)


async def add_user(pool, telegram_id:int, username: str, first_name: str):
    """Добавление польщователя в БД"""
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (telegram_id, username, first_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id) DO NOTHING
            """, telegram_id, username, first_name
        )


async def get_all_users(pool):
    """Получает всех пользователей из базы данных"""
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM users")
        users = [
            {
                'telegram_id': row['telegram_id'],
                'username': row['username'],
                'first_name': row['first_name'],
                'bot_open': row['bot_open']
            }
            for row in rows
        ]
        return users



async def get_user_by_id(pool, telegram_id: int):
    """Возвращает пользователя по ID"""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
        return dict(row) if row else None


async def update_bot_open_status(pool, telegram_id: int, bot_open: bool):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE users
            SET bot_open = $1
            WHERE telegram_id = $2
            """, bot_open, telegram_id
        )

