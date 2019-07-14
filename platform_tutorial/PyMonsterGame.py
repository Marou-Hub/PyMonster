"""
Platformer Game
"""
import arcade

# Constants
from platform_tutorial.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from platform_tutorial.physics_engine import PhysicsEngine
from platform_tutorial.road import Road
from platform_tutorial.viewport import Viewport
from platform_tutorial.player import Player

SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.coin_list = None
        self.wall_list = None
        self.foreground_list = None
        self.background_list = None
        self.dont_touch_list = None
        self.porte_list = None

        # Separate variable that holds the player sprite
        self.player = None

        # Our physics engine
        self.physics_engine = None

        # Used to keep track of our scrolling
        self.viewport = None

        # Keep track of the score
        self.score = 0

        # Damage
        self.damager_forward = None

        # Where is the right edge of the map?
        self.end_of_map = 0
        self.game_over_count_down: float = 0
        self.near_door = False
        self.road = Road()

        # Load sounds
        self.collect_coin_sound = arcade.load_sound("sounds/coin1.wav")
        self.jump_sound = arcade.load_sound("sounds/jump1.wav")
        self.game_over = arcade.load_sound("sounds/gameover1.wav")

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self, level, pos_x, pos_y):
        """ Set up the game here. Call this function to restart the game. """
        self.road.current_level = level

        # Used to keep track of our scrolling
        self.viewport = Viewport()

        # Create the Sprite lists
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.porte_list = arcade.SpriteList()

        # Set up the player, specifically placing it at these coordinates.
        if self.player:
            self.player.set(pos_x, pos_y)
        else:
            self.player = Player("images/adventure_girl", pos_x, pos_y)

        # --- Load in a map from the tiled editor ---

        # Name of map file to load
        map_name = f"map2_level_{level}.tmx"
        # Name of the layer in the file that has our platforms/walls
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

        # Read in the tiled map
        my_map = arcade.read_tiled_map(map_name, TILE_SCALING)

        # -- Walls
        # Grab the layer of items we can't move through
        map_array = my_map.layers_int_data[platforms_layer_name]

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = len(map_array[0]) * GRID_PIXEL_SIZE

        # -- Platforms
        self.wall_list = arcade.generate_sprites(my_map, platforms_layer_name, TILE_SCALING)

        # -- Coins
        self.coin_list = arcade.generate_sprites(my_map, coins_layer_name, TILE_SCALING)

        # -- Background
        self.background_list = arcade.generate_sprites(my_map, background_layer_name, TILE_SCALING)

        # -- Foreground
        self.foreground_list = arcade.generate_sprites(my_map, foreground_layer_name, TILE_SCALING)

        # -- Don't Touch Layer
        self.dont_touch_list = arcade.generate_sprites(my_map, dont_touch_layer_name, TILE_SCALING)

        # -- Doors Layer
        self.porte_list = arcade.generate_sprites(my_map, porte_layer_name, TILE_SCALING)

        # --- Other stuff
        # Set the background color
        if my_map.backgroundcolor:
            arcade.set_background_color(my_map.backgroundcolor)

        # Create the 'physics engine'
        self.physics_engine = PhysicsEngine(self.player, self.wall_list, GRAVITY)
        self.physics_engine.enable_multi_jump(1)

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        self.background_list.draw()
        self.wall_list.draw()
        self.porte_list.draw()
        self.player.draw()
        self.coin_list.draw()
        self.dont_touch_list.draw()
        self.foreground_list.draw()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score} Position: {int(self.player.center_x)}"
        self.viewport.draw_text(score_text, 10, 10, arcade.csscolor.WHITE, 18)

        if self.game_over_count_down:
            self.viewport.shade()
            self.viewport.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.csscolor.WHITE, 50, anchor_x="center", anchor_y="center")

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.physics_engine.jump(PLAYER_JUMP_SPEED)
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.LEFT or key == arcade.key.Q:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.E and self.near_door:
            self.enter_door()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.LEFT or key == arcade.key.Q:
            self.player.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = 0

    def update(self, delta_time):
        """ Movement and game logic """
        if self.game_over_count_down > 0:
            self.game_over_count_down -= delta_time
            if self.game_over_count_down <= 0:
                self.end_game_over()
            else:
                self.player.update_dying_animation(self.damager_forward)
                self.physics_engine.update()

        else:
            # Call update physics
            self.physics_engine.update()

            # Call update for player
            self.player.update_animation(self.physics_engine.jumps_since_ground > 0)
    
            # See if we hit any coins
            coin_hit_list = arcade.check_for_collision_with_list(self.player,
                                                                 self.coin_list)
    
            # Loop through each coin we hit (if any) and remove it
            for coin in coin_hit_list:
                # Remove the coin
                coin.remove_from_sprite_lists()
                # Play a sound
                arcade.play_sound(self.collect_coin_sound)
                # Add one to the score
                self.score += 1
    
            # Did the player fall off the map?
            if self.player.center_y < -100:
                self.start_game_over()
                    
            # Did the player touch something they should not?
            damager_list = arcade.check_for_collision_with_list(self.player, self.dont_touch_list)
            if damager_list:
                self.damager_forward = damager_list[0]
                self.start_game_over()
    
            # See if the user got to the end of the level
            if self.player.center_x >= self.end_of_map - 32:

                # Load the next level
                next_level, pos_x, pos_y = self.road.exit_right()
                self.setup(next_level, pos_x, pos_y)
    
                # Set the camera to the start
                self.viewport.reset()

            if self.player.center_x <= 0:
                # Load the next level
                next_level, pos_x, pos_y = self.road.exit_left()
                self.setup(next_level, pos_x, pos_y)

                # Set the camera to the start
                self.viewport.reset()

            if arcade.check_for_collision_with_list(self.player, self.porte_list):
                self.near_door = True
            else:
                self.near_door = False

            # --- Manage Scrolling ---
            self.viewport.update(self.player.left, self.player.right, self.player.top, self.player.bottom)

    def enter_door(self):
        # Load the next level
        next_level, pos_x, pos_y = self.road.exit_door()
        self.setup(next_level, pos_x, pos_y)

    def start_game_over(self):
        arcade.play_sound(self.game_over)
        self.game_over_count_down = 2
        self.player.start_dying_animation()
    
    def end_game_over(self):
        self.game_over_count_down = 0
        self.player.reset()
        self.viewport.reset()
        self.damager_forward = None


def main():
    """ Main method """
    window = MyGame()
    window.setup(1, 64, 96)
    arcade.run()


if __name__ == "__main__":
    main()
