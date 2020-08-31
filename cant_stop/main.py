from random import randint
from enum import Enum

import kivy

kivy.require('1.9.1')

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import BooleanProperty, ObjectProperty, NumericProperty
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window, platform
from os.path import join, dirname

# KIVY LAUNCHER uses KIVY version is 1.9.1

DICE_COUNT = 4
CLIMBER_COUNT = 3
RESET_DICE = '0'
SELECT_COLOR = 'ff0000'
RESET_COLOR = 'ffd8ff'
curdir = dirname(__file__)


def image_folder(file):
    return join(curdir, 'images', file)


circle_texture = Image(source=image_folder('circle.png'), mipmap=True).texture


class Phase(Enum):
    ROLL = 1
    ROLLING = 2
    SELECT = 3
    CHOOSE = 4
    FAILED = 5


class DiceLayout(BoxLayout):
    ready = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(DiceLayout, self).__init__(orientation='vertical', **kwargs)
        self.dices = []
        for x in range(DICE_COUNT):
            dice = Dice()
            self.add_widget(dice)
            self.dices.append(dice)
        self.event = None
        self.animation_step = 0
        self.animation_time = 0

    def reset(self, dice):
        dice.text = dice.text.replace(SELECT_COLOR, RESET_COLOR)

    def select(self, dice):
        self.dices[dice].text = self.dices[dice].text.replace(RESET_COLOR, SELECT_COLOR)

    def roll_dice(self, event):
        self.ready = False
        for dice in self.dices:
            self.reset(dice)
            dice.update(randint(1, 6))
        self.start_animation()

    def start_animation(self):
        self.animation_step = 0
        self.animation_time = 0
        self.event = Clock.schedule_interval(self.step_animation, 1 / 30.)

    def step_animation(self, time_passed):
        dice = self.dices[self.animation_step % DICE_COUNT]
        dice.update(randint(1, 6))
        self.animation_step += 1
        self.animation_time += time_passed
        if self.animation_time > 1.0:
            self.stop_animation()

    def stop_animation(self):
        self.event.cancel()
        self.ready = True

    def get_all_pairs(self):
        pairs = {}
        key = tuple(sorted([self.dices[0].value + self.dices[1].value, self.dices[2].value + self.dices[3].value]))
        val = [0, 1, 2, 3]
        pairs[key] = val
        key = tuple(sorted([self.dices[0].value + self.dices[2].value, self.dices[1].value + self.dices[3].value]))
        val = [0, 2, 1, 3]
        pairs[key] = val
        key = tuple(sorted([self.dices[0].value + self.dices[3].value, self.dices[1].value + self.dices[2].value]))
        val = [0, 3, 1, 2]
        pairs[key] = val
        return pairs


class Dice(Label):
    def __init__(self, **kwargs):
        super(Dice, self).__init__(text='[color=' + RESET_COLOR + '][size=70]' + RESET_DICE + '[/size][/color]', markup=True, **kwargs)
        self.value = 0

    def update(self, value):
        self.value = value
        self.text = '[color=' + RESET_COLOR + '][size=70]' + str(value) + '[/size][/color]'


