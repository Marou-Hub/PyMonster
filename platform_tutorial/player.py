import arcade

CHARACTER_SCALING = 1


class Player(arcade.AnimatedWalkingSprite):
    def __init__(self, image_name, x, y):
        super().__init__(CHARACTER_SCALING)
        self.set(x, y)

        self.stand_right_textures = []
        self.stand_right_textures.append(arcade.load_texture(image_name + "/player_stand.png",
                                                                    scale=CHARACTER_SCALING))
        self.stand_left_textures = []
        self.stand_left_textures.append(arcade.load_texture(image_name + "/player_stand.png",
                                                                   scale=CHARACTER_SCALING, mirrored=True))

        self.walk_right_textures = []

        self.walk_right_textures.append(arcade.load_texture(image_name + "/player_walk1.png",
                                                                   scale=CHARACTER_SCALING))
        self.walk_right_textures.append(arcade.load_texture(image_name + "/player_walk2.png",
                                                                   scale=CHARACTER_SCALING))

        self.walk_left_textures = []

        self.walk_left_textures.append(arcade.load_texture(image_name + "/player_walk1.png",
                                                                  scale=CHARACTER_SCALING, mirrored=True))
        self.walk_left_textures.append(arcade.load_texture(image_name + "/player_walk2.png",
                                                                  scale=CHARACTER_SCALING, mirrored=True))
        self.texture_change_distance = 20

    def set(self, x, y):
        self.initial_x = x
        self.initial_y = y
        self.center_x = x
        self.center_y = y

    def reset(self):
        self.center_x = self.initial_x
        self.center_y = self.initial_y
        self.change_x = 0
        self.change_y = 0
        if self.initial_x < 100:
            self.state = arcade.FACE_RIGHT
        else:
            self.state = arcade.FACE_LEFT
