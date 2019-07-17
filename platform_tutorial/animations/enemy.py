import arcade

from platform_tutorial.animations.animated_character import AnimatedCharacter, FACE_LEFT, FACE_RIGHT

SMALL_ENEMY_SCALING = 0.5
SMALL_ENEMY_SPEED = 1
BIG_ENEMY_SCALING = 0.2
BIG_ENEMY_SPEED = 1


def generate_enemy(filename, position, flag_list):
    if filename == "images/enemies/wormGreen.png":
        return SmallEnemy("images/worm", position, flag_list)
    if filename == "images/enemies/slimeGreen.png":
        return SmallEnemy("images/slime", position, flag_list)
    if filename == "images/enemies/zombie_1.png":
        return SmallEnemy("images/zombie_1", position, flag_list)
    if filename == "images/enemies/zombie_2.png":
        return SmallEnemy("images/zombie_2", position, flag_list)
    return None


class Enemy(AnimatedCharacter):
    def __init__(self, flag_list, position, scale, speed):
        super().__init__(position, scale)
        self.flag_list = flag_list
        self.speed = speed
        self.change_x = self.speed

    def update_animation(self):
        self.update()
        super().update_animation()

        # change direction if hit a flag
        if self.flag_list:
            hit_list = arcade.check_for_collision_with_list(self, self.flag_list)
            if len(hit_list) > 0:
                if self.face == FACE_LEFT:
                    self.face = FACE_RIGHT
                    self.change_x = self.speed
                elif self.face == FACE_RIGHT:
                    self.face = FACE_LEFT
                    self.change_x = -self.speed

    def kill(self):
        self.start_dying_animation()

    def on_dead(self):
        self.remove_from_sprite_lists()


class SmallEnemy(Enemy):
    def __init__(self, image_folder, position, flag_list):
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
    def __init__(self, image_folder, position, flag_list):
        super().__init__(flag_list, position, BIG_ENEMY_SCALING, BIG_ENEMY_SPEED)
        self.setup(image_folder)

    def setup(self, image_folder):
        self.stand_right_textures.append(arcade.load_texture(image_folder + "/stand.png", scale=BIG_ENEMY_SPEED, mirrored=True))
        self.stand_left_textures.append(arcade.load_texture(image_folder + "/stand.png", scale=SMALL_ENEMY_SCALING))

        self.walk_right_textures.append(arcade.load_texture(image_folder + "/move.png", scale=SMALL_ENEMY_SCALING, mirrored=True))
        self.walk_right_textures.append(self.stand_right_textures[0])
        self.walk_left_textures.append(arcade.load_texture(image_folder + "/move.png", scale=SMALL_ENEMY_SCALING))
        self.walk_left_textures.append(self.stand_left_textures[0])

        self.die_right_textures.append(arcade.load_texture(image_folder + "/hurt.png", scale=SMALL_ENEMY_SCALING, mirrored=True))
        self.die_right_textures.append(arcade.load_texture(image_folder + "/dead.png", scale=SMALL_ENEMY_SCALING, mirrored=True))
        self.die_left_textures.append(arcade.load_texture(image_folder + "/hurt.png", scale=SMALL_ENEMY_SCALING))
        self.die_left_textures.append(arcade.load_texture(image_folder + "/dead.png", scale=SMALL_ENEMY_SCALING))

        for i in range(1, 10):
            texture_name = f"/Idle ({i}).png"
            self.stand_right_textures.append(arcade.load_texture(image_folder + texture_name, scale=BIG_ENEMY_SPEED))
            self.stand_left_textures.append(arcade.load_texture(image_folder + texture_name, scale=BIG_ENEMY_SPEED, mirrored=True))

        for i in range(1, 8):
            texture_name = f"/Walk ({i}).png"
            self.walk_right_textures.append(arcade.load_texture(image_folder + texture_name, scale=BIG_ENEMY_SPEED))
            self.walk_left_textures.append(arcade.load_texture(image_folder + texture_name, scale=BIG_ENEMY_SPEED, mirrored=True))

        for i in range(1, 10):
            texture_name = f"/Dead ({i}).png"
            self.die_right_textures.append(arcade.load_texture(image_folder + texture_name, scale=BIG_ENEMY_SPEED))
            self.die_left_textures.append(arcade.load_texture(image_folder + texture_name,scale=BIG_ENEMY_SPEED, mirrored=True))

