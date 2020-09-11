from random import randint
from enum import Enum
from os.path import join, dirname

import kivy

kivy.require('1.9.1')

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import BooleanProperty, ObjectProperty, NumericProperty
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window, platform
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.utils import get_color_from_hex
from kivy.uix.screenmanager import ScreenManager, Screen

from cant_stop.players.player import Player
from cant_stop.game_logic.context import Context
from cant_stop.constants import CLIMBER_COUNT, DICE_COUNT, RESET_COLOR, RESET_DICE, SELECT_COLOR

# KIVY LAUNCHER uses KIVY version is 1.9.1 and PYTHON 2.7.2 !!

#############################################################################################
# Globals & constants
#############################################################################################

curdir = dirname(__file__)


def image_folder(file):
    return join(curdir, 'images', file)


circle_texture = Image(source=image_folder('circle.png'), mipmap=True).texture
sm = ScreenManager()


class Phase(Enum):
    ROLL = 1
    ROLLING = 2
    SELECT = 3
    CHOOSE = 4
    FAILED = 5


#############################################################################################
# Players
#############################################################################################

class PlayerLabel(Label):
    def __init__(self, player, **kwargs):
        super(PlayerLabel, self).__init__(text='[color=' + player.color + '][size=30]' + player.get_name() + '[/size][/color]', markup=True, halign='center', **kwargs)
        self.selected = False

    def on_size(self, *args):
        self._update()

    def on_pos(self, *args):
        self._update()

    def select(self, value):
        self.selected = value
        self._update()

    def _update(self):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.selected:
                Color(1, 1, 1, 1)
            else:
                Color(0, 0, 0, 0)
            Rectangle(pos=self.pos, size=self.size)


PLAYERS = (Player(1, '0000ff', True), Player(2, '00ff00', False), Player(3, 'ff00ff', False))


#############################################################################################
# Menu screen
#############################################################################################

class Menu(Screen):
    def build(self):
        self.name = 'Menu'  # On donne un nom a l'ecran
        layout = BoxLayout(orientation='vertical', spacing=10)
        title = Label(text="[color=ffd800][size=70]- CAN'T STOP -[/size][/color]", markup=True, halign='center', size_hint_y=0.3)
        layout.add_widget(title)
        for player in PLAYERS:
            buttons = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.2)
            player_label = Label(text='[color=' + player.color + '][size=50]' + player.get_name() + '[/size][/color]', markup=True, halign='center', size_hint_x=0.3)
            buttons.add_widget(player_label)
            human = ToggleButton(group=player.get_name(), state=('down' if player.human else 'normal'), text='[color='+RESET_COLOR+'][size=30]HUMAN[/size][/color]', markup=True, size_hint_x=0.3)
            buttons.add_widget(human)
            robot = ToggleButton(group=player.get_name(), state=('normal' if player.human else 'down'), text='[color='+RESET_COLOR+'][size=30]ROBOT[/size][/color]', markup=True, size_hint_x=0.3)
            buttons.add_widget(robot)
            human.bind(on_press=self.make_human(player))
            robot.bind(on_press=self.make_robot(player))
            layout.add_widget(buttons)
        play = Button(text='[color='+RESET_COLOR+'][size=30]PLAY[/size][/color]', markup=True, size_hint_y=0.2)
        play.bind(on_press=self.play)
        layout.add_widget(play)
        self.add_widget(layout)

    def play(self, event):
        sm.current = 'Playground'

    def make_human(self, player):
        def bind(instance):
            player.human = True
        return bind

    def make_robot(self, player):
        def bind(instance):
            player.human = False
        return bind


#############################################################################################
# Dices management
#############################################################################################

class DiceLayout(BoxLayout):
    ready = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(DiceLayout, self).__init__(orientation='vertical', **kwargs)
        self.dices = []
        for x in range(DICE_COUNT):
            dice = Dice()
            self.add_widget(dice)
            self.dices.append(dice)
        self.pairs = {}
        self.event = None
        self.animation_step = 0
        self.animation_time = 0

    def reset(self, dice):
        dice.text = dice.text.replace(SELECT_COLOR, RESET_COLOR)

    def select(self, dice):
        dice.text = dice.text.replace(RESET_COLOR, SELECT_COLOR)

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
        self.pairs = {}
        self.add_pairs(0, 1, 2, 3)
        self.add_pairs(0, 2, 1, 3)
        self.add_pairs(0, 3, 1, 2)
        return self.pairs

    def add_pairs(self, p11, p12, p21, p22):
        p1 = self.dices[p11].value + self.dices[p12].value
        p2 = self.dices[p21].value + self.dices[p22].value
        if p1 > p2:
            self.pairs[(p2, p1)] = (self.dices[p21], self.dices[p22], self.dices[p11], self.dices[p12])
        else:
            self.pairs[(p1, p2)] = (self.dices[p11], self.dices[p12], self.dices[p21], self.dices[p22])


