from threading import Event

from platform_tutorial.multi_player.network import Network


class Server(Network):
    def __init__(self):
        super().__init__()
        self.connected: Event = Event()

    def on_client_connected_to_server(self, conn):
        self.connected.set()
        super().on_client_connected_to_server(conn)

    def on_client_disconnected(self):
        self.connected.clear()


def main():
    """ Main method """
    server = Server()
    server.start_server()
    server.connected.wait()
    server.incoming_events.get()
    server.incoming_events.get()
    server.stop()


if __name__ == "__main__":
    main()
