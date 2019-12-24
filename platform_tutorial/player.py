import arcade

from platform_tutorial.animations.animated_character import AnimatedCharacter, FACE_LEFT, FACE_RIGHT
from platform_tutorial.constants import GRAVITY
from platform_tutorial.physics_engine import PhysicsEngine

CHARACTER_SCALING = 0.21
BULLET_SCALING = 0.8
BULLET_SPEED = 10
ATTACK_DECAY = 10
# Movement speed of player, in tile per second
PLAYER_MOVEMENT_SPEED = 4
PLAYER_JUMP_SPEED = 10


class Player(AnimatedCharacter):
    def __init__(self, image_name, position):
        super().__init__(position, CHARACTER_SCALING)

        self.physics_engine = None
        self.jumping: bool = False

        self.attack_1_right_textures = []
        self.attack_1_left_textures = []
        self.attack_2_right_textures = []
        self.attack_2_left_textures = []

        self.texture_change_distance = 20

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
        self.texture_change_time = 0.2
        super().start_moving()

    def start_attack_1(self):
        # Create a fake invisible bullet representing the knife hit box
        self.hit_box = arcade.Sprite("images/items/hitbox.png", scale=0.5)
        self.hit_box.position = self.position
        if self.face == FACE_LEFT:
            self.hit_box.right = self.left
        elif self.face == FACE_RIGHT:
            self.hit_box.left = self.right
        # Start animation
        self.texture_change_time = 0.2
        self.start_attack(self.attack_1_left_textures, self.attack_1_right_textures)
        return self.hit_box

    def start_attack_2(self):
        self.texture_change_time = 0.1
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
        for i in range(1, 10, 2):
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

    def update_animation(self, delta_time: float = 1/60):
        jumping = self.is_jumping()
        # refresh jumping state
        if jumping and self.change_y == 0 and self.physics_engine:
            self.physics_engine.can_jump()
            jumping = self.is_jumping()
        self.update_animations(delta_time, jumping)

    def enable_physics(self, wall_list):
        # Create the 'physics engine'
        self.physics_engine = PhysicsEngine(self, wall_list, GRAVITY)
        self.physics_engine.enable_multi_jump(1)

    def update_physics(self, delta_time):
        if self.physics_engine:
            self.physics_engine.update(delta_time)

    def jump(self):
        if self.physics_engine and self.physics_engine.can_jump():
            self.physics_engine.jump(PLAYER_JUMP_SPEED)
            return True
        return False

    def set_jumping(self, jumping):
        self.jumping = jumping

    def is_jumping(self):
        return self.physics_engine.jumps_since_ground > 0 if self.physics_engine is not None else self.jumping

    def move_left(self):
        self.change_x = -PLAYER_MOVEMENT_SPEED

    def move_right(self):
        self.change_x = PLAYER_MOVEMENT_SPEED

    def stop_move(self):
        self.change_x = 0
