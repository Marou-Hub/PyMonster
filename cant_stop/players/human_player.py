from kivy.uix.button import Button

from cant_stop.constants import RESET_COLOR
from cant_stop.players.player import PlayerBehavior


class HumanBehavior(PlayerBehavior):
    def is_human(self):
        return True

    def select(self, context, selections):
        for pair, dices in selections.items():
            sel = Button(text='[color=' + RESET_COLOR + '][size=30]' + str(pair) + '[/size][/color]', markup=True)
            sel.bind(on_press=self.make_selection_bind(context, pair, dices))
            context.add_button(sel)

    def make_selection_bind(self, context, pair, dices):
        def selection_bind(event):
            context.select(pair, dices)
        return selection_bind
