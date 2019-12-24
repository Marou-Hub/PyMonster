import os

import arcade

from platform_tutorial.animations.animated_sprite import AnimatedSprite, MODE_CYCLE_BACKWARD

SCALING = 0.25


class Fire(AnimatedSprite):
    def __init__(self, center_x: float = 0, center_y: float = 0):
        super().__init__(scale=SCALING, center_x=center_x, center_y=center_y+26, texture_change_time=0.2)
        self.setup()

    def setup(self):
        textures = []
        for i in range(10, 30):
            texture_name = f"/images/fire/Fire {i:d}.png"
            textures.append(arcade.load_texture(os.getcwd() + texture_name))
        self.start_animation(textures, MODE_CYCLE_BACKWARD)
