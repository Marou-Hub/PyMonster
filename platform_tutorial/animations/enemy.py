import arcade

from platform_tutorial.animations.animated_character import AnimatedCharacter, FACE_LEFT, FACE_RIGHT
from platform_tutorial.constants import convert_speed_to_frame

SMALL_ENEMY_SCALING = 0.5
SMALL_ENEMY_SPEED = 0.2
BIG_ENEMY_SPEED = 0.5


def generate_enemy(tag, position, flag_list):
    if tag == "worm":
        return SmallEnemy("images/worm", flag_list, position)
    if tag == "slime":
        return SmallEnemy("images/slime", flag_list, position)
    if tag == "zombie_1":
        return BigEnemy("images/zombie_1", flag_list, position, 0.21)
    if tag == "zombie_2":
        return BigEnemy("images/zombie_2", flag_list, position, 0.18)
    return None


class Enemy(AnimatedCharacter):
    def __init__(self, flag_list, position, scale, speed):
        super().__init__(position, scale)
        self.flag_list = flag_list
        self.speed = speed
        self.change_x = self.speed

    def update_animation(self, delta_time: float = 1/60):
        self.update()

        # change direction if hit a flag
        if self.flag_list:
            hit_list = arcade.check_for_collision_with_list(self, self.flag_list)
            if len(hit_list) > 0:
                if self.face == FACE_LEFT:
                    self.change_x = convert_speed_to_frame(self.speed, delta_time)
                elif self.face == FACE_RIGHT:
                    self.change_x = - convert_speed_to_frame(self.speed, delta_time)
        super().update_animation(delta_time)

    def kill(self):
        self.start_dying_animation()

    def on_dead(self):
        self.remove_from_sprite_lists()


class SmallEnemy(Enemy):
    def __init__(self, image_folder, flag_list, position):
        super().__init__(flag_list, position, SMALL_ENEMY_SCALING, SMALL_ENEMY_SPEED)
        self.setup(image_folder)

    def setup(self, image_folder):
        self.stand_right_textures.append(arcade.load_texture(image_folder + "/stand.png", scale=SMALL_ENEMY_SCALING, mirrored=True))
        self.stand_left_textures.append(arcade.load_texture(image_folder + "/stand.png", scale=SMALL_ENEMY_SCALING))

        self.walk_right_textures.append(arcade.load_texture(image_folder + "/move.png", scale=SMALL_ENEMY_SCALING, mirrored=True))
        self.walk_right_textures.append(self.stand_right_textures[0])
        self.walk_left_textures.append(arcade.load_texture(image_folder + "/move.png", scale=SMALL_ENEMY_SCALING))
        self.walk_left_textures.append(self.stand_left_textures[0])

        self.die_right_textures.append(arcade.load_texture(image_folder + "/hurt.png", scale=SMALL_ENEMY_SCALING, mirrored=True))
        self.die_right_textures.append(arcade.load_texture(image_folder + "/dead.png", scale=SMALL_ENEMY_SCALING, mirrored=True))
        self.die_left_textures.append(arcade.load_texture(image_folder + "/hurt.png", scale=SMALL_ENEMY_SCALING))
        self.die_left_textures.append(arcade.load_texture(image_folder + "/dead.png", scale=SMALL_ENEMY_SCALING))


class BigEnemy(Enemy):
    def __init__(self, image_folder, flag_list, position, scale):
        super().__init__(flag_list, position, scale, BIG_ENEMY_SPEED)
        self.center_y += 16
        self.setup(image_folder)

    def setup(self, image_folder):
        for i in range(1, 10):
            texture_name = f"/Idle ({i}).png"
            self.stand_right_textures.append(arcade.load_texture(image_folder + texture_name, scale=self.scale))
            self.stand_left_textures.append(arcade.load_texture(image_folder + texture_name, scale=self.scale, mirrored=True))

        for i in range(1, 8):
            texture_name = f"/Walk ({i}).png"
            self.walk_right_textures.append(arcade.load_texture(image_folder + texture_name, scale=self.scale))
            self.walk_left_textures.append(arcade.load_texture(image_folder + texture_name, scale=self.scale, mirrored=True))

        for i in range(1, 10):
            texture_name = f"/Dead ({i}).png"
            self.die_right_textures.append(arcade.load_texture(image_folder + texture_name, scale=self.scale))
            self.die_left_textures.append(arcade.load_texture(image_folder + texture_name,scale=self.scale, mirrored=True))

