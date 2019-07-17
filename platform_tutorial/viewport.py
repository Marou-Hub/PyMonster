import arcade

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
from platform_tutorial.constants import SCREEN_WIDTH, SCREEN_HEIGHT

LEFT_VIEWPORT_MARGIN = 150
RIGHT_VIEWPORT_MARGIN = 150
BOTTOM_VIEWPORT_MARGIN = 100
TOP_VIEWPORT_MARGIN = 100


class Viewport:
    def __init__(self):
        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

    def draw_text(self, text: str,
                  start_x: float, start_y: float,
                  color: arcade.Color,
                  font_size: float = 12,
                  width: int = 0,
                  align: str = "left",
                  font_name=('calibri', 'arial'),
                  bold: bool = False,
                  italic: bool = False,
                  anchor_x: str = "left",
                  anchor_y: str = "baseline",
                  rotation: float = 0
                  ):
        arcade.draw_text(text, start_x + self.view_left, start_y + self.view_bottom,
                         color, font_size, width, align, font_name, bold, italic, anchor_x, anchor_y, rotation)

    def draw_bubble(self, center_x: float, center_y: float, width: float, height: float, color: arcade.Color):
        arcade.draw_rectangle_filled(center_x + self.view_left, center_y + self.view_bottom, width, height, color)

    def shade(self):
        arcade.draw_lrtb_rectangle_filled(self.view_left, SCREEN_WIDTH + self.view_left, SCREEN_HEIGHT + self.view_bottom, self.view_bottom, [125, 125, 125, 125 ])

    def update(self, left, right, top, bottom):
        # --- Manage Scrolling ---

        # Track if we need to change the viewport

        changed = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if left < left_boundary:
            self.view_left -= left_boundary - left
            changed = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if right > right_boundary:
            self.view_left += right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if top > top_boundary:
            self.view_bottom += top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - bottom
            changed = True

        if changed:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)

    def set(self, left, bottom):
        self.view_bottom = int(bottom)
        self.view_left = int(left)

        # Do the scrolling
        arcade.set_viewport(self.view_left,
                            SCREEN_WIDTH + self.view_left,
                            self.view_bottom,
                            SCREEN_HEIGHT + self.view_bottom)

    def reset(self):
        self.view_left = 0
        self.view_bottom = 0

    def is_off_screen(self, sprite: arcade.Sprite):
        return sprite.left > self.view_left + SCREEN_WIDTH or sprite.right < self.view_left
