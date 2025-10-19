import redis.asyncio as redis  # Используем асинхронный Redis
import json
import logging


class RedisStorage:
    def __init__(
            self,
            redis_url: str|None = None,
            redis_host='localhost',
            redis_port=6379,
            redis_db=0,
            key_prefix: str = "bot",
    ):
        """Инициализация подключения к Redis."""
        self.key_prefix = key_prefix.rstrip(":")
        if redis_url:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
        else:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
            )
    # создание удобно читаемых ключей
    def _k(self, *parts: str) -> str:
        return ":".join((self.key_prefix, *parts))

    async def close(self) -> None:
        await self.redis_client.aclose()

    async def set_data(self, key: str, value, expire: int|None = None) -> None:
        """Сохранение данных в Redis."""
        value_json = json.dumps(value, ensure_ascii=False)  # Сериализуем в JSON
        await self.redis_client.set(key, value_json, ex=expire)

    async def get_data(self, key: str):
        """Получение данных из Redis."""
        try:
            value_json = await self.redis_client.get(key)
            if value_json:
                return json.loads(value_json)  # Десериализация из JSON
            return None
        except (json.JSONDecodeError, redis.RedisError):
            return None

    async def delete_data(self, key: str):
        """Удаление ключа из Redis."""
        await self.redis_client.delete(key)

    # async def is_flood(self, user_id: int, interval: int = 1) -> bool:
    async def is_flood(self, user_id: int, limit: int = 1, window_sec: int = 1) -> bool:

        """
        Проверяет, отправил ли пользователь сообщение слишком быстро.
        :return: True, если флуд, False, если нет
        Разрешаем не более `limit` событий за окно `window_sec`.
        Реализация: INCR + EXPIRE.
        """
        key = self._k("flood", f"user:{user_id}")
        try:
            cnt = await self.redis_client.incr(key)
            if cnt == 1:
                # Первый инкремент — ставим TTL на окно
                await self.redis_client.expire(key, window_sec)
            is_spam = cnt > limit
            if is_spam:
                logging.debug("Flood detected: user_id=%s count=%s", user_id, cnt)
            return is_spam
        except redis.RedisError:
            # В случае проблем с Redis не блокируем пользователя
            return False


    async def set_state(self, user_id: int, state: str, data: dict = None):
        """
        Устанавливает состояние пользователя.
        :param user_id: ID пользователя
        :param state: Название состояния
        :param data: Дополнительные данные
        """
        key = self._k("user_state", str(user_id))
        value = {"state": state, "data": data or {}}
        await self.set_data(key, value, expire=3600)  # TTL — 1 час

    async def get_state(self, user_id: int):
        key = self._k("user_state", str(user_id))
        return await self.get_data(key)

    async def reset_state(self, user_id: int):
        key = self._k("user_state", str(user_id))
        await self.delete_data(key)

