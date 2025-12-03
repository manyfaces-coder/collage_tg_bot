
# Используем базовый образ с Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем зависимости
COPY requirements.txt /app
# Устанавливаем
RUN pip install --no-cache-dir -r requirements.txt

## Копируем файлы проекта в контейнер
COPY . /app

# Указываем команду для запуска бота
CMD ["python", "aiogram_run.py"]