class Dice(Label):
    def __init__(self, **kwargs):
        super(Dice, self).__init__(text='[color=' + RESET_COLOR + '][size=70]' + RESET_DICE + '[/size][/color]', markup=True, **kwargs)
        self.value = 0

    def update(self, value):
        self.value = value
        self.text = '[color=' + RESET_COLOR + '][size=70]' + str(value) + '[/size][/color]'


#############################################################################################
# Play board management
#############################################################################################

class BoardLayout(BoxLayout):
    def __init__(self, board, **kwargs):
        super(BoardLayout, self).__init__(orientation='horizontal', **kwargs)
        # Board
        self.board = board
        self.player_id = -1
        self.climbers = {}
        self.board_images = {}
        self.board_labels = {}
        self.event = None
        self.show_overlap = True
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

    def un_select(self):
        for label in self.board_labels.values():
            label.text = label.text.replace(SELECT_COLOR, RESET_COLOR)

    def pre_select(self, pair):
        self.board_labels[pair].text = self.board_labels[pair].text.replace(RESET_COLOR, SELECT_COLOR)

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
        # Compute overlap
        self.compute_overlap()
        # update UI
        self.update()
        return need_climber

    def compute_overlap(self):
        for k, n in self.climbers.items():
            li = self.board[k]
            player = -1
            for i, v in enumerate(li):
                if v == self.player_id:
                    player = i
                    break
            idx = min(player + n, len(li) - 1)
            if li[idx] != 0:
                self.start_animation()
                break
        else:
            self.stop_animation()

    def update(self):
        for k, li in self.board.items():
            player = -1
            for i, v in enumerate(li):
                if v == 0:
                    self.board_images[k][i].color = [1, 1, 1, 1]
                else:
                    if v == self.player_id:
                        player = i
                    self.board_images[k][i].color = get_color_from_hex(PLAYERS[v-1].color)
            if k in self.climbers:
                idx = min(player + self.climbers[k], len(li) - 1)
                if li[idx] == 0 or self.show_overlap:
                    self.board_images[k][min(player + self.climbers[k], len(li) - 1)].color = [1, 0, 0, 1]

    def reset(self):
        self.un_select()
        self.climbers = {}
        self.update()

    def validate(self):
        for k, v in self.climbers.items():
            li = self.board[k]
            for index, value in enumerate(li):
                if value == self.player_id:
                    li[index] = 0
                    li[min(index + v, len(li) - 1)] = self.player_id
                    break
            else:
                li[min(v - 1, len(li) - 1)] = self.player_id
        self.climbers = {}
        self.update()

    def start_animation(self):
        if self.event is None:
            self.event = Clock.schedule_interval(self.step_animation, 0.5)

    def step_animation(self, time_passed):
        self.show_overlap = not self.show_overlap
        self.update()

    def stop_animation(self):
        if self.event:
            self.event.cancel()
            self.event = None
        self.show_overlap = True

    def is_overlap(self):
        return self.event is not None


