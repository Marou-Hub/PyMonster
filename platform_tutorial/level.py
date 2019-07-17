import arcade

# Name of the layer in the file that has our platforms/walls
from platform_tutorial.animations.enemy import generate_enemy
from platform_tutorial.constants import TILE_SCALING, GRID_PIXEL_SIZE, COIN_SCALING

platforms_layer_name = 'Platforms'
# Name of the layer that has items for pick-up
coins_layer_name = 'Coins'
# Name of the layer that has items for foreground
foreground_layer_name = 'Foreground'
# Name of the layer that has items for background
background_layer_name = 'Background'
# Name of the layer that has items we shouldn't touch
dont_touch_layer_name = "Don't Touch"
# Name of the layer that has items for doors
porte_layer_name = 'porte'
# Name of the layer that has items for enemies
enemy_layer_name = 'Enemies'
# Name of the layer that has items for enemy flags
flag_layer_name = 'Flags'
# Name of the layer that has items for player access
access_layer_name = 'Access'


class Level:
    def __init__(self):
        self.wall_list = None
        self.coin_list = None
        self.foreground_list = None
        self.background_list = None
        self.door_list = None
        self.dont_touch_list = None
        self.enemy_list = None
        self.flag_list = None
        self.access_list = None
        # Where is the right edge of the map?
        self.end_of_map = 0
        # Cut scenes
        self.cut_scene = None

    def setup(self, level):
        # Name of map file to load
        map_name = f"map2_level_{level}.tmx"
        # Read in the tiled map
        my_map = arcade.read_tiled_map(map_name, TILE_SCALING)

        # -- Walls
        # Grab the layer of items we can't move through
        map_array = my_map.layers_int_data[platforms_layer_name]

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = len(map_array[0]) * GRID_PIXEL_SIZE

        # -- Platforms
        self.wall_list = generate_sprites(my_map, platforms_layer_name, TILE_SCALING)

        # -- Coins
        self.coin_list = generate_sprites(my_map, coins_layer_name, COIN_SCALING)

        # -- Background
        self.background_list = generate_sprites(my_map, background_layer_name, TILE_SCALING)

        # -- Foreground
        self.foreground_list = generate_sprites(my_map, foreground_layer_name, TILE_SCALING)

        # -- Don't Touch Layer
        self.dont_touch_list = generate_sprites(my_map, dont_touch_layer_name, TILE_SCALING)

        # -- Doors Layer
        self.door_list = generate_sprites(my_map, porte_layer_name, TILE_SCALING)

        # -- Flag Layer
        self.flag_list = generate_sprites(my_map, flag_layer_name, TILE_SCALING)

        # -- Enemies Layer
        self.enemy_list = arcade.SpriteList()
        enemy_placeholders = generate_sprites(my_map, enemy_layer_name, TILE_SCALING)
        for ep in enemy_placeholders:
            enemy = generate_enemy(ep.filename, ep.position, self.flag_list)
            if enemy is not None:
                self.enemy_list.append(enemy)

        # -- Access Layer
        self.access_list = generate_sprites(my_map, access_layer_name, TILE_SCALING)
        for door in self.door_list:
            self.access_list.append(door)

        # --- Other stuff
        # Set the background color
        if my_map.backgroundcolor:
            arcade.set_background_color(my_map.backgroundcolor)

    def pre_draw(self):
        # Draw our sprites
        self.background_list.draw()
        self.wall_list.draw()
        self.door_list.draw()
        self.enemy_list.draw()

    def post_draw(self):
        # Draw our sprites
        self.coin_list.draw()
        self.dont_touch_list.draw()
        self.foreground_list.draw()

    def update_animation(self):
        self.dont_touch_list.update_animation()
        self.enemy_list.update_animation()


def generate_sprites(map_object: arcade.TiledMap, layer_name: str, scaling: float, base_directory="") -> arcade.SpriteList:
    """
    Generate the sprites for a layer in a map.

    :param TiledMap map_object: Map previously read in from read_tiled_map function
    :param layer_name: Name of the layer we want to generate sprites from. Case sensitive.
    :param scaling: Scaling factor.
    :param base_directory: Directory to read images from. Defaults to current directory.
    :return: List of sprites
    :rtype: SpriteList
    """
    sprite_list = arcade.SpriteList()

    if layer_name not in map_object.layers_int_data:
        print(f"Warning, no layer named '{layer_name}'.")
        return sprite_list

    map_array = map_object.layers_int_data[layer_name]

    # Loop through the layer and add in the wall list
    for row_index, row in enumerate(map_array):
        for column_index, item in enumerate(row):
            if str(item) in map_object.global_tile_set:
                tile_info = map_object.global_tile_set[str(item)]
                tmx_file = base_directory + tile_info.source

                my_sprite = arcade.Sprite(tmx_file, scaling)
                my_sprite.right = column_index * (map_object.tilewidth * scaling)
                my_sprite.top = (map_object.height - row_index) * (map_object.tileheight * scaling)
                # set filename to identify the tile
                my_sprite.filename = tmx_file

                if tile_info.points is not None:
                    my_sprite.set_points(tile_info.points)
                sprite_list.append(my_sprite)
            elif item != 0:
                print(f"Warning, could not find {item} image to load.")

    return sprite_list