class BoardLayout(BoxLayout):
    def __init__(self, board, **kwargs):
        super(BoardLayout, self).__init__(orientation='horizontal', **kwargs)
        # Board
        self.board = board
        self.climbers = {}
        self.board_images = {}
        self.board_labels = {}
        # Build board UI
        max_len = 0
        for li in self.board.values():
            max_len = max(max_len, len(li))
        col_size = 1 / 11
        for x, li in self.board.items():
            col = BoxLayout(orientation='vertical', size_hint_x=col_size)
            for y in range(len(li), max_len):
                widget = Image()
                widget.color = [0, 0, 0, 0.5]
                widget.texture = circle_texture
                col.add_widget(widget)
            lim = []
            for y in range(len(li)):
                widget = Image()
                widget.texture = circle_texture
                lim.insert(0, widget)
                col.add_widget(widget)
            label = Label(text='[color=' + RESET_COLOR + '][size=40]' + str(x) + '[/size][/color]', markup=True, halign='center')
            col.add_widget(label)
            self.add_widget(col)
            self.board_images[x] = lim
            self.board_labels[x] = label

    def pre_select(self, pair):
        self.board_labels[pair].text = self.board_labels[pair].text.replace(RESET_COLOR, SELECT_COLOR)

    def un_select(self):
        for label in self.board_labels.values():
            label.text = label.text.replace(SELECT_COLOR, RESET_COLOR)

    def can_use_without_climber(self, pair):
        li = self.board[pair]
        if li[-1] != 0:  # already full
            return True
        if pair in self.climbers:  # already selected
            return True
        return False

    def select(self, pair):
        # Update board
        li = self.board[pair]
        if li[-1] != 0:  # already full
            return False
        need_climber = pair not in self.climbers
        if need_climber:
            self.climbers[pair] = 1
        else:
            self.climbers[pair] += 1
        # update UI
        self.update()
        return need_climber

    def update(self):
        for k, li in self.board.items():
            player = -1
            for i, v in enumerate(li):
                if v == 1:
                    player = i
                    self.board_images[k][i].color = [0, 0, 1, 1]
                else:
                    self.board_images[k][i].color = [1, 1, 1, 1]
            if k in self.climbers:
                self.board_images[k][min(player + self.climbers[k], len(li) - 1)].color = [1, 0, 0, 1]

    def reset(self):
        self.un_select()
        self.climbers = {}
        self.update()

    def validate(self):
        for k, v in self.climbers.items():
            li = self.board[k]
            for index, value in enumerate(li):
                if value == 1:
                    li[index] = 0
                    li[min(index + v, len(li) - 1)] = 1
                    break
            else:
                li[min(v - 1, len(li) - 1)] = 1
        self.climbers = {}
        self.update()


