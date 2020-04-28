from platform import python_version

import kivy

kivy.require('1.9.1')

from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.treeview import TreeView,  TreeViewNode
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window, platform
from os.path import join, dirname, isfile
import numpy as np
from json import load, dump

# KIVY LAUNCHER uses KIVY 1.9.1 and PYTHON 2.7.2 !!
# Things that DO NOT WORK with KIVY LAUNCHER (specific python 3)
# - Overriding App __init__
# - Formatted strings in Label: ie Label(text=f"toto{var}", ... (however, string concat works)

#############################################################################################
# Globals & constants
#############################################################################################

curdir = dirname(__file__)
cloud_image = Image(source=join(curdir, 'images', 'cloudysky.png'))
EPSILON = 0.01
FLOOR_ROCK = 1
FLOOR_MUD = 2
FLOOR_ICE = 3
CHARGE = 50
CHARGE_LOW = 51
VICTORY = 100
START = 200
GOLD = 201
WALL_N = 1000
WALL_S = 1001
WALL_W = 1002
WALL_E = 1003
FLOORS = {
    FLOOR_ROCK: (0.5, -0.4),
    FLOOR_MUD: (0.3, -0.3),
    FLOOR_ICE: (0.5, -0.6),
}
sm = ScreenManager()
# maps
with open(join(curdir, 'maps', 'maps.json')) as fd:
    maps = load(fd)
prefile = join(curdir, 'prefs.json')
with open(prefile) as fd:
    prefs = load(fd)


def unlock(level, score):
    save_progress = False  # temp
    prefs['coins'] += score
    current = prefs['current']
    if level > current:
        prefs['current'] = level
        if save_progress:
            with open(prefile, 'w') as fd:
                dump(prefs, fd)


#############################################################################################
# Intro
#############################################################################################
class Intro(Screen):
    def build(self):
        self.name = 'Intro'  # On donne un nom a l'ecran
        layout = FloatLayout()
        # Une image de fond:
        self.cloud_texture = cloud_image.texture
        self.cloud_texture.wrap = 'repeat'
        self.bgImage = Image(texture=self.cloud_texture, allow_stretch=True, keep_ratio=False)
        layout.add_widget(self.bgImage)
        self.speed = -0.2
        self.dy = 0.
        # labels
        self.grabing = False
        self.event = None
        layout.add_widget(Label(text='[color=ff0000][size=60sp]Touch the SKY[/size][/color]', markup=True, halign='center',
                                size_hint=(.5, .25), pos_hint={'x': .25, 'y': .7}))
        layout.add_widget(Label(text='[size=20sp]Kivy v.' + kivy.__version__ + '[/size]', markup=True,
                                halign='center', size_hint=(.5, .15), pos_hint={'x': .25, 'y': .45}))
        layout.add_widget(Label(text='[size=20sp]Python v.' + python_version() + '[/size]', markup=True,
                                halign='center', size_hint=(.5, .15), pos_hint={'x': .25, 'y': .55}))
        layout.add_widget(Label(text='[color=ff0000][size=30sp]Tap to start[/size][/color]', markup=True,
                                halign='center', size_hint=(.5, .15), pos_hint={'x': .25, 'y': .2}))
        self.add_widget(layout)

    def on_enter(self, *args):
        self.event = Clock.schedule_interval(self.scroll_textures, 1 / 60.)

    def on_leave(self, *args):
        self.event.cancel()

    def scroll_textures(self, time_passed):
        # Update the uvpos of the texture
        self.cloud_texture.uvpos = (self.cloud_texture.uvpos[0], (self.cloud_texture.uvpos[1] + time_passed * self.speed + self.dy) % self.width)

        # Redraw the texture
        texture = self.bgImage.property('texture')
        texture.dispatch(self.bgImage)

    def on_touch_down(self, touch):
        touch.grab(self)
        self.speed = 0
        self.grabing = False

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.dy = touch.dsy
            self.grabing = True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.speed = self.dy
            if not self.grabing:
                # switch to game screen
                sm.current = 'Menu'
            self.grabing = False


