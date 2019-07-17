class SceneEvent:
    def __init__(self, trigger):
        self.trigger = trigger

    def update(self, delta_time):
        pass

    def draw(self):
        pass


class TimeLine:
    def __init__(self, end_timer=-1):
        self.events = []
        self.timer: float = 0
        self.end_timer: float = end_timer
        self.cur_event = None

    def add_event(self, event):
        self.events.append(event)

    def update(self, delta_time):
        self.timer += delta_time
        self.cur_event = None
        for event in self.events:
            if event.trigger <= self.timer:
                self.cur_event = event
            else:
                break
        if self.cur_event:
            self.cur_event.update(delta_time)

    def draw(self):
        if self.cur_event:
            self.cur_event.draw()

