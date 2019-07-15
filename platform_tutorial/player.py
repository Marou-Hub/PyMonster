import math
import arcade

CHARACTER_SCALING = 0.21
LASER_SCALING = 0.8

BULLET_SPEED = 5

ATTACK_DECAY = 10

FACE_RIGHT = 1
FACE_LEFT = 2
MOVING = 1
ATTACK = 2
DYING = 3


class Player(arcade.Sprite):
    def __init__(self, image_name, position):
        super().__init__(scale=CHARACTER_SCALING)
        self.set(position)

        self.status = MOVING
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
        self.attack_1_right_textures = []
        self.attack_1_left_textures = []
        self.attack_2_right_textures = []
        self.attack_2_left_textures = []

        self.cur_texture_index = 0
        self.texture_change_distance = 20
        self.texture_change_frames = 5
        self.last_texture_change_center_x = 0
        self.last_texture_change_center_y = 0
        self.stand_frame = 0

        self.init_new(image_name)

    def update_animation(self, jumping: bool):
        if self.status == ATTACK:
            self.update_attack_animation()
        else:
            self.update_moving_animation(jumping)

    def update_moving_animation(self, jumping: bool = False):
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
            if x2-x1 > 0:
                self.center_x += 5
            elif x2-x1 < 0:
                self.center_x -= 5
        texture_list = []
        if self.face == FACE_LEFT:
            texture_list = self.die_left_textures
        elif self.face == FACE_RIGHT:
            texture_list = self.die_right_textures
        if self.stand_frame % self.texture_change_frames == 0 and self.cur_texture_index < len(texture_list)-1:
            self.cur_texture_index += 1
        self.texture = texture_list[self.cur_texture_index]
        self.stand_frame += 1

    def update_attack_animation(self):
        if self.stand_frame % self.texture_change_frames == 0:
            if self.cur_texture_index < len(self.textures)-1:
                self.cur_texture_index += 1
            else:
                self.textures = []
                self.start_moving()
                return
        self.set_texture(self.cur_texture_index)
        self.stand_frame += 1

    def start_dying_animation(self):
        """
        Move toward damager and resolve gravity collisions.
        """
        self.stop()
        self.stand_frame = 1
        self.cur_texture_index = 0
        self.status = DYING

    def start_moving(self):
        self.texture_change_frames = 5
        if self.face == FACE_LEFT:
            self.center_x += ATTACK_DECAY
        elif self.face == FACE_RIGHT:
            self.center_x -= ATTACK_DECAY
        self.status = MOVING
        self.update_moving_animation()

    def can_attack(self):
        return self.status == MOVING

    def start_attack_1(self):
        self.texture_change_frames = 5
        self.start_attack(self.attack_1_left_textures, self.attack_1_right_textures)

    def start_attack_2(self):
        self.texture_change_frames = 10
        self.start_attack(self.attack_2_left_textures, self.attack_2_right_textures)
        # Create a bullet
        bullet = arcade.Sprite("images/items/bullet.png", LASER_SCALING)
        bullet.position = self.position
        if self.face == FACE_LEFT:
            bullet.change_x = -BULLET_SPEED
            bullet.right = self.left
            bullet.angle = 90
        elif self.face == FACE_RIGHT:
            bullet.change_x = BULLET_SPEED
            bullet.angle = -90
            bullet.left = self.right
        return bullet

    def start_attack(self, left_textures, right_textures):
        self.status = ATTACK
        self.stand_frame = 1
        self.cur_texture_index = 0
        if self.face == FACE_LEFT:
            self.textures = left_textures
            self.center_x -= ATTACK_DECAY
        elif self.face == FACE_RIGHT:
            self.textures = right_textures
            self.center_x += ATTACK_DECAY

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

        for i in range(1, 10):
            texture_name = f"/Dead ({i}).png"
            self.die_right_textures.append(arcade.load_texture(image_name + texture_name,
                                                               scale=CHARACTER_SCALING))
            self.die_left_textures.append(arcade.load_texture(image_name + texture_name,
                                                              scale=CHARACTER_SCALING, mirrored=True))

        for i in range(1, 7):
            texture_name = f"/Melee ({i}).png"
            self.attack_1_right_textures.append(arcade.load_texture(image_name + texture_name,
                                                               scale=CHARACTER_SCALING))
            self.attack_1_left_textures.append(arcade.load_texture(image_name + texture_name,
                                                              scale=CHARACTER_SCALING, mirrored=True))

        for i in range(1, 3):
            texture_name = f"/Shoot ({i}).png"
            self.attack_2_right_textures.append(arcade.load_texture(image_name + texture_name,
                                                                    scale=CHARACTER_SCALING))
            self.attack_2_left_textures.append(arcade.load_texture(image_name + texture_name,
                                                                   scale=CHARACTER_SCALING, mirrored=True))

    def set(self, position):
        self.initial = position
        self.position = position

    def reset(self):
        self.status = MOVING
        self.texture_change_frames = 5
        self.position = self.initial
        self.stop()
        if self.center_x < 100:
            self.face = arcade.FACE_RIGHT
        else:
            self.face = arcade.FACE_LEFT
