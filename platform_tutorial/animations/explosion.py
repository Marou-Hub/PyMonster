import os

import arcade

from platform_tutorial.animations.animated_sprite import AnimatedSprite, MODE_ONE_FORWARD

SCALING = 0.25


class Explosion(AnimatedSprite):
    def __init__(self, scale: float = SCALING,
                 image_x: float = 0, image_y: float = 0,
                 center_x: float = 0, center_y: float = 0):
        super().__init__(scale=scale, image_x=image_x, image_y=image_y, center_x=center_x, center_y=center_y)
        self.texture_change_frames = 1
        self.setup()

    def setup(self):
        textures = []
        for i in range(1, 44):
            texture_name = f"/images/explosion/Explosion {i:02d}.png"
            textures.append(arcade.load_texture(os.getcwd() + texture_name))
        self.start_animation(textures, MODE_ONE_FORWARD)

    def on_animation_end(self):
        super().on_animation_end()
        self.kill()
