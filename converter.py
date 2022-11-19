#!/bin/python

from PIL import Image
import argparse

gs_raw_filename=''
gs_include_header = "#include \"GuiLite.h\"\n";

def load_image(filename, target_width, target_height):
    """
    Loads an image, resized it to the target dimensions and returns it's data.
    """

    image = Image.open(filename, 'r')
    #print(image.size, "red", target_width, target_height)
    if (target_width and target_height):
        image = image.resize((target_width, target_height), Image.NEAREST)
    # 关键的是这个 image_data
    image_data = image.load()

    return image.size[0], image.size[1], image_data


def get_pixel_intensity(pixel, invert=False, max_value=255):
    """
    Gets the average intensity of a pixel.
    """
    intensity = 0

    # Pixel is multi channel
    if type(pixel) is list or type(pixel) is tuple:
        # 计算平均像素
        for channel_intensity in pixel:
            intensity += channel_intensity
        intensity /= len(pixel)
    # Pixel is single channel
    elif type(pixel) is int or type(pixel) is float:
        intensity = pixel
    # Pixel is magic
    else:
        raise ValueError('Not a clue what format the pixel data is: ' + str(type(pixel)))

    if invert:
        return max_value - intensity
    else:
        return intensity


def get_average_pixel_intensity(width, height, pixel_data, invert):
    """
    Gets the average intensity over all pixels.
    """

    avg_intensity = 0

    for x_idx in range(0, width):
        for y_idx in range(0, height):
            avg_intensity += get_pixel_intensity(pixel_data[x_idx, y_idx], invert)

    avg_intensity = avg_intensity / (width * height)

    return avg_intensity


def output_image_c_array(width, height, pixel_data, invert):
    """
    Outputs the data in a C bitmap array format.
    """

    print (gs_include_header)
    print ('static const unsigned short raw_data[] = {')

    for y_idx in range(0, height):
        next_line = ''
        next_value = 0
        rgb16_value = 0

        for x_idx in range(0, width):
            next_value = pixel_data[x_idx, y_idx]
            rgb16_value = (next_value[0] >> 3 << 11) | (next_value[1] >> 2 << 5) | (next_value[2] >> 3)
            rgb16_value = 0xffff - rgb16_value
            #print(next_value, type(next_value), rgb16_value, type(rgb16_value))
            next_line += str('0x%0.4X' % rgb16_value).lower() + ","

        print (next_line)

    print ('};')
    endline = 'extern const BITMAP_INFO ' + gs_raw_filename + ';\n'
    endline += 'const BITMAP_INFO ' + gs_raw_filename
    endline += ' = {\n'
    endline += '    ' + str(width) + ',\n'
    endline += '    ' + str(height) + ',\n'
    endline += '    ' + str(2) + ',\n' # 目前仅仅支持 16 bit显示
    endline += '    (unsigned short *)raw_data,\n};'
    print(endline)


def convert(params):
    """
    Runs an image conversion.
    """

    global gs_raw_filename
    # 获取文件的文件的名字（去除类型后缀）
    gs_raw_filename = params.image.split('/')[-1].split('.')[0]
    width, height, image_data = load_image(params.image, params.width, params.height)

    #if params.threshold == 0:
    #    crossover_intensity = get_average_pixel_intensity(width, height, image_data, params.invert)
    #else:
    #    crossover_intensity = params.threshold
    #print(crossover_intensity, "red rgb format")
    output_image_c_array(width, height, image_data, params.invert)


def run():
    """
    Gets parameters and runs conversion.
    """
    parser = argparse.ArgumentParser(description='Convert a bitmap image to a C array for GLCDs')

    parser.add_argument(
            '-i', '--invert',
            action='store_true',
            help='Invert image intensity')

    parser.add_argument(
            '--threshold',
            default=0,
            type=int,
            help='BW pixel intensity threshold')

    parser.add_argument(
            '--width',
            default=0,
            type=int,
            help='Width of the output image')

    parser.add_argument(
            '--height',
            default=0,
            type=int,
            help='Height of the output image')

    parser.add_argument(
            '-f', '--image',
            type=str,
            help='Image file to convert')

    params = parser.parse_args()
    convert(params)


if __name__ == '__main__':
    run()