#############################################################################################
# Level Menu
#############################################################################################
class TreeViewButton(BoxLayout, TreeViewNode):
    def build(self, level, lock):
        self.level_no = level  # level field already exists in TreeViewNode
        desc = maps[level - 1]['desc']
        self.add_widget(Label(text='[color=ff0000][size=50]Level ' + str(level) + '[/size][/color]\n[color=ffffff][size=20]' + desc + '[/size][/color]', markup=True, halign='center'))
        self.im = Image(source=join(curdir, 'images', 'Lock.png' if lock else 'Play.png'))
        self.add_widget(self.im)
        if lock:
            self.disabled = True

    def rebuild(self, lock):
        self.is_selected = False
        if not lock and self.disabled:
            self.im.source = join(curdir, 'images', 'Play.png')
            self.disabled = False

    def on_touch_down(self, touch):
        super(TreeViewButton, self).on_touch_down(touch)
        # switch to game screen
        play = Playground()
        play.build(self.level_no)
        sm.add_widget(play)
        sm.current = 'Playground'


class Menu(Screen):
    def build(self):
        self.name = 'Menu'  # On donne un nom a l'ecran
        layout = BoxLayout(orientation='vertical')
        buttons = BoxLayout(size_hint_y=0.2)
        btn1 = Button(text='Levels')
        btn2 = Button(text='Customs')
        btn3 = Button(text='Options')
        buttons.add_widget(btn1)
        buttons.add_widget(btn2)
        buttons.add_widget(btn3)
        layout.add_widget(buttons)
        tv = TreeView(hide_root=True, size_hint_y=None)
        tv.bind(minimum_height=tv.setter('height'))
        cur_level = prefs['current']
        self.tvs = []
        for i in range(len(maps)):
            tvb = TreeViewButton()
            level = i + 1
            tvb.build(level, level > cur_level)
            self.tvs.append(tvb)
            tv.add_node(tvb)
        sv = ScrollView(bar_width=50, do_scroll_x=False)
        sv.add_widget(tv)
        layout.add_widget(sv)
        self.add_widget(layout)

    def rebuild(self):
        cur_level = prefs['current']
        for i in range(len(self.tvs)):
            tvb = self.tvs[i]
            level = i + 1
            tvb.rebuild(level > cur_level)


#############################################################################################
# Playground
#############################################################################################
def damper_it(value, damper_value):
    if value > EPSILON:
        value -= damper_value
        if value < EPSILON:
            value = 0
    elif value < -EPSILON:
        value += damper_value
        if value > -EPSILON:
            value = 0
    else:
        value = 0
    return value


class Circle(Rectangle):
    radius = 15
    stopped = False
    gravity = 200.
    force_x = 0
    force_y = 0
    speed_x = 0
    speed_y = 0
    speed_max = 300.
    damper = 400
    force_bounce = 800

    def build(self, x, y):
        self.radius = Window.size[0] / 30
        self.pos = (x - self.radius, y - self.radius)
        self.size = (self.radius * 2, self.radius * 2)

    def damper_force(self, dt):
        damper = self.damper * dt
        self.force_x = damper_it(self.force_x, damper)
        self.force_y = damper_it(self.force_y, damper)

    def update_speed(self, dt):
        self.speed_x += self.force_x * dt
        if self.speed_x > self.speed_max:
            self.speed_x = self.speed_max
        elif self.speed_x < -self.speed_max:
            self.speed_x = -self.speed_max
        self.speed_y += (self.force_y - self.gravity) * dt
        if self.speed_y > self.speed_max:
            self.speed_y = self.speed_max
        elif self.speed_y < -self.speed_max:
            self.speed_y = -self.speed_max

    def choc(self, damper, up):
        (damper_x, damper_y) = damper
        self.speed_x = damper_x * self.speed_x
        self.speed_y = damper_y * self.speed_y
        if up is not None:
            self.force_y = 0
            if up:
                self.speed_y = -abs(self.speed_y)
            else:
                self.speed_y = abs(self.speed_y)

    def bounce(self, target_x, target_y, charge):
        (x, y) = self.pos
        x += self.radius
        y += self.radius
        dx = abs(target_x - x)
        dy = abs(target_y - y)
        if dx < 2:
            slope = 1
        else:
            slope = dy / (dx + dy)
        if target_x > x:
            self.force_x = (1 - slope) * self.force_bounce * (charge + .1)
        else:
            self.force_x = -(1 - slope) * self.force_bounce * (charge + .1)
        self.force_y = slope * self.force_bounce * charge
        # impulse
        self.update_speed(1)

    def step(self, dt):
        if not self.stopped:
            (x, y) = self.pos
            self.update_speed(dt)
            x += self.speed_x * dt
            y += self.speed_y * dt
            self.damper_force(dt)
            self.pos = (x, y)

    def collide(self, got):
        (x, y) = self.pos
        # wall collision
        if WALL_N in got:
            (y, pixel) = got[WALL_N]
            y -= self.radius * 2
            self.choc(FLOORS[pixel], True)
        elif WALL_S in got:
            (y, pixel) = got[WALL_S]
            self.choc(FLOORS[pixel], False)
        # border collision
        if y < 0:
            y = 0
            self.choc((0.9, -0.6), False)
        elif y + self.radius * 2 > Window.size[1]:
            y = Window.size[1] - self.radius * 2
            self.choc((0.9, -0.6), True)
        if x < 0:
            x = 0
            self.choc((-0.7, 0.9), None)
        elif x + self.radius * 2 > Window.size[0]:
            x = Window.size[0] - self.radius * 2
            self.choc((-0.7, 0.9), None)
        self.pos = (x, y)


