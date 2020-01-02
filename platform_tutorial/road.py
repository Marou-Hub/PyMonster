from platform_tutorial.animations.fire import Fire
from platform_tutorial.constants import TILE_PROP
from platform_tutorial.cut_scene import Intro
from platform_tutorial.level import Level

ACCESS_LEFT = 0
ACCESS_RIGHT = 1
ACCESS_DOOR = 2
ACCESS_ITEMS = {
    ACCESS_LEFT: "accessLeft",  # images/items/flagRed1.png
    ACCESS_RIGHT: "accessRight",  # images/items/flagRed2.png
    ACCESS_DOOR: "accessDoor"  # images/tiles/doorClosed_mid.png
}
ACCESS_DEFAULT_POSITION = {
    ACCESS_LEFT: [64, 96],
    ACCESS_RIGHT: [2388, 96],
    ACCESS_DOOR: [2398, 96]
}


class LevelAccess:
    def __init__(self, level, access):
        self.next_level = level
        self.next_access = access


class LevelCrossing:
    def __init__(self, left=None, right=None, door=None):
        self.accesses = {ACCESS_LEFT: left, ACCESS_RIGHT: right, ACCESS_DOOR: door}

    def get(self, access):
        if access is not None and self.accesses[access]:
            return self.accesses[access]
        return self.accesses[ACCESS_LEFT]


class Road:
    def __init__(self, viewport, player):
        self.viewport = viewport
        self.player = player
        self.current_level = None
        self.levels = {
            0: LevelCrossing(LevelAccess(0, ACCESS_LEFT), LevelAccess(2, ACCESS_LEFT)),
            1: LevelCrossing(LevelAccess(1, ACCESS_LEFT), LevelAccess(2, ACCESS_LEFT), LevelAccess(1, ACCESS_LEFT)),
            2: LevelCrossing(LevelAccess(1, ACCESS_RIGHT), LevelAccess(2, ACCESS_RIGHT), LevelAccess(3, ACCESS_LEFT)),
            3: LevelCrossing(LevelAccess(2, ACCESS_DOOR)),
        }

    def next_level(self, exit_access=ACCESS_LEFT):
        target_level: LevelAccess
        if self.current_level is None:
            self.current_level = 0
            target_level = LevelAccess(0, ACCESS_LEFT)
        else:
            target_level = self.levels[self.current_level].get(exit_access)
        self.current_level = target_level.next_level
        return self.load_level(target_level.next_level, target_level.next_access)

    def load_level(self, current_level, current_access=ACCESS_LEFT):
        level = Level()
        level.setup(current_level)
        position = None
        for access in level.access_list:
            if access.properties[TILE_PROP] == ACCESS_ITEMS[current_access]:
                position = access.position
                break
        if position is None:
            position = ACCESS_DEFAULT_POSITION[current_access]
        self.current_level = current_level
        self.customize_level(level)
        return level, position

    def customize_level(self, level):
        if self.current_level == 0:
            for coin in level.coin_list:
                fire = Fire(center_x=coin.center_x, center_y=coin.center_y)
                level.dont_touch_list.append(fire)
                coin.kill()
            level.cut_scene = Intro(self.viewport, self.player)
