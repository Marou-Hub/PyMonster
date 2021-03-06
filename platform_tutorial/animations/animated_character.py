import math
import arcade

# Orientation
FACE_RIGHT = 1
FACE_LEFT = 2
# Animation mode
MOVING = 1
ATTACK = 2
DYING = 3


class AnimatedCharacter(arcade.Sprite):
    def __init__(self, position, scale: float = 1):
        super().__init__(scale=scale)

        self.initial = None
        if position is not None:
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

        self.cur_texture_index = 0
        self.texture_change_distance = 20
        self.texture_change_time: float = 0.2
        self.last_texture_change_center_x = 0
        self.last_texture_change_center_y = 0
        self.stand_time: float = 0.

    def update_animation(self, delta_time: float = 1/60):
        self.update_animations(delta_time, False)

    def update_animations(self, delta_time: float, jumping: bool):
        if self.status == ATTACK:
            self.update_attack_animation(delta_time)
        elif self.status == DYING:
            self.update_dying_animation(delta_time)
        else:
            self.update_moving_animation(delta_time, jumping)

    def update_moving_animation(self, delta_time: float, jumping: bool = False):
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
            self._safe_set_texture(texture_list)
            if self.cur_texture_index < len(texture_list) - 1:
                self.cur_texture_index += 1

        elif self.change_x == 0 and self.change_y == 0:
            if self.face == FACE_LEFT:
                texture_list = self.stand_left_textures
            elif self.face == FACE_RIGHT:
                texture_list = self.stand_right_textures
            if self.stand_time >= self.texture_change_time:
                self.stand_time = 0.
                self.cur_texture_index += 1
                if self.cur_texture_index >= len(texture_list):
                    self.cur_texture_index = 0
            else:
                self.stand_time += delta_time
            self._safe_set_texture(texture_list)

        elif change_direction or distance >= self.texture_change_distance:
            self.last_texture_change_center_x = self.center_x
            self.last_texture_change_center_y = self.center_y
            self.stand_time = 0.
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

            self._safe_set_texture(texture_list)
            self.cur_texture_index = next_index

        if self._texture is None:
            print("Error, no texture set")
        else:
            self.width = self._texture.width * self.scale
            self.height = self._texture.height * self.scale
        self.jumping = jumping

    def update_dying_animation(self, delta_time: float, damager: arcade.Sprite = None):
        """
        Move toward damager and resolve gravity collisions.
        """
        self.stop()
        if damager and damager.properties['Collision'] != 'False':
            x1 = self.center_x
            x2 = damager.center_x
            if x2 - x1 > 0:
                self.center_x += 5
            elif x2 - x1 < 0:
                self.center_x -= 5
        self.stand_time += delta_time
        if self.stand_time >= self.texture_change_time:
            self.stand_time = 0.
            texture_list = []
            if self.face == FACE_LEFT:
                texture_list = self.die_left_textures
            elif self.face == FACE_RIGHT:
                texture_list = self.die_right_textures
            if self.cur_texture_index < len(texture_list) - 1:
                self.cur_texture_index += 1
                try:
                    self._safe_set_texture(texture_list)
                except Exception as e:
                    print(e)
            else:
                self.on_dead()

    def _safe_set_texture(self, from_texture_list):
        if self.cur_texture_index >= len(from_texture_list):
            self.cur_texture_index = 0
        # try:
        self.texture = from_texture_list[self.cur_texture_index]
        # except Exception as e:
        #     print(e)

    def on_dead(self):
        pass

    def start_dying_animation(self):
        self.stop()
        self.stand_time = 0.
        self.cur_texture_index = 0
        self.status = DYING

    def update_attack_animation(self, delta_time: float):
        if self.stand_time >= self.texture_change_time:
            self.stand_time = 0.
            if self.cur_texture_index < len(self.textures) - 1:
                self.cur_texture_index += 1
            else:
                self.textures = []
                self.start_moving()
                return
        self.set_texture(self.cur_texture_index)
        self.stand_time += delta_time

    def start_moving(self):
        self.status = MOVING
        self.update_moving_animation()

    def can_attack(self):
        return self.status == MOVING

    def start_attack(self, left_textures, right_textures):
        self.status = ATTACK
        self.stand_time = 0.
        self.cur_texture_index = 0
        if self.face == FACE_LEFT:
            self.textures = left_textures
        elif self.face == FACE_RIGHT:
            self.textures = right_textures

    def set(self, position):
        self.initial = position
        self.position = position

    def reset(self):
        self.status = MOVING
        self.position = self.initial
        self.stop()
        if self.center_x < 100:
            self.face = arcade.FACE_RIGHT
        else:
            self.face = arcade.FACE_LEFT
