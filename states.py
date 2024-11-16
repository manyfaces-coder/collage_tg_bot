from aiogram.fsm.state import StatesGroup, State


class WaitImage(StatesGroup):
    user_image = State()  # Состояние ожидания изображения от пользователя
    #Нужно состояние для ожидания интервалов выход из которых только после их принятия

class WaitIntervals(StatesGroup):
    user_intervals = State()