from platform_tutorial.constants import SCREEN_WIDTH


class Road:
    def __init__(self):
        self.current_level = 0

    def exit_right(self):
        next_level = 1
        pos_x = 64
        pos_y = 96
        if self.current_level == 1:
            next_level = 2
        return next_level, pos_x, pos_y

    def exit_left(self):
        next_level = 1
        pos_x = 2388
        pos_y = 96
        if self.current_level == 2:
            next_level = 1
        if self.current_level == 3:
            next_level = 2
            pos_x = 2398
        return next_level, pos_x, pos_y

    def exit_door(self):
        next_level = 1
        pos_x = 64
        pos_y = 96
        if self.current_level == 2:
            next_level = 3
        return next_level, pos_x, pos_y
