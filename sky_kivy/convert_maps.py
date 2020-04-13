from PIL import Image
from os.path import isfile, join, dirname
from os import listdir
import re
import numpy as np


conversion = {
    (0, 0, 0): 1,  # wall in black
    (255, 0, 0): 2,  # charge in red
    (0, 255, 0): 3,  # win in green
}
mapdir = join(dirname(__file__), 'maps')
pattern = "^map(\\d+).png"


def convert_maps():
    mapfiles = [f for f in listdir(mapdir) if isfile(join(mapdir, f)) and re.match(pattern, f)]
    for f in mapfiles:
        match = re.search(pattern, f)
        convert_map(join(mapdir, f), match.group(1))


def convert_map(file, level):
    im = Image.open(file).convert('RGB')
    width, height = im.size
    ar = np.zeros((width, height))
    for y in range(height):
        for x in range(width):
            # y coordinate is reversed
            pix = im.getpixel((x, height - y - 1))
            if pix in conversion:
                ar[x, y] = conversion[pix]
    # save map
    np.save(join(mapdir, 'map'+str(level)), ar)


if __name__ == '__main__':
    convert_maps()
