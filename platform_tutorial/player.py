import arcade

CHARACTER_SCALING = 1


class Player(arcade.Sprite):
    def __init__(self, image_name, x, y):
        super().__init__(image_name, CHARACTER_SCALING)
        self.initial_x = x
        self.initial_y = y
        self.center_x = x
        self.center_y = y

    def reset(self):
        self.center_x = self.initial_x
        self.center_y = self.initial_y
