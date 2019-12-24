# Screen
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650

# Physics
GRAVITY = 0.7

# Constants used to scale our sprites from their original size
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

TILE_PROP = 'Tag'


# Conversion from Tile per second to pixel per frame
def convert_speed_to_frame(velocity: float, delta_time: float):
    return velocity * GRID_PIXEL_SIZE * delta_time


# Conversion from pixel per frame to Tile per second
def convert_speed_to_timed(velocity: float, delta_time: float):
    return velocity / (GRID_PIXEL_SIZE * delta_time)
