from arcade import Sprite

MODE_CYCLE_FORWARD = 0
MODE_CYCLE_BACKWARD = 1
MODE_CYCLE_PONG = 2
MODE_ONE_FORWARD = 3


class AnimatedSprite(Sprite):
    """
    Sprite for platformer games that supports animations.
    """

    def __init__(self, scale: float = 1,
                 image_x: float = 0, image_y: float = 0,
                 center_x: float = 0, center_y: float = 0):

        super().__init__(scale=scale, image_x=image_x, image_y=image_y,
                         center_x=center_x, center_y=center_y)
        self.mode = MODE_CYCLE_FORWARD
        self.forwardWay = True
        self.cur_texture_index = 0
        self.texture_change_frames = 5
        self.frame = -1

    def start_animation(self, textures, mode=MODE_CYCLE_FORWARD):
        self.textures = textures
        self.mode = mode
        if mode == MODE_CYCLE_FORWARD:
            self.cur_texture_index = 0
            self.forwardWay = True
        elif mode == MODE_CYCLE_BACKWARD:
            self.cur_texture_index = len(textures) - 1
            self.forwardWay = False
        elif mode == MODE_CYCLE_PONG:
            self.cur_texture_index = 0
            self.forwardWay = True
        else: # MODE_ONE_FORWARD
            self.cur_texture_index = 0
            self.forwardWay = True
        self.set_texture(self.cur_texture_index)

    def update_animation(self):
        """
        Logic for selecting the proper texture to use.
        """
        self.frame += 1
        if self.frame % self.texture_change_frames == 0:
            if self.forwardWay:
                self.cur_texture_index += 1
            else:
                self.cur_texture_index -= 1

            if self.cur_texture_index >= len(self.textures) or self.cur_texture_index < 0:
                self.on_animation_end()
            self.set_texture(self.cur_texture_index)

    def on_animation_end(self):
        """
        Reached an end of animation.
        """
        if self.mode == MODE_CYCLE_FORWARD:
            self.cur_texture_index = 0
        elif self.mode == MODE_CYCLE_BACKWARD:
            self.cur_texture_index = len(self.textures) - 1
        elif self.mode == MODE_CYCLE_PONG:
            if self.forwardWay:
                self.cur_texture_index = len(self.textures) - 1
            else:
                self.cur_texture_index = 0
            self.forwardWay = not self.forwardWay
        else:  # MODE_ONE_FORWARD
            self.cur_texture_index = len(self.textures) - 1

