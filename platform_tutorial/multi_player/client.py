from time import sleep

from platform_tutorial.multi_player.game_event import GameEvent, KEY_PRESS
from platform_tutorial.multi_player.network import Network


class Client(Network):
    def __init__(self):
        super().__init__()


def main():
    """ Main method """
    client = Client()
    client.start_client()
    sleep(2)
    client.send(GameEvent(KEY_PRESS, 1, 2))
    sleep(2)
    client.send(GameEvent(KEY_PRESS, 1, 2))
    sleep(2)
    client.stop()


if __name__ == "__main__":
    main()
