from PIL import Image
from os.path import isfile, join, dirname
from os import listdir
import re
import numpy as np

FLOOR_ROCK = 1
FLOOR_MUD = 2
FLOOR_ICE = 3
CHARGE = 50
CHARGE_LOW = 51
VICTORY = 100
START = 200
GOLD = 201

conversion = {
    (0, 0, 0): FLOOR_ROCK,  # horizontal rock floor in black
    (160, 115, 0): FLOOR_MUD,  # horizontal mud floor in brown
    (128, 128, 128): FLOOR_ICE,  # horizontal ice floor in grey
    (255, 0, 0): CHARGE,  # charge in red
    (0, 255, 0): VICTORY,  # win in green
    (0, 0, 255): START,  # start position in blue
    (255, 255, 0): GOLD,  # start position in yellow
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
            elif y == 0 or (0 < ar[x, y - 1] < 10):
                ar[x, y] = CHARGE_LOW  # low charge above naked floor
    # save map
    np.save(join(mapdir, 'map'+str(level)), ar)


if __name__ == '__main__':
    convert_maps()