class CantStopLayout(BoxLayout, Context):
    phase = ObjectProperty(None)
    remaining_climbers = NumericProperty(CLIMBER_COUNT)

    def __init__(self, **kwargs):
        super(CantStopLayout, self).__init__(orientation='horizontal', **kwargs)
        self.player = None
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
        # Main panel
        panel = BoxLayout(orientation='vertical')
        player_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        self.player_labels = []
        for player in PLAYERS:
            player_label = PlayerLabel(player)
            self.player_labels.append(player_label)
            player_layout.add_widget(player_label)
        panel.add_widget(player_layout)
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
        panel.add_widget(self.board)
        # Button
        self.buttons = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.2)
        # self.play = Button(background_normal=image_folder('dices.png'), background_down=image_folder('dices.png'), background_disabled_normal=image_folder('dices.png'), background_color=(1, 1, 1, 1), size_hint_x=0.2)
        self.play = Button(text='[color='+RESET_COLOR+'][size=30]PLAY[/size][/color]', markup=True, size_hint_x=0.5)
        self.play.bind(on_press=self.play_round)
        self.buttons.add_widget(self.play)
        self.stop = Button(text='[color='+RESET_COLOR+'][size=30]STOP[/size][/color]', markup=True, size_hint_x=0.5)
        self.stop.bind(on_press=self.stop_round)
        # Help label
        self.label = Label(text='[color=ffd800][size=20]Launch dice[/size][/color]', markup=True, halign='left')
        self.buttons.add_widget(self.label)
        panel.add_widget(self.buttons)
        self.add_widget(panel)
        # Start game
        self.start_round()
        self.phase = Phase.ROLL

    def pre_select(self, pair, dices):
        self.board.pre_select(pair[0])
        self.dices.select(dices[0])
        self.dices.select(dices[1])
        if len(pair) > 1:
            self.board.pre_select(pair[1])

    def select(self, pair, dices):
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

    def print_label(self, text):
        self.label.text = '[color=' + self.player.color + '][size=30]' + self.player.get_name() + '[/size][/color] ' + text
        if self.label.parent is None:
            self.buttons.add_widget(self.label)

    def add_button(self, button):
        self.buttons.add_widget(button)

    def on_ready(self, _, value):
        self.board.un_select()
        if value:
            all_pairs = self.dices.get_all_pairs()
            selections = {}
            if self.remaining_climbers > 1:
                selections = all_pairs
            elif self.remaining_climbers == 1:
                for pair, dices in all_pairs.items():
                    if self.board.can_use_without_climber(pair[0]) or self.board.can_use_without_climber(pair[1]):
                        selections[pair] = dices
                    else:
                        selections[(pair[0], )] = (dices[0], dices[1])
                        selections[(pair[1], )] = (dices[2], dices[3])
            else:
                for pair, dices in all_pairs.items():
                    use1 = self.board.can_use_without_climber(pair[0])
                    use2 = self.board.can_use_without_climber(pair[1])
                    if use1 and use2:
                        selections[pair] = dices
                    elif use1:
                        selections[(pair[0], )] = (dices[0], dices[1])
                    elif use2:
                        selections[(pair[1], )] = (dices[2], dices[3])
            self.buttons.clear_widgets()
            if len(selections) > 0:
                self.player.select(self, selections)
                self.phase = Phase.SELECT
            else:
                self.phase = Phase.FAILED

    def on_remaining_climbers(self, _, value):
        self.climbers.text = '[color=888888][size=50]' + str(value) + '[/size][/color]'

    def on_phase(self, _, value):
        if self.phase == Phase.ROLL:
            if self.player.human:
                if self.play.parent is None:
                    self.buttons.add_widget(self.play)
                self.print_label('[color=ffd800][size=20]roll dices[/size][/color]')
            else:
                self.play_round(None)
        elif self.phase == Phase.ROLLING:
            self.print_label('[color=ffd800][size=20]rolling[/size][/color]')
            self.play.disabled = True
        elif self.phase == Phase.CHOOSE:
            is_overlap = self.board.is_overlap()
            remain_climber = self.remaining_climbers > 0
            self.play.disabled = False
            self.buttons.clear_widgets()
            if self.player.human:
                self.buttons.add_widget(self.play)
                if not remain_climber and not is_overlap:
                    self.buttons.add_widget(self.stop)
            else:
                if not remain_climber and not is_overlap:
                    self.player.choose(self)
                else:
                    self.play.trigger_action()
            if remain_climber:
                self.print_label("[color=ffd800][size=20]continue, some climbers left[/size][/color]")
            elif is_overlap:
                self.print_label("[color=ffd800][size=20]can't Stop, overlap[/size][/color]")
        elif self.phase == Phase.FAILED:
            self.print_label('[color=ffd800][size=20]has[/size] [/color][color=ff0000][size=20]FAILED[/size][/color]')
            self.play.disabled = True
            Clock.schedule_once(self.fail_round, 2.)

    def start_round(self):
        self.remaining_climbers = CLIMBER_COUNT
        next_player_id = 1 if self.player is None else self.player.id + 1
        if next_player_id > len(PLAYERS):
            next_player_id = 1
        self.player = PLAYERS[next_player_id - 1]
        self.board.player_id = self.player.id
        for i, p in enumerate(self.player_labels):
            p.select(self.player.id == i + 1)

    def play_round(self, event):
        self.phase = Phase.ROLLING
        self.dices.roll_dice(event)

    def stop_round(self, event):
        self.board.validate()
        self.buttons.clear_widgets()
        self.start_round()
        self.phase = Phase.ROLL

    def fail_round(self, event):
        self.board.reset()
        self.start_round()
        self.phase = Phase.ROLL


class CantStopScreen(Screen):
    def build(self):
        self.name = 'Playground'  # On donne un nom a l'ecran
        self.add_widget(CantStopLayout())


#############################################################################################
# Screen & Application
#############################################################################################
menu = Menu()
playground = CantStopScreen()


class CantStopApp(App):
    title = 'Cant Stop'

    def build(self):
        menu.build()
        sm.add_widget(menu)
        playground.build()
        sm.add_widget(playground)
        sm.current = 'Menu'
        return sm

    def on_pause(self):
        return True


if __name__ in ('__main__', '__android__'):
    if platform == 'win':
        Window.size = (960, 540)
    CantStopApp().run()
