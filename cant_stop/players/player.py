class PlayerBehavior(object):
    def is_human(self):
        pass

    def select(self, context, selections):
        """ Select dice pair from available selections """
        pass

    def choose(self, context):
        """ Choose to continue or to stop playing """
        pass


class Player(object):
    def __init__(self, id, color, human):
        self.id = id
        self.color = color
        self.score = 0
        self.behavior = None
        self.human = human

    @property
    def human(self):
        return self.behavior.is_human()

    @human.setter
    def human(self, v):
        if v:
            from cant_stop.players.human_player import HumanBehavior
            self.behavior = HumanBehavior()
        else:
            from cant_stop.players.robot_player import RobotBehavior
            self.behavior = RobotBehavior()

    def get_name(self):
        return 'Player ' + str(self.id)

    def select(self, context, selections):
        self.behavior.select(context, selections)

    def choose(self, context):
        self.behavior.choose(context)