class Playground(Screen):

    circle = ObjectProperty(None, allownone=True)
    color = ObjectProperty(None, allownone=True)
    charge = NumericProperty(0)
    charged_low = BooleanProperty(False)
    coins = ListProperty()
    time = NumericProperty(0)
    score = NumericProperty(0)
    ending = -1

    def build(self, level):
        self.name = 'Playground'  # On donne un nom a l'ecran
        self.map = None
        self.background = None
        # score labels
        self.score_label = Label(text='[color=ffd800][size=20]Coins: 0[/size][/color]', markup=True, halign='left', size_hint=(.25, .15), pos_hint={'x': 0, 'y': .91})
        self.add_widget(self.score_label)
        self.time_label = Label(text='[color=ffd800][size=20]Time: 0[/size][/color]', markup=True, halign='left', size_hint=(.25, .15), pos_hint={'x': .5, 'y': .91})
        self.add_widget(self.time_label)
        # custom widget
        self.widget = Widget()
        self.widget.texture = Image(source=join(curdir, 'images', 'circle.png'), mipmap=True).texture
        self.add_widget(self.widget, 2)
        self.event = None
        # map
        self.level = level
        self.map = np.load(join(curdir, 'maps', 'map' + str(level) + '.npy'))
        # background
        image_file = join(curdir, 'maps', 'background' + str(level) + '.png')
        if not isfile(image_file):
            image_file = join(curdir, 'maps', 'map' + str(level) + '.png')
        self.background = Image(source=image_file, allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background, 3)

    def on_enter(self, *args):
        self.event = Clock.schedule_interval(self.step, 1 / 30.)
        # object placements
        self.scan_objects()
        self.timer = 0.

    def on_leave(self, *args):
        self.event.cancel()
        sm.remove_widget(self)

    def on_score(self, instance, value):
        self.score_label.text = '[color=ffd800][size=20]Coins: ' + str(value) + '[/size][/color]'

    def on_time(self, instance, value):
        self.time_label.text = '[color=ffd800][size=20]Time: ' + str(value) + '[/size][/color]'

    def scan_objects(self):
        texture_size = self.map.shape
        radius = int(Window.size[0] / 30)
        portal = False
        for y in range(texture_size[1]):
            for x in range(texture_size[0]):
                pixel = self.map[x, y]
                if pixel == 0:
                    continue
                if pixel == START and not debug_mode:
                    self.add_circle(x * Window.size[0] // texture_size[0], y * Window.size[1] // texture_size[1])
                elif pixel == GOLD:
                    self.add_gold(x * Window.size[0] // texture_size[0], y * Window.size[1] // texture_size[1], radius)
                elif pixel == VICTORY and not portal:
                    portal = True
                    self.add_portal(x * Window.size[0] // texture_size[0], y * Window.size[1] // texture_size[1])
                    if debug_mode:
                        self.add_circle(x * Window.size[0] // texture_size[0] - 50, y * Window.size[1] // texture_size[1] + 50)

    def scan_map(self, last_pos, new_pos, radius):
        (x1, y1) = last_pos
        (x2, y2) = new_pos
        # dx = x2 - x1
        dy = y2 - y1
        up = dy > 0
        # translate to texture coordinates
        image_size = self.background.size
        texture_size = self.map.shape
        x = int((x2 + radius) * texture_size[0] // image_size[0])
        oriy = int(y1 * texture_size[1] // image_size[1])
        r = int(2 * radius * texture_size[1] // image_size[1])
        # dx = int((dx + radius) * texture_size[0] // image_size[0])
        dy = int(dy * texture_size[1] // image_size[1])
        got = {}
        # scan collisions
        if up:
            for i in range(max(dy, 2)):
                y = oriy + r + i
                if y > texture_size[1] - 1:
                    continue
                pixel = self.map[x, y]
                if pixel == 0:
                    continue
                if pixel in FLOORS:
                    wall_y = y * image_size[1] // texture_size[1]
                    if wall_y < (y2 + 2 * radius):
                        got[WALL_N] = (wall_y, pixel)
                        break
        else:
            for i in range(max(abs(dy), 2)):
                y = oriy - i - 1
                if y < 0:
                    continue
                pixel = self.map[x, y]
                if pixel == 0:
                    continue
                if pixel in FLOORS:
                    wall_y = (y + 1) * image_size[1] // texture_size[1]
                    if wall_y > y2:
                        got[WALL_S] = (wall_y, pixel)
                        break
        # scan zone effects
        scany = r + abs(dy)
        if not up:
            oriy += dy
        for i in range(scany):
            y = oriy + i
            if y < 0 or y > texture_size[1] - 1:
                continue
            pixel = self.map[x, y]
            if pixel == CHARGE:
                got[CHARGE] = True
            elif pixel == CHARGE_LOW:
                got[CHARGE_LOW] = True
            elif pixel == VICTORY:
                got[VICTORY] = True
        return got

    def step(self, dt):
        if self.ending >= 0:
            self.on_step_victory(dt)
            return
        # Update timer
        self.timer += dt
        if int(self.timer) > self.time:
            self.time = int(self.timer)
        # Update animations
        if self.circle is not None:
            # Apply mvt + gravity
            last_pos = self.circle.pos
            self.circle.step(dt)
            # Detect if charged (near floor for now)
            got = self.scan_map(last_pos, self.circle.pos, self.circle.radius)
            if VICTORY in got:
                self.on_start_victory()
                return
            if CHARGE in got:
                if self.charge < 1:
                    self.charge += 2 * dt  # complete charge in 1/2 sec
                    if self.charge > 1:
                        self.charge = 1
                    self.color.v = .2 + (.8 * self.charge)
            elif self.charge > 0:
                self.charge -= 2 * dt  # complete charge in 1/2 sec
                if self.charge < 0:
                    self.charge = 0
                self.color.v = .2 + (.8 * self.charge)
            self.charged_low = CHARGE_LOW in got
            # compute collisions
            self.circle.collide(got)
            # coin collision: distance between circle and coin centers
            (circle_x, circle_y) = self.circle.pos
            circle_x += self.circle.radius
            circle_y += self.circle.radius
            hit = self.circle.radius * 1.25
            for coin in self.coins:
                (x, y) = coin.pos
                x += coin.size[0] / 2
                y += coin.size[1] / 2
                dist = ((x-circle_x)**2 + (y-circle_y)**2)**0.5
                if dist < hit:
                    self.coins.remove(coin)
                    self.remove_widget(coin)
                    self.score += 1
                    break

    def add_circle(self, x, y):
        with self.widget.canvas.before:
            self.color = Color(.95, .7, .2, mode='hsv')
            circle = Circle(texture=self.widget.texture)
            circle.build(x, y)
        self.circle = circle

    def add_gold(self, x, y, radius):
        pos = (x - radius, y - radius)
        coin = Image(source=join(curdir, 'images', 'coin.zip'), anim_delay=0.1, pos=pos, size_hint=(0.06, 0.06))
        self.coins.append(coin)
        self.add_widget(coin, 3)

    def add_portal(self, x, y):
        self.portal = Image(source=join(curdir, 'images', 'portal.gif'), anim_delay=0.1, pos=(x, y), size_hint=(0.12, 0.12))
        self.add_widget(self.portal, 3)

    def on_start_victory(self):
        self.ending = 0

    def on_end_victory(self):
        self.event.cancel()
        unlock(self.level + 1, self.score)
        victory.load(self.time, self.score)
        sm.current = 'Victory'
        menu.rebuild()

    def on_step_victory(self, dt):
        self.ending += dt
        # move to portal center
        if self.ending < 1:
            x, y = self.circle.pos
            target_x, target_y = self.portal.pos
            target_x += self.portal.width / 2 - self.circle.radius
            target_y += self.portal.height / 2 - self.circle.radius
            step = dt / (1. - self.ending)
            if step >= 1:
                self.circle.pos = (target_x, target_y)
            else:
                self.circle.pos = (x + (target_x - x) * step, y + (target_y - y) * step)
        # vanish
        elif self.ending < 2:
            step = (2. - self.ending) * 2
            ds = (self.circle.size[0] - self.circle.radius * step) / 2
            self.circle.size = (self.circle.radius * step, self.circle.radius * step)
            x, y = self.circle.pos
            self.circle.pos = (x + ds, y + ds)
        # end
        else:
            self.on_end_victory()

    def on_touch_down(self, touch):
        if self.ending >= 0:
            self.on_end_victory()
        elif self.circle is None:
            self.add_circle(touch.x, touch.y)
        elif self.charged_low or self.charge > 0:
            self.circle.bounce(touch.x, touch.y, self.charge)


#############################################################################################
# Victory
#############################################################################################
class Victory(Screen):
    time = NumericProperty(0)
    score = NumericProperty(0)
    total = NumericProperty(0)

    def build(self):
        self.name = 'Victory'  # On donne un nom a l'ecran
        layout = FloatLayout()
        # Une image de fond:
        self.cloud_texture = cloud_image.texture
        self.cloud_texture.wrap = 'repeat'
        self.bgImage = Image(texture=self.cloud_texture, allow_stretch=True, keep_ratio=False)
        layout.add_widget(self.bgImage)
        self.speed = -0.1
        # labels
        layout.add_widget(Image(source=join(curdir, 'images', 'treasure_chest.png'), size_hint=(.5, .5), pos_hint={'x': .25, 'y': .5}))
        self.time_label = Label(text='0', markup=True, halign='left', size_hint=(.25, .15), pos_hint={'x': .25, 'y': .4})
        layout.add_widget(self.time_label)
        self.score_label = Label(text='0', markup=True, halign='left', size_hint=(.25, .15), pos_hint={'x': .25, 'y': .3})
        layout.add_widget(self.score_label)
        layout.add_widget(Image(source=join(curdir, 'images', 'coin.zip'), anim_delay=0.1, size_hint=(.2, .2), pos_hint={'x': .75, 'y': .22}))
        self.total_label = Label(text='0', markup=True, halign='center', size_hint=(.25, .15), pos_hint={'x': .25, 'y': .2})
        layout.add_widget(self.total_label)
        self.add_widget(layout)
        self.event = None

    def load(self, time, score):
        self.score_label.text = '[color=ffd800][size=40sp]Coins gained: ' + str(score) + '[/size][/color]'
        self.time_label.text = '[color=ffd800][size=40sp]Time elapsed: ' + str(time) + '[/size][/color]'
        self.total_label.text = '[color=ffd800][size=40sp]Total Coins: ' + str(prefs['coins']) + '[/size][/color]'


    def on_enter(self, *args):
        self.event = Clock.schedule_interval(self.scroll_textures, 1 / 30.)

    def on_leave(self, *args):
        self.event.cancel()

    def scroll_textures(self, time_passed):
        # Update the uvpos of the texture
        self.cloud_texture.uvpos = (self.cloud_texture.uvpos[0], (self.cloud_texture.uvpos[1] + time_passed * self.speed) % self.width)

        # Redraw the texture
        texture = self.bgImage.property('texture')
        texture.dispatch(self.bgImage)

    def on_touch_up(self, touch):
        # switch to game screen
        sm.current = 'Menu'


#############################################################################################
# Screen & Application
#############################################################################################
intro = Intro()
menu = Menu()
victory = Victory()
debug_mode = False


class SkyKivyApp(App):
    # !!overriding __init__ crashes the android kivy launcher!!
    title = 'Touch the SKY'
    icon = 'icon.png'

    def build(self):
        Window.bind(on_keyboard=self.on_keyboard)
        intro.build()
        sm.add_widget(intro)
        menu.build()
        sm.add_widget(menu)
        victory.build()
        sm.add_widget(victory)
        if debug_mode:
            play = Playground()
            play.build(1)
            sm.add_widget(play)
            sm.current = 'Playground'
        else:
            sm.current = 'Intro'
        return sm

    def on_keyboard(self, window, keycode1, keycode2, text, modifiers):
        if keycode1 in [27, 1001]:
            if sm.current == 'Menu':
                sm.current = 'Intro'
                return True
            if sm.current == 'Playground':
                sm.current = 'Menu'
                return True
            if sm.current == 'Victory':
                sm.current = 'Menu'
                return True
        return False


if __name__ in ('__main__', '__android__'):
    if platform == 'win':
        Window.size = (540, 960)
    SkyKivyApp().run()
