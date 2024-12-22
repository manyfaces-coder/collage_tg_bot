from dataclasses import dataclass


class CollageException(Exception):

    def __str__(self):
        return "Исключение при передаче изображения пользователя в функцию обработки изображений"


    # def send_mesage_about_exeption(self):
    #     await bot.send_photo(chat_id=message.chat.id,
    #                          photo=types.FSInputFile(path='main_images/murzik.jpg'),
    #                          caption="Извините, произошла какая-то ошибка "
    #                                  "при оброботке фото, мой кот тоже не в "
    #                                  "восторге :(")

class VerticalIntervalException(Exception):
    def __str__(self):
        return "Нельзя разделить ваше фото на такое количество вертикальных интервалов\n" \
               "Попробуйте с числом поменьше"

class HorizontalIntervalException(Exception):
    def __str__(self):
        return f"Нельзя разделить ваше фото на такое количество горизонтальных интервалов\n" \
               f"Попробуйте с числом поменьше"


# @dataclass
# class VerticalIntervalException(Exception):
#     vertical_interval: int
#
#     def __repr__(self):
#         return f"Нельзя разделить ваше фото на такое количество вертикальных интервалов: {self.vertical_interval}\n" \
#                f"Попробуйте с числом поменьше"


# @dataclass
# class HorizontalIntervalException(Exception):
#     # horizontal_interval: int
#
#     def __repr__(self):
#         return f"Нельзя разделить ваше фото на такое количество горизонтальных интервалов\n" \
#                f"Попробуйте с числом поменьше"

