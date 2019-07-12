import arcade

CHARACTER_SCALING = 1


class Player(arcade.Sprite):
    def __init__(self, image_name, x, y):
        super().__init__(image_name, CHARACTER_SCALING)
        self.center_x = x
        self.center_y = y
