"""
Platformer Game
"""
import arcade

# Constants
from platform_tutorial.animations.explosion import Explosion
from platform_tutorial.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from platform_tutorial.cut_scene import GameOver
from platform_tutorial.player import Player
from platform_tutorial.road import Road, ACCESS_RIGHT, ACCESS_LEFT, ACCESS_DOOR
from platform_tutorial.viewport import Viewport

SCREEN_TITLE = "Platformer"


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.level = None
        # These are 'lists' that keep track of our sprites. Each sprite should
        self.bullet_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()

        # Separate variable that holds the player sprite
        self.player = Player("images/adventure_girl", None)

        # Used to keep track of our scrolling
        self.viewport = Viewport()

        # Keep track of the score
        self.score = 0

        # Placements
        self.near_door = False
        self.road = Road(self.viewport, self.player)

        # Cut scenes
        self._cut_scene = None

        # Load sounds
        self.collect_coin_sound = arcade.load_sound("sounds/coin1.wav")
        self.jump_sound = arcade.load_sound("sounds/jump1.wav")
        self.gun_sound = arcade.sound.load_sound("sounds/laser1.wav")
        self.hit_sound = arcade.sound.load_sound("sounds/explosion2.wav")

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        # Cheat codes
        self.no_damage = False

    def _get_cut_scene(self):
        if self._cut_scene:
            return self._cut_scene
        else:
            return self.level.cut_scene

    def _set_cut_scene(self, cs):
        if cs is not None:
            self._cut_scene = cs
        else:
            self._cut_scene = None
            self.level.cut_scene = None

    cut_scene = property(_get_cut_scene, _set_cut_scene)

    def setup(self, level, position, with_physics=True):
        """ Set up the game here. Call this function to restart the game. """
        # --- Load in a map from the tiled editor ---
        self.level = level

        # Set up the player, specifically placing it at these coordinates.
        self.player.set(position)

        # Create the 'physics engine'
        if with_physics:
            self.player.enable_physics(self.level.wall_list)

        self.update(0)

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        if self.level:
            self.level.pre_draw()
        self.bullet_list.draw()
        self.draw_players()
        self.explosions_list.draw()
        if self.level:
            self.level.post_draw()

        score_text = self.hud_console()
        self.viewport.draw_text(score_text, 10, 10, arcade.csscolor.WHITE, 18)

        if self.cut_scene:
            self.cut_scene.draw()

    def draw_players(self):
        self.player.draw()

    def hud_console(self):
        # Debug
        debug = ""
        # for fire in self.level.dont_touch_list:
        #     if type(fire) is Fire:
        #         debug = " frame " + str(fire.cur_texture_index)
        # Draw our score on the screen, scrolling it with the viewport
        return f"Score: {self.score} Position: {int(self.player.center_x)} {debug}"

    def on_key_press(self, key, modifiers):
        self.key_press(key, self.player)

    def key_press(self, key, player):
        """Called whenever a key is pressed. """
        if self.cut_scene:
            # skip cut scene if tab
            if key == arcade.key.TAB or key == arcade.key.E:
                self.cut_scene.skip()
            return

        if key == arcade.key.UP or key == arcade.key.SPACE:
            if player.jump():
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.LEFT or key == arcade.key.Q:
            player.move_left()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            player.move_right()
        elif key == arcade.key.E and self.near_door:
            self.enter_door()
        elif key == arcade.key.N:
            self.no_damage = not self.no_damage

    def on_key_release(self, key, modifiers):
        self.key_release(key, self.player)

    def key_release(self, key, player):
        """Called when the user releases a key. """
        if self.cut_scene:
            return

        if key == arcade.key.LEFT or key == arcade.key.Q:
            player.stop_move()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            player.stop_move()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.mouse_press(x, y, button, self.player)

    def mouse_press(self, x: float, y: float, button: int, player):
        if self.cut_scene:
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            if player.can_attack():
                self.bullet_list.append(player.start_attack_1())
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            if player.can_attack():
                self.bullet_list.append(player.start_attack_2())
                arcade.sound.play_sound(self.gun_sound)

    def update(self, delta_time):
        """ Movement and game logic """
        if self.cut_scene:
            if self.cut_scene.is_completed():
                self.cut_scene = None
            else:
                self.cut_scene.update(delta_time)
                self.level.update_animation()
                self.player.update_physics()

        else:
            # Call update physics
            self.player.update_physics()

            # Call update for player
            if self.level:
                self.level.update_animation()
                self.level.enemy_list.update_animation()

            self.explosions_list.update_animation()

            # Call update for player
            self.player.update_animation()

            # Update bullets
            self.bullet_list.update()
            for bullet in self.bullet_list:
                # Check this bullet to see if it hit a coin
                hit_list = arcade.check_for_collision_with_list(bullet, self.level.enemy_list)

                # If it did, get rid of the bullet
                if len(hit_list) > 0:
                    explosion = Explosion()
                    explosion.center_x = hit_list[0].center_x
                    explosion.center_y = hit_list[0].center_y
                    self.explosions_list.append(explosion)
                    bullet.kill()

                # For every enemy we hit, add to the score and remove the enemy
                for enemy in hit_list:
                    enemy.kill()
                    self.score += 1

                    # Hit Sound
                    arcade.sound.play_sound(self.hit_sound)
                if self.viewport.is_off_screen(bullet):
                    bullet.kill()
    
            # See if we hit any coins
            coin_hit_list = arcade.check_for_collision_with_list(self.player,
                                                                 self.level.coin_list)
    
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
            if not self.no_damage:
                damager_list = arcade.check_for_collision_with_list(self.player, self.level.dont_touch_list)
                if damager_list:
                    self.start_game_over(damager_list[0])
    
            # See if the user got to the end of the level
            if self.current_player.center_x >= self.level.end_of_map - 32:

                # Load the next level
                next_level, pos = self.road.next_level(ACCESS_RIGHT)
                self.setup(next_level, pos)
    
                # Set the camera to the start
                self.viewport.reset()

            if self.current_player.center_x <= 0:
                # Load the next level
                next_level, pos = self.road.next_level(ACCESS_LEFT)
                self.setup(next_level, pos)

                # Set the camera to the start
                self.viewport.reset()

            if arcade.check_for_collision_with_list(self.current_player, self.level.door_list):
                self.near_door = True
            else:
                self.near_door = False

            # --- Manage Scrolling ---
            self.viewport.update(self.current_player.left, self.current_player.right, self.current_player.top, self.current_player.bottom)

    def enter_door(self):
        # Load the next level
        next_level, pos = self.road.next_level(ACCESS_DOOR)
        self.setup(next_level, pos)

    def start_game_over(self, damager=None):
        self.cut_scene = GameOver(self.viewport, self.player, damager)
        self.cut_scene.start_animation()

    @property
    def current_player(self):
        return self.player


def main():
    """ Main method """
    window = MyGame()
    next_level, pos = window.road.next_level()
    window.setup(next_level, pos)

    arcade.run()


if __name__ == "__main__":
    main()
