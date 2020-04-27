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
# tiles
tile_size = 20
tiledir = join(dirname(__file__), '..', 'platform_tutorial', 'images', 'tiles')
tile = Image.open(join(tiledir, 'stoneMid.png')).resize((tile_size, tile_size))

def convert_maps():
    mapfiles = [f for f in listdir(mapdir) if isfile(join(mapdir, f)) and re.match(pattern, f)]
    for f in mapfiles:
        match = re.search(pattern, f)
        convert_map(join(mapdir, f), match.group(1))


def convert_map(file, level):
    im = Image.open(file).convert('RGB')
    width, height = im.size  # map are 54x96
    # Tiles are 128x128
    back = Image.new('RGBA', (width * tile_size, height * tile_size), (255, 255, 255, 0))
    ar = np.zeros((width, height))
    for y in range(height):
        for x in range(width):
            # y coordinate is reversed
            pix = im.getpixel((x, height - y - 1))
            if pix in conversion:
                code = conversion[pix]
                ar[x, y] = code
                if code == FLOOR_ROCK:
                    back.paste(tile, (x * tile_size, (height - y - 1) * tile_size))
            elif y == 0 or (0 < ar[x, y - 1] < 10):
                ar[x, y] = CHARGE_LOW  # low charge above naked floor
    # save map
    np.save(join(mapdir, 'map'+str(level)), ar)
    back.save(join(mapdir, 'background'+str(level)+'.png'))


if __name__ == '__main__':
    #convert_maps()
    convert_map(join(mapdir, 'map1.png'), 1)
