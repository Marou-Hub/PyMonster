import arcade

from platform_tutorial.animations.animated_character import AnimatedCharacter, FACE_LEFT, FACE_RIGHT

SMALL_ENEMY_SCALING = 0.5
SMALL_ENEMY_SPEED = 2


def generate_enemy(filename, position, flag_list):
    if filename == "images/enemies/wormGreen.png":
        return SmallEnemy("images/worm", position, flag_list)


class SmallEnemy(AnimatedCharacter):
    def __init__(self, image_folder, position, flag_list):
        super().__init__(position, SMALL_ENEMY_SCALING)
        self.flag_list = flag_list
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

        self.change_x = SMALL_ENEMY_SPEED

    def update_animation(self):
        self.update()
        super().update_animation()

        # change direction if hit a flag
        if self.flag_list:
            hit_list = arcade.check_for_collision_with_list(self, self.flag_list)
            if len(hit_list) > 0:
                if self.face == FACE_LEFT:
                    self.face = FACE_RIGHT
                    self.change_x = SMALL_ENEMY_SPEED
                elif self.face == FACE_RIGHT:
                    self.face = FACE_LEFT
                    self.change_x = -SMALL_ENEMY_SPEED

    def kill(self):
        self.start_dying_animation()

    def on_dead(self):
        self.remove_from_sprite_lists()
