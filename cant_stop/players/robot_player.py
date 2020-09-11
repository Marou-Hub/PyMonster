from kivy.clock import Clock

from cant_stop.constants import ACTION_COLOR, SELECT_COLOR
from cant_stop.players.player import PlayerBehavior
from random import choice


class RobotBehavior(PlayerBehavior):
    def is_human(self):
        return False

    def select(self, context, selections):
        pair = choice(list(selections.keys()))
        dices = selections[pair]
        context.print_label('[color=' + ACTION_COLOR + '][size=20]is selecting[/size][/color] [color=' + SELECT_COLOR + '][size=30]' + str(pair) + '[/size][/color]')
        context.pre_select(pair, dices)
        Clock.schedule_once(self.complete_select(context, pair, dices), 2.)

    def complete_select(self, context, pair, dices):
        def selection_bind(event):
            context.select(pair, dices)
        return selection_bind

    def choose(self, context):
        do_play = choice([True, False])
        print("play? " + str(do_play))
        context.print_label('[color=' + ACTION_COLOR + '][size=20]is choosing to[/size][/color] [color=' + SELECT_COLOR + '][size=30]' + ('PLAY' if do_play else 'STOP') + '[/size][/color]')
        Clock.schedule_once(self.complete_choose(context.play if do_play else context.stop), 2.)

    def complete_choose(self, action):
        def choose_bind(event):
            action.trigger_action()
        return choose_bind
