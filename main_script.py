import PIL
from PIL import Image
import os.path

#
# # from itertools import product
#
INTERVAL = 32


def open_orig_pic(path_to_pic):
    os.path.normpath(path_to_pic)
    # image = Image.open('original_image/1.jpg')
    # image = Image.open(path_to_pic)
    return Image.open(path_to_pic)


def scale_image(image):
    print(image.size)
    h, v = image.size
    print(h, v)
    # s_o_image = image.resize((int(h/4), int(v/4)), Image.LANCZOS)
    # return image.resize((int(h / 4), int(v / 4)), Image.LANCZOS, optimize=True, quality=95)
    return image.resize((int(h / 4), int(v / 4)), Image.LANCZOS)


#
# foo.save('image_scaled.jpg', quality=95)  # The saved downsized image size is 24.8kb
#
# foo.save('image_scaled_opt.jpg', optimize=True, quality=95)  # The saved downsized image size is 22.9kb
def create_mirror_collage(image_1):
    # image_1 = Image.open('image_scaled_opt.jpg')

    # out = image_1.transpose(PIL.Image.FLIP_LEFT_RIGHT)
    image_2 = image_1.transpose(PIL.Image.FLIP_LEFT_RIGHT)
    # out.save('collage_picture/2.png')

    image_3 = image_1.transpose(PIL.Image.FLIP_TOP_BOTTOM)
    # out_1.save('collage_picture/3.png')

    image_4 = image_3.transpose(PIL.Image.FLIP_LEFT_RIGHT)
    # out_2.save('collage_picture/4.png')
    # image.show()

    img_01_size = image_1.size
    mirror_collage = Image.new('RGB', (2 * img_01_size[0], 2 * img_01_size[1]), (250, 250, 250))

    mirror_collage.paste(image_1, (0, 0))
    mirror_collage.paste(image_2, (img_01_size[0], 0))
    mirror_collage.paste(image_3, (0, img_01_size[1]))
    mirror_collage.paste(image_4, (img_01_size[0], img_01_size[1]))

    # mirror_collage.save("p/mirror_collage.png", "PNG")
    # new_im = Image.open('merged_images.png')
    return mirror_collage


# new_im.show()
#

def cutting_vertically(image, interval=32):
    w, h = image.size

    # grid = product(range(0, h - h % d, d), range(0, w - w % d, d))
    # interval = 32  # глобальная переменная
    print("СЮДА")
    print(w - w % interval)
    print(int(w / interval))
    step_horizontal = range(0, w - w % interval, int(w / interval))
    print(step_horizontal)
    num_column = 0
    list_columns = []
    end_column = 0
    for i in step_horizontal:
        # print(num_column)
        print(i)
        end_column = i + int(w / interval)
        print(end_column)
        column = image.crop((i, 0, end_column, h))
        # column.save(f'columns/column_{num_column}.png')
        list_columns.append(column)

        # list_columns.append()
        num_column += 1

    print(list_columns)

    return list_columns, w, h
      # В СПИСКЕ ДОЛЖНО БЫТЬ ЧЕТНОЕ ЧИСЛО ТО ЕСТЬ 31 ЭЛЕМЕНТ И ПОСЛЕДНИЙ НУЖНО ПРОСТО СТАВИТЬ В КОНЕЦ

def sew_columns(list_columns, w, h, interval):

    new_collage = Image.new('RGB', (w - w % interval, h), (250, 250, 250))
    x = int(w / interval)
    start = 0
    print("P")
    print(
        len(list_columns))
    for i in range(0, int(len(list_columns) / 2)):
        new_collage.paste(list_columns[0], (start, 0))
        end_column = start + x
        new_collage.paste(list_columns[(len(list_columns) - 1)], (end_column, 0))
        list_columns.pop(0)
        list_columns.pop()
        start = end_column + x
        print(end_column)
        print(len(list_columns))

    # new_collage.save("p/pre_final.png", "PNG")
    print(list_columns)
    return new_collage


def cutting_horizontal(image, interval=32):
    # interval = 57

    # pre_final = Image.open('pre_final.png')
    # new_im.show()

    w, h = image.size
    print(w, h)
    # interval = int(w/32)
    # interval = 30
    print(f'INTERVAL = {interval}')
    step_vertical = range(0, h - h % interval, int(h / interval))
    print(step_vertical)
    num_row = 0
    list_rows = []
    # end_row = 0
    for i in step_vertical:
        # print(num_column)
        print(i)
        end_row = i + int(h / interval)
        print(end_row)
        row = image.crop((0, i, w, end_row))
        # row.save(f'rows/column_{num_row}.png')
        list_rows.append(row)

        # list_columns.append()
        num_row += 1

    print(list_rows)
    return list_rows, w, h

def sew_rows(list_rows, w, h, interval):

    new_collage = Image.new('RGB', (w, h - h % interval), (250, 250, 250))
    y = int(h / interval)
    start = 0
    # print("P")
    # print(len(list_rows))
    for i in range(0, int(len(list_rows) / 2)):
        new_collage.paste(list_rows[0], (0, start))
        # new_collage.paste(list_columns[0], (start, 0))
        end_row = start + y
        # new_collage.paste(list_rows[(len(list_columns) - 1)], (end_column, 0))
        new_collage.paste(list_rows[(len(list_rows) - 1)], (0, end_row))
        list_rows.pop(0)
        list_rows.pop()
        start = end_row + y
        print(end_row)
        # print(len(list_rows))

    return new_collage


# new_collage.save("final.png", "PNG")
# print(list_columns)
def start(vertical_interval, horizontal_interval):
    scaled_image = scale_image(open_orig_pic('original_image/1.jpg'))
    mirror_collage = create_mirror_collage(scaled_image)
    columns_list, w, h = cutting_vertically(mirror_collage, interval=vertical_interval)
    pre_final_image = sew_columns(columns_list, w, h, vertical_interval)
    row_list, w, h = cutting_horizontal(pre_final_image, interval=horizontal_interval)
    final_collage = sew_rows(row_list, w, h, horizontal_interval)
    final_collage.save("final/final_collage.png", "PNG", optimize=True)
    print("КОНЕЦ")

if __name__ == "__main__":
    print("start")
    start(vertical_interval=32, horizontal_interval=32)
    # final_collage = cutting_horizontal(sew_columns(
    #     cutting_vertically(
    #         create_mirror_collage(
    #             scale_image(
    #                 open_orig_pic('original_image/1.jpg'))), interval=40)), interval=40)
    # final_collage.save("final_collage.png", "PNG", optimize=True)