class CantStopScreen(BoxLayout):
    phase = ObjectProperty(Phase.ROLL)
    remaining_climbers = NumericProperty(CLIMBER_COUNT)

    def __init__(self, **kwargs):
        super(CantStopScreen, self).__init__(orientation='horizontal', **kwargs)
        # Build Dices UI
        tools = BoxLayout(orientation='vertical', size_hint_x=0.15)
        self.dices = DiceLayout()
        self.dices.bind(ready=self.on_ready)
        tools.add_widget(self.dices)
        # Climbers stock
        container = BoxLayout(orientation='vertical', padding=[15, 0], size_hint_y=0.2)
        self.climbers = Button(text='[color=888888][size=50]' + str(CLIMBER_COUNT) + '[/size][/color]', markup=True, background_disabled_normal=image_folder('climber.png'), disabled=True)
        container.add_widget(self.climbers)
        tools.add_widget(container)
        self.add_widget(tools)
        # Build board UI
        board = {
            2: [0, 0, 0],
            3: [0, 0, 0, 0],
            4: [0, 0, 0, 0, 0],
            5: [0, 0, 0, 0, 0, 0],
            6: [0, 0, 0, 0, 0, 0, 0],
            7: [0, 0, 0, 0, 0, 0, 0, 0],
            8: [0, 0, 0, 0, 0, 0, 0],
            9: [0, 0, 0, 0, 0, 0],
            10: [0, 0, 0, 0, 0],
            11: [0, 0, 0, 0],
            12: [0, 0, 0],
        }
        self.board = BoardLayout(board)
        panel = BoxLayout(orientation='vertical')
        panel.add_widget(self.board)
        # Button
        self.buttons = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.2)
        # self.play = Button(background_normal=image_folder('dices.png'), background_down=image_folder('dices.png'), background_disabled_normal=image_folder('dices.png'), background_color=(1, 1, 1, 1), size_hint_x=0.2)
        self.play = Button(text='[color='+RESET_COLOR+'][size=30]PLAY[/size][/color]', markup=True, size_hint_x=0.3)
        self.play.bind(on_press=self.play_round)
        self.buttons.add_widget(self.play)
        self.stop = Button(text='[color='+RESET_COLOR+'][size=30]STOP[/size][/color]', markup=True, size_hint_x=0.3, disabled=True)
        self.stop.bind(on_press=self.stop_round)
        # Help label
        self.label = Label(text='[color=ffd800][size=20]Launch dice[/size][/color]', markup=True, halign='left')
        panel.add_widget(self.buttons)
        self.add_widget(panel)

    def start_round(self):
        self.remaining_climbers = CLIMBER_COUNT

    def on_ready(self, _, value):
        if value:
            all_pairs = self.dices.get_all_pairs()
            selections = {}
            if self.remaining_climbers > 1:
                selections = all_pairs
            elif self.remaining_climbers == 1:
                for pair, dices in all_pairs.items():
                    if self.board.can_use_without_climber(pair[0]):
                        selections[pair] = dices
                    else:
                        selections[(pair[1], )] = [dices[2], dices[3]]
            else:
                for pair, dices in all_pairs.items():
                    use1 = self.board.can_use_without_climber(pair[0])
                    use2 = self.board.can_use_without_climber(pair[1])
                    if use1 and use2:
                        selections[pair] = dices
                    elif use1:
                        selections[(pair[0], )] = [dices[0], dices[1]]
                    elif use2:
                        selections[(pair[1], )] = [dices[2], dices[3]]
            self.buttons.clear_widgets()
            if len(selections) > 0:
                for pair, dices in selections.items():
                    sel = Button(text='[color=' + RESET_COLOR + '][size=30]' + str(pair) + '[/size][/color]', markup=True)
                    sel.bind(on_press=self.make_selection_bind(pair, dices))
                    self.buttons.add_widget(sel)
                self.phase = Phase.SELECT
            else:
                self.phase = Phase.FAILED
        self.board.un_select()

    def make_selection_bind(self, pair, dices):
        def selection_bind(event):
            consume_climber = self.board.select(pair[0])
            if consume_climber:
                self.remaining_climbers -= 1
            self.dices.select(dices[0])
            self.dices.select(dices[1])
            if len(pair) > 1:
                consume_climber = self.board.select(pair[1])
                if consume_climber:
                    self.remaining_climbers -= 1
            self.phase = Phase.CHOOSE
        return selection_bind

    def on_remaining_climbers(self, _, value):
        self.climbers.text = '[color=888888][size=50]' + str(value) + '[/size][/color]'

    def on_phase(self, _, value):
        if self.phase == Phase.ROLL:
            self.label.text = '[color=ffd800][size=20]Roll dice[/size][/color]'
            self.play.disabled = False
            self.stop.disabled = True
        elif self.phase == Phase.ROLLING:
            self.label.text = '[color=ffd800][size=20]Rolling[/size][/color]'
            self.play.disabled = True
            self.stop.disabled = True
        elif self.phase == Phase.CHOOSE:
            self.buttons.clear_widgets()
            self.buttons.add_widget(self.play)
            self.buttons.add_widget(self.stop)
            self.label.text = '[color=ffd800][size=20]Continue or Stop[/size][/color]'
            self.play.text = '[color='+RESET_COLOR+'][size=30]PLAY[/size][/color]'
            self.play.disabled = False
            self.stop.disabled = False
        elif self.phase == Phase.FAILED:
            self.label.text = '[color=ffd800][size=20]FAILED!![/size][/color]'
            self.buttons.add_widget(self.play)
            self.buttons.add_widget(self.label)
            self.play.disabled = True
            self.stop.disabled = True
            Clock.schedule_once(self.fail_round, 1.)

    def play_round(self, event):
        self.phase = Phase.ROLLING
        self.dices.roll_dice(event)

    def stop_round(self, event):
        self.board.validate()
        self.label.text = '[color=ffd800][size=20]Next Player[/size][/color]'
        self.buttons.remove_widget(self.stop)
        self.buttons.add_widget(self.label)
        self.start_round()

    def fail_round(self, event):
        self.board.reset()
        self.start_round()
        self.phase = Phase.ROLL


class CantStopApp(App):
    title = 'Cant Stop'

    def build(self):
        return CantStopScreen()

    def on_pause(self):
        return True


if __name__ in ('__main__', '__android__'):
    if platform == 'win':
        Window.size = (960, 540)
    CantStopApp().run()
