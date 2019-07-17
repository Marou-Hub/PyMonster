import arcade

from platform_tutorial.animations.animated_character import AnimatedCharacter, FACE_LEFT, FACE_RIGHT

CHARACTER_SCALING = 0.21
BULLET_SCALING = 0.8
BULLET_SPEED = 5
ATTACK_DECAY = 10


class Player(AnimatedCharacter):
    def __init__(self, image_name, position):
        super().__init__(position, CHARACTER_SCALING)

        self.attack_1_right_textures = []
        self.attack_1_left_textures = []
        self.attack_2_right_textures = []
        self.attack_2_left_textures = []

        self.texture_change_distance = 20
        self.texture_change_frames = 5

        self.hit_box = None

        self.setup(image_name)

    def start_moving(self):
        # remove attack 1 hit box
        if self.hit_box is not None:
            self.hit_box.kill()
            self.hit_box = None
        # replace player for move animation
        if self.face == FACE_LEFT:
            self.center_x += ATTACK_DECAY
        elif self.face == FACE_RIGHT:
            self.center_x -= ATTACK_DECAY
        self.texture_change_frames = 5
        super().start_moving()

    def start_attack_1(self):
        self.texture_change_frames = 5
        self.start_attack(self.attack_1_left_textures, self.attack_1_right_textures)
        # Create a fake invisible bullet representing the knife hit box
        self.hit_box = arcade.Sprite("images/tiles/cactus.png", scale=0.5)
        self.hit_box.points = self.points
        if self.face == FACE_LEFT:
            self.hit_box.right = self.left
        elif self.face == FACE_RIGHT:
            self.hit_box.left = self.right
        return self.hit_box

    def start_attack_2(self):
        self.texture_change_frames = 10
        self.start_attack(self.attack_2_left_textures, self.attack_2_right_textures)
        # Create a bullet
        bullet = arcade.Sprite("images/items/bullet.png", BULLET_SCALING)
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
        if self.face == FACE_LEFT:
            self.center_x -= ATTACK_DECAY
        elif self.face == FACE_RIGHT:
            self.center_x += ATTACK_DECAY
        super().start_attack(left_textures, right_textures)

    def setup(self, image_name):
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
