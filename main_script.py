import PIL
from PIL import Image
import os.path


def check_intervals(vertical_interval, horizontal_interval):
    # if type(interval) == float:
    #     interval = int(interval)
    # if interval % 2 != 2:
    #     interval -= 1
    return vertical_interval, horizontal_interval


def open_orig_pic(path_to_pic):
    os.path.normpath(path_to_pic)
    return Image.open(path_to_pic)


def scale_image(image):
    h, v = image.size
    return image.resize((int(h / 4), int(v / 4)), Image.LANCZOS)


def create_mirror_collage(image_1):
    # get the image at the upper right corner
    image_2 = image_1.transpose(PIL.Image.FLIP_LEFT_RIGHT)

    # get the image in the lower left corner
    image_3 = image_1.transpose(PIL.Image.FLIP_TOP_BOTTOM)

    # get the image at the lower right corner
    image_4 = image_3.transpose(PIL.Image.FLIP_LEFT_RIGHT)

    image_1_size = image_1.size
    mirror_collage = Image.new('RGB', (2 * image_1_size[0], 2 * image_1_size[1]), (250, 250, 250))

    mirror_collage.paste(image_1, (0, 0))
    mirror_collage.paste(image_2, (image_1_size[0], 0))
    mirror_collage.paste(image_3, (0, image_1_size[1]))
    mirror_collage.paste(image_4, (image_1_size[0], image_1_size[1]))
    return mirror_collage


def cutting_vertically(image, interval=32):
    w, h = image.size
    try:
        step_horizontal = range(0, w - w % interval, int(w / interval))
    except:
        print("The interval is impossible")
        raise
    list_columns = []
    for i in step_horizontal:
        end_column = i + int(w / interval)
        column = image.crop((i, 0, end_column, h))
        list_columns.append(column)
    return list_columns, w, h


def sew_columns(list_columns, w, h, interval):
    new_collage = Image.new('RGB', (w - w % interval, h), (250, 250, 250))
    x = int(w / interval)
    first_pixel_column = 0
    for i in range(0, int(len(list_columns) / 2)):
        new_collage.paste(list_columns[0], (first_pixel_column, 0))
        end_column = first_pixel_column + x
        new_collage.paste(list_columns[(len(list_columns) - 1)], (end_column, 0))
        list_columns.pop(0)
        list_columns.pop()
        first_pixel_column = end_column + x
    return new_collage


def cutting_horizontal(image, interval=32):
    w, h = image.size
    try:
        step_vertical = range(0, h - h % interval, int(h / interval))
    except:
        print("The interval is impossible")
        raise
    list_rows = []
    for i in step_vertical:
        end_row = i + int(h / interval)
        row = image.crop((0, i, w, end_row))
        list_rows.append(row)
    return list_rows, w, h


def sew_rows(list_rows, w, h, interval):
    new_collage = Image.new('RGB', (w, h - h % interval), (250, 250, 250))
    y = int(h / interval)
    first_pixel_row = 0
    for i in range(0, int(len(list_rows) / 2)):
        new_collage.paste(list_rows[0], (0, first_pixel_row))
        end_row = first_pixel_row + y
        new_collage.paste(list_rows[(len(list_rows) - 1)], (0, end_row))
        list_rows.pop(0)
        list_rows.pop()
        first_pixel_row = end_row + y
    return new_collage


def start(vertical_interval=30, horizontal_interval=30, file_path='original_image/1.jpg'):
    print("PRILETELI")
    scaled_image = scale_image(open_orig_pic(file_path))
    mirror_collage = create_mirror_collage(scaled_image)
    columns_list, w, h = cutting_vertically(mirror_collage, interval=vertical_interval)
    pre_final_image = sew_columns(columns_list, w, h, vertical_interval)
    row_list, w, h = cutting_horizontal(pre_final_image, interval=horizontal_interval)
    final_collage = sew_rows(row_list, w, h, horizontal_interval)
    final_collage.save("final/final_collage.png", "PNG", optimize=True)
    return "final/final_collage.png"


if __name__ == "__main__":
    print("start")
    start(vertical_interval=30, horizontal_interval=30)


