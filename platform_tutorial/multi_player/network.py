import queue
import socket
from threading import Event, Thread

from platform_tutorial.multi_player.game_event import GameEvent, WELCOME, serialize_event, deserialize_event

SERVER = "127.0.0.1"
PORT = 5555


class Network:
    def __init__(self):
        self._socket = None
        self._socket2 = None
        self.started: Event = Event()
        self.incoming_events = queue.Queue()
        self.accept_thread = None
        self.consumer_thread = None

    @property
    def socket(self):
        return self._socket2 if self._socket2 is not None else self._socket

    def start_client(self):
        print("Starting client")
        self._socket = socket.socket()
        self._socket.connect((SERVER, PORT))
        self.started.set()
        self.consume()

    def start_server(self):
        print("Starting server")
        self.started.set()
        self._socket = socket.socket()
        self._socket.bind((SERVER, PORT))
        self._socket.listen(1)
        self.accept()

    def stop(self):
        print("Stopping server")
        self.started.clear()
        if self._socket2:
            self._socket2.close()
        if self._socket:
            self._socket.close()

    def send(self, event):
        print("Sending event: ", event)
        self.socket.sendall(serialize_event(event))

    def on_client_connected_to_server(self, conn):
        if self._socket2:
            self._socket2.close()
        self._socket2 = conn
        self.send(GameEvent(WELCOME))
        self.consume()

    def on_client_disconnected(self):
        pass

    def accept(self):
        if self.accept_thread and self.accept_thread.is_alive():
            self.accept_thread.join(1)
        self.accept_thread = AcceptThread(self)
        self.accept_thread.start()

    def consume(self):
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(1)
        self.consumer_thread = ConsumerThread(self)
        self.consumer_thread.start()

    def get_events(self):
        items = []
        try:
            while True:
                item = self.incoming_events.get_nowait()
                if item is not None:
                    items.append(item)
                else:
                    break
        except queue.Empty:
            pass
        return items


class AcceptThread(Thread):
    def __init__(self, network: Network):
        super().__init__()
        self.network = network

    def run(self):
        print("Start listening")
        while self.network.started.is_set():
            try:
                conn, addr = self.network._socket.accept()
                print("Connected by: ", addr)
                self.network.on_client_connected_to_server(conn)
            except:
                break


class ConsumerThread(Thread):
    def __init__(self, network: Network):
        super().__init__()
        self.network = network

    def run(self):
        print("Start consuming")
        while self.network.started.is_set():
            try:
                data = self.network.socket.recv(2048)
                if not data:
                    print("Disconnected")
                    break
                event = deserialize_event(data)
                self.network.incoming_events.put_nowait(event)
                print("Received: ", event)
            except:
                break
        if self.network.started.is_set():
            print("Lost connection")
        self.network.on_client_disconnected()
