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


class A:
    def __init__(self):
        print("Entering A")
        print("Leaving A")


class B:
    def __init__(self):
        print("Entering B")
        print("Leaving B")


class C(A, B):
    def __init__(self):
        print("Entering C")
        # A.__init__(self)
        # B.__init__(self)
        super(B, self).__init__()
        print("Leaving C")


def main():
    """ Main method """
    C()
    # server = Server()
    # server.start_server()
    # server.connected.wait()
    # server.incoming_events.get()
    # server.incoming_events.get()
    # server.stop()


if __name__ == "__main__":
    main()
