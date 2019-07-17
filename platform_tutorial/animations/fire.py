import os

import arcade

from platform_tutorial.animations.animated_sprite import AnimatedSprite, MODE_CYCLE_PONG

SCALING = 0.25


class Fire(AnimatedSprite):
    def __init__(self, scale: float = SCALING,
                 image_x: float = 0, image_y: float = 0,
                 center_x: float = 0, center_y: float = 0):

        super().__init__(scale=scale, image_x=image_x, image_y=image_y, center_x=center_x, center_y=center_y)
        self.setup()

    def setup(self):
        textures = []
        for i in range(8, 15):
            texture_name = f"/images/explosion/Explosion {i:02d}.png"
            textures.append(arcade.load_texture(os.getcwd() + texture_name))
        self.start_animation(textures, MODE_CYCLE_PONG)
