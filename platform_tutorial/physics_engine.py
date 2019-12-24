"""
Physics engines for top-down or platformers.
"""
from arcade import PhysicsEnginePlatformer
from arcade.sprite import Sprite
from arcade.sprite_list import SpriteList

from platform_tutorial.constants import convert_speed_to_frame, convert_speed_to_timed


class PhysicsEngine(PhysicsEnginePlatformer):
    """
    This class will move everything, and take care of collisions.
    """

    def __init__(self, player_sprite: Sprite, platforms: SpriteList, gravity_constant: float = 2,
                 ladders: SpriteList = None):
        """
        Constructor.
        """
        super().__init__(player_sprite, platforms, gravity_constant, ladders)

    def update(self, delta_time: float = 1/60):
        """
        Move everything and resolve collisions.
        """
        # Backup altered data
        backup_width = self.player_sprite.width
        backup_gravity = self.gravity_constant
        backup_change_x = self.player_sprite.change_x
        # Shrink player width for better collision
        self.player_sprite.width /= 2
        # Compute velocity from tile per second to pixel per frame
        self.gravity_constant = convert_speed_to_frame(self.gravity_constant, delta_time)
        self.player_sprite.change_x = convert_speed_to_frame(self.player_sprite.change_x, delta_time)
        self.player_sprite.change_y = convert_speed_to_frame(self.player_sprite.change_y, delta_time)

        # Standard (non timed) update
        super().update()

        # restore values
        self.player_sprite.width = backup_width
        self.gravity_constant = backup_gravity
        self.player_sprite.change_x = backup_change_x
        self.player_sprite.change_y = convert_speed_to_timed(self.player_sprite.change_y, delta_time)
