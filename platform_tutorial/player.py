import math
import arcade

CHARACTER_SCALING = 0.21

FACE_RIGHT = 1
FACE_LEFT = 2
JUMP_UP = 3
JUMP_DOWN = 4


class Player(arcade.Sprite):
    def __init__(self, image_name, x, y):
        super().__init__(scale=CHARACTER_SCALING)
        self.set(x, y)

        self.face = FACE_RIGHT
        self.jumping = False

        self.stand_right_textures = []
        self.stand_left_textures = []
        self.walk_right_textures = []
        self.walk_left_textures = []
        self.jump_up_right_textures = []
        self.jump_up_left_textures = []
        self.jump_down_right_textures = []
        self.jump_down_left_textures = []
        self.die_right_textures = []
        self.die_left_textures = []

        self.cur_texture_index = 0
        self.texture_change_distance = 20
        self.texture_change_frames = 5
        self.last_texture_change_center_x = 0
        self.last_texture_change_center_y = 0
        self.stand_frame = 0

        self.init_new(image_name)

    def update_animation(self, jumping: bool):
        """
        Logic for selecting the proper texture to use.
        """
        x1 = self.center_x
        x2 = self.last_texture_change_center_x
        y1 = self.center_y
        y2 = self.last_texture_change_center_y
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if self.jumping != jumping:
            self.cur_texture_index = 0
        texture_list = []

        change_direction = False
        if self.change_x > 0 \
                and self.change_y == 0 \
                and self.face != FACE_RIGHT \
                and self.walk_right_textures \
                and len(self.walk_right_textures) > 0:
            self.face = FACE_RIGHT
            change_direction = True
        elif self.change_x < 0 and self.change_y == 0 and self.face != FACE_LEFT \
                and self.walk_left_textures and len(self.walk_left_textures) > 0:
            self.face = FACE_LEFT
            change_direction = True

        if jumping:
            if not self.jumping:
                self.cur_texture_index = 0
            if self.face == FACE_LEFT:
                if self.change_y >= 0:
                    texture_list = self.jump_up_left_textures
                else:
                    texture_list = self.jump_down_left_textures
            elif self.face == FACE_RIGHT:
                if self.change_y >= 0:
                    texture_list = self.jump_up_right_textures
                else:
                    texture_list = self.jump_down_right_textures
            self.texture = texture_list[self.cur_texture_index]
            if self.cur_texture_index < len(texture_list) - 1:
                self.cur_texture_index += 1

        elif self.change_x == 0 and self.change_y == 0:
            if self.face == FACE_LEFT:
                texture_list = self.stand_left_textures
            elif self.face == FACE_RIGHT:
                texture_list = self.stand_right_textures
            if self.stand_frame % self.texture_change_frames == 0:
                self.cur_texture_index += 1
                if self.cur_texture_index >= len(texture_list):
                    self.cur_texture_index = 0
            self.texture = texture_list[self.cur_texture_index]
            self.stand_frame += 1

        elif change_direction or distance >= self.texture_change_distance:
            self.last_texture_change_center_x = self.center_x
            self.last_texture_change_center_y = self.center_y
            self.stand_frame = 0
            next_index = self.cur_texture_index

            if self.face == FACE_LEFT:
                texture_list = self.walk_left_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError("update_animation was called on a sprite that doesn't have a "
                                       "list of walk left textures.")
            elif self.face == FACE_RIGHT:
                texture_list = self.walk_right_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError("update_animation was called on a sprite that doesn't have a list of "
                                       "walk right textures.")
            next_index += 1
            if next_index >= len(texture_list):
                next_index = 0

            if self.cur_texture_index >= len(texture_list):
                self.cur_texture_index = 0
            self.texture = texture_list[self.cur_texture_index]
            self.cur_texture_index = next_index

        if self._texture is None:
            print("Error, no texture set")
        else:
            self.width = self._texture.width * self.scale
            self.height = self._texture.height * self.scale
        self.jumping = jumping

    def update_dying_animation(self, damager: arcade.Sprite = None):
        """
        Move toward damager and resolve gravity collisions.
        """
        self.stop()
        if damager:
            x1 = self.center_x
            x2 = damager.center_x
            nabs = int(math.fabs(x2-x1))
            if nabs > 5:
                self.center_x += (x2-x1) / nabs * 5
            else:
                self.center_x += x2

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

        for i in range(1, 5):
            texture_name = f"/Jump ({i}).png"
            self.jump_up_right_textures.append(arcade.load_texture(image_name + texture_name,
                                                                   scale=CHARACTER_SCALING))
            self.jump_up_left_textures.append(arcade.load_texture(image_name + texture_name,
                                                                  scale=CHARACTER_SCALING, mirrored=True))

        for i in range(6, 10):
            texture_name = f"/Jump ({i}).png"
            self.jump_down_right_textures.append(arcade.load_texture(image_name + texture_name,
                                                                     scale=CHARACTER_SCALING))
            self.jump_down_left_textures.append(arcade.load_texture(image_name + texture_name,
                                                                    scale=CHARACTER_SCALING, mirrored=True))

    def set(self, x, y):
        self.initial_x = x
        self.initial_y = y
        self.center_x = x
        self.center_y = y

    def reset(self):
        self.center_x = self.initial_x
        self.center_y = self.initial_y
        self.stop()
        if self.initial_x < 100:
            self.face = arcade.FACE_RIGHT
        else:
            self.face = arcade.FACE_LEFT
