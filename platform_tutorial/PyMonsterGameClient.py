import arcade

from platform_tutorial.PyMonsterGame import MyGame
from platform_tutorial.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from platform_tutorial.multi_player.client import Client
from platform_tutorial.multi_player.game_event import GameEvent, LEVEL, MOVE, KEY_PRESS, MOUSE_PRESS, KEY_RELEASE
from platform_tutorial.player import Player


class MyGameClient(MyGame, Client):
    def __init__(self):
        MyGame.__init__(self)
        Client.__init__(self)
        self.ready = False
        self.player2 = None
        self.switch = {
            LEVEL: self.load_level,
            MOVE: self.move_item
        }

    def on_draw(self):
        if self.ready:
            super().on_draw()
        else:
            self.viewport.draw_bubble(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, 500, 50, arcade.csscolor.WHITE_SMOKE)
            self.viewport.draw_text("Connexion au serveur", SCREEN_WIDTH / 2,
                                    SCREEN_HEIGHT / 2 + 100, arcade.csscolor.LIGHT_SKY_BLUE, 20,
                                    anchor_x="center", anchor_y="center")

    def draw_players(self):
        self.player.draw()
        self.player2.draw()

    def update(self, delta_time):
        for event in self.get_events():
            func = self.switch.get(event.event_type, None)
            if func is not None:
                func(event)
        if self.level is not None:
            # Call update for player
            self.player2.update_animations(False)
            super().update(delta_time)

    def load_level(self, event):
        level, pos = self.road.load_level(event.pid)
        if self.player2 is None:
            self.player2 = Player("images/adventure_girl_2", pos)
        else:
            self.player2.position = pos
        self.setup(level, pos, False)
        self.ready = True

    def move_item(self, event):
        if event.pid == 1:
            self.player.center_x = event.x
            self.player.center_y = event.y
            self.player.change_x = event.vx
            self.player.change_y = event.vy
            self.player.set_jumping(event.cond)
        elif event.pid == 2:
            self.player2.center_x = event.x
            self.player2.center_y = event.y
            self.player2.change_x = event.vx
            self.player2.change_y = event.vy
            self.player2.set_jumping(event.cond)

    def on_key_press(self, key, modifiers):
        self.send(GameEvent(KEY_PRESS, key))

    def on_key_release(self, key, modifiers):
        self.send(GameEvent(KEY_RELEASE, key))
        if key == arcade.key.LEFT or key == arcade.key.Q or key == arcade.key.RIGHT or key == arcade.key.D:
            self.player2.stop_move()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.send(GameEvent(MOUSE_PRESS, button, x, y))

    @property
    def current_player(self):
        return self.player2


def main():
    """ Main method """
    window = MyGameClient()
    window.start_client()

    arcade.run()


if __name__ == "__main__":
    main()
