import arcade

from platform_tutorial.PyMonsterGame import MyGame
from platform_tutorial.multi_player.game_event import GameEvent, MOVE, LEVEL, CREATE, DELETE, KEY_PRESS, MOUSE_PRESS, KEY_RELEASE
from platform_tutorial.multi_player.server import Server
from platform_tutorial.player import Player


NETWORK_LATENCY = 0.1


class MyGameServer(MyGame, Server):
    def __init__(self):
        MyGame.__init__(self)
        Server.__init__(self)
        self.latency_timer: float = 0
        self.player2 = None
        self.switch = {
            CREATE: self.setup_player2,
            DELETE: self.delete_player2,
            KEY_PRESS: self.key_press_player2,
            KEY_RELEASE: self.key_release_player2,
            MOUSE_PRESS: self.mouse_press_player2,
        }

    def on_client_connected_to_server(self, conn):
        super().on_client_connected_to_server(conn)
        position = self.player.position
        self.send_world_full_status()
        self.incoming_events.put_nowait(GameEvent(CREATE, 2, position[0], position[1]))

    def setup(self, level, position, with_physics=True):
        super().setup(level, position, with_physics)
        if self.connected.is_set():
            if self.player2 is not None:
                self.player2.enable_physics(self.level.wall_list)
                self.player2.position = position
            self.send_world_full_status()

    def on_client_disconnected(self):
        super().on_client_disconnected()
        self.incoming_events.put_nowait(GameEvent(DELETE, 2))

    def setup_player2(self, event):
        self.player2 = Player("images/adventure_girl_2", [event.x, event.y])
        self.player2.update_animations(False)
        self.player2.enable_physics(self.level.wall_list)

    # noinspection PyUnusedLocal
    def delete_player2(self, event):
        self.player2.remove_from_sprite_lists()
        self.player2 = None

    def key_press_player2(self, event):
        self.key_press(event.pid, self.player2)

    def key_release_player2(self, event):
        self.key_release(event.pid, self.player2)

    def mouse_press_player2(self, event):
        self.mouse_press(event.x, event.y, event.pid, self.player2)

    def draw_players(self):
        self.player.draw()
        if self.connected.is_set() and self.player2 is not None:
            self.player2.draw()

    def hud_console(self):
        # Debug
        hud = f"Score: {self.score} Player1: {int(self.player.center_x)}"
        if self.connected.is_set() and self.player2 is not None:
            hud += f" Player2: {int(self.player2.center_x)}"
        return hud

    def update(self, delta_time):
        for event in self.get_events():
            func = self.switch.get(event.event_type, None)
            if func is not None:
                func(event)
        if self.connected.is_set() and self.player2 is not None:
            # Call update physics
            self.player2.update_physics()
            # Call update for player
            self.player2.update_animation()
        # standard update
        super().update(delta_time)
        if self.connected.is_set():
            self.send_world_update(delta_time)

    def send_world_full_status(self):
        self.send(GameEvent(LEVEL, self.road.current_level))
        # player position
        self.send(GameEvent(MOVE, 1, self.player.center_x, self.player.center_y, self.player.change_x, self.player.change_y, self.player.is_jumping()))
        if self.player2 is not None:
            self.send(GameEvent(MOVE, 2, self.player2.center_x, self.player2.center_y, self.player2.change_x, self.player2.change_y, self.player2.is_jumping()))
        # all mobiles position

    def send_world_update(self, delta_time):
        self.latency_timer += delta_time
        if self.latency_timer > NETWORK_LATENCY:
            self.latency_timer = 0
            # players position
            self.send(GameEvent(MOVE, 1, self.player.center_x, self.player.center_y, self.player.change_x, self.player.change_y, self.player.is_jumping()))
            if self.player2 is not None:
                self.send(GameEvent(MOVE, 2, self.player2.center_x, self.player2.center_y, self.player2.change_x, self.player2.change_y, self.player.is_jumping()))
            # only changes since previous frame


def is_moving(sprite: arcade.Sprite):
    return sprite.change_x != 0 or sprite.change_y != 0


def main():
    """ Main method """
    window = MyGameServer()
    next_level, pos = window.road.next_level()
    window.setup(next_level, pos)
    window.start_server()

    arcade.run()


if __name__ == "__main__":
    main()
