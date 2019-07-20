import pickle

# Event types
# Lifecycle
WELCOME = 0
QUIT = 1
# User inputs
KEY_PRESS = 10
KEY_RELEASE = 11
MOUSE_PRESS = 12
# World updates
LEVEL = 20
MOVE = 21
CREATE = 22
DELETE = 23


class GameEvent:
    def __init__(self, event_type, pid=0, x=0, y=0, vx=0, vy=0, cond=False, desc=""):
        self.event_type: int = event_type
        self.pid: int = pid
        self.x: float = x
        self.y: float = y
        self.vx: float = vx
        self.vy: float = vy
        self.cond: float = cond
        self.desc: str = desc

    def __str__(self):
        return "type=" + str(self.event_type) + ", owner=" + str(self.pid)


def serialize_event(event: GameEvent):
    return pickle.dumps(event)


def deserialize_event(event) -> GameEvent:
    return pickle.loads(event)
