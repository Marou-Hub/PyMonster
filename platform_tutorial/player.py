import arcade

CHARACTER_SCALING = 0.21


class Player(arcade.AnimatedWalkingSprite):
    def __init__(self, image_name, x, y):
        super().__init__(CHARACTER_SCALING)
        self.set(x, y)

        self.texture_change_distance = 20
        self.stand_right_textures = []
        self.stand_left_textures = []
        self.walk_right_textures = []
        self.walk_left_textures = []
        self.init_new(image_name)

    def init_old(self, image_name):
        self.stand_right_textures.append(arcade.load_texture(image_name + "/player_stand.png",
                                                                    scale=CHARACTER_SCALING))
        self.stand_left_textures.append(arcade.load_texture(image_name + "/player_stand.png",
                                                                   scale=CHARACTER_SCALING, mirrored=True))

        self.walk_right_textures.append(arcade.load_texture(image_name + "/player_walk1.png",
                                                                   scale=CHARACTER_SCALING))
        self.walk_right_textures.append(arcade.load_texture(image_name + "/player_walk2.png",
                                                                   scale=CHARACTER_SCALING))

        self.walk_left_textures.append(arcade.load_texture(image_name + "/player_walk1.png",
                                                                  scale=CHARACTER_SCALING, mirrored=True))
        self.walk_left_textures.append(arcade.load_texture(image_name + "/player_walk2.png",
                                                                  scale=CHARACTER_SCALING, mirrored=True))

    def init_new(self, image_name):
        for i in range(1, 10):
            texture_name = f"/Idle ({i}).png"
            self.stand_right_textures.append(arcade.load_texture(image_name + texture_name,
                                                                        scale=CHARACTER_SCALING))
            self.stand_left_textures.append(arcade.load_texture(image_name + texture_name,
                                                                       scale=CHARACTER_SCALING, mirrored=True))

        for i in range(1, 8):
            texture_name = f"/Run ({i}).png"
            self.walk_right_textures.append(arcade.load_texture(image_name + texture_name,
                                                                       scale=CHARACTER_SCALING))
            self.walk_left_textures.append(arcade.load_texture(image_name + texture_name,
                                                                      scale=CHARACTER_SCALING, mirrored=True))

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
