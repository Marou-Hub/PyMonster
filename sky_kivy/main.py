from platform import python_version

import kivy

kivy.require('1.9.1')

from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty, BooleanProperty
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

# KIVY LAUNCHER uses KIVY 1.9.1 and PYTHON 2.7.2 !!
# Things that DO NOT WORK with KIVY LAUNCHER (specific python 3)
# - Overriding App __init__
# - Formatted strings in Label: ie Label(text=f"toto{var}", ... (however, string concat works)

#############################################################################################
# Globals & constants
#############################################################################################

curdir = dirname(__file__)
EPSILON = 0.01
WALL = 1
CHARGE = 2
VICTORY = 3
WALL_N = 1000
WALL_S = 1001
WALL_W = 1002
WALL_E = 1003
sm = ScreenManager()
# settings
cur_level = 1
max_level = 20


#############################################################################################
# Intro
#############################################################################################
class Intro(Screen):
    def build(self):
        self.name = 'Intro'  # On donne un nom a l'ecran
        layout = FloatLayout()
        # Une image de fond:
        cloud_image = Image(source=join(curdir, 'images', 'cloudysky.png'))
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
        self.level = level
        self.add_widget(Label(text='[color=ff0000][size=60]Level ' + str(level) + '[/size][/color]', markup=True, halign='center'))
        self.add_widget(Image(source=join(curdir, 'images', 'Lock.png' if lock else 'Play.png')))
        if lock:
            self.disabled = True

    def on_touch_down(self, touch):
        super(TreeViewButton, self).on_touch_down(touch)
        # switch to game screen
        play.load(self.level)
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
        for i in range(1, max_level):
            tvb = TreeViewButton()
            tvb.build(i, i > cur_level)
            tv.add_node(tvb)
        sv = ScrollView(bar_width=50, do_scroll_x=False)
        sv.add_widget(tv)
        layout.add_widget(sv)
        self.add_widget(layout)


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
    charge = 0

    def build(self, x, y):
        self.radius = Window.size[0] / 30
        self.pos = (x - self.radius, y - self.radius)
        self.size = (self.radius * 2, self.radius * 2)

    def increase_charge(self, dt):
        self.charge += 500 * dt  # complete charge in 1 sec
        if self.charge >= 100:
            self.charge = 100
            return True
        return False

    def decrease_charge(self, dt):
        self.charge -= 500 * dt
        if self.charge <= 0:
            self.charge = 0
            return True
        return False

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

    def choc(self, damper_x, damper_y):
        self.speed_x = damper_x * self.speed_x
        self.speed_y = damper_y * self.speed_y

    def bounce(self, target_x, target_y):
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
            self.force_x = (1 - slope) * self.force_bounce
        else:
            self.force_x = -(1 - slope) * self.force_bounce
        self.force_y = slope * self.force_bounce
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

    def collide(self, last_pos, got):
        (x, y) = self.pos
        _y = last_pos[1] + self.radius
        # wall collision
        if WALL_N in got:
            y = got[WALL_N] - self.radius * 2
            self.choc(0.9, -0.6)
        elif WALL_S in got:
            y = got[WALL_S]
            self.choc(0.9, -0.6)
        # border collision
        if y < 0:
            y = 0
            self.choc(0.9, -0.6)
        elif y + self.radius * 2 > Window.size[1]:
            y = Window.size[1] - self.radius * 2
            self.choc(0.9, -0.6)
        if x < 0:
            x = 0
            self.choc(-0.7, 0.9)
        elif x + self.radius * 2 > Window.size[0]:
            x = Window.size[0] - self.radius * 2
            self.choc(-0.7, 0.9)
        self.pos = (x, y)


class Playground(Screen):

    circle = ObjectProperty(None, allownone=True)
    color = ObjectProperty(None, allownone=True)
    charged = BooleanProperty(False)
    charging = BooleanProperty(False)

    def build(self):
        self.name = 'Playground'  # On donne un nom a l'ecran
        self.map = None
        self.background = None
        # custom widget
        widget = Widget()
        widget.texture = Image(source=join(curdir, 'images', 'circle.png'), mipmap=True).texture
        self.add_widget(widget)
        self.event = None

    def load(self, level):
        if self.background is not None:
            self.remove_widget(self.background)
        # map
        self.level = level
        self.map = np.load(join(curdir, 'maps', 'map' + str(level) + '.npy'))
        # background
        image_file = join(curdir, 'maps', 'background' + str(level) + '.png')
        if not isfile(image_file):
            image_file = join(curdir, 'maps', 'map' + str(level) + '.png')
        self.background = Image(source=image_file, allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background, 1)

    def on_enter(self, *args):
        self.event = Clock.schedule_interval(self.step, 1 / 30.)

    def on_leave(self, *args):
        self.event.cancel()

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
            for i in range(max(dy, 1)):
                y = oriy + r + i
                if y > texture_size[1]:
                    continue
                pixel = self.map[x, y]
                if pixel == 0:
                    continue
                if pixel == WALL:
                    wall_y = y * image_size[1] // texture_size[1]
                    if wall_y < (y2 + 2 * radius):
                        got[WALL_N] = wall_y
                        break
        else:
            for i in range(max(abs(dy), 1)):
                y = oriy - i - 1
                if y < 0:
                    continue
                pixel = self.map[x, y]
                if pixel == 0:
                    continue
                if pixel == WALL:
                    wall_y = (y + 1) * image_size[1] // texture_size[1]
                    if wall_y > y2:
                        got[WALL_S] = wall_y
                        break
        # scan zone effects
        scany = r + abs(dy)
        if not up:
            oriy += dy
        for i in range(scany):
            y = oriy + i
            pixel = self.map[x, y]
            if pixel == CHARGE:
                got[CHARGE] = True
        return got

    def step(self, dt):
        # Update animations
        if self.circle is not None:
            # Apply mvt + gravity
            last_pos = self.circle.pos
            self.circle.step(dt)
            # Detect if charged (near floor for now)
            got = self.scan_map(last_pos, self.circle.pos, self.circle.radius)
            if CHARGE in got:
                if not self.charged:
                    complete = self.circle.increase_charge(dt)
                    self.color.v = max(.2, self.circle.charge / 100)
                    self.charging = not complete
                    self.charged = complete
            elif self.charged or self.charging:
                complete = self.circle.decrease_charge(dt)
                self.color.v = max(.2, self.circle.charge / 100)
                self.charging = not complete
                self.charged = not complete
            # compute collisions
            self.circle.collide(last_pos, got)

    def add_circle(self, x, y):
        widget = self.children[0]
        with widget.canvas.before:
            self.color = Color(.95, .7, .2, mode='hsv')
            circle = Circle(texture=widget.texture)
            circle.build(x, y)
        self.circle = circle

    def on_touch_down(self, touch):
        if self.circle is None:
            self.add_circle(touch.x, touch.y)
        elif self.charged:
            self.circle.bounce(touch.x, touch.y)


#############################################################################################
# Screen & Application
#############################################################################################
intro = Intro()
menu = Menu()
play = Playground()


class SkyKivyApp(App):
    # !!overriding __init__ crashes the android kivy launcher!!
    title = 'Touch the SKY'
    icon = 'icon.png'

    def build(self):
        intro.build()
        sm.add_widget(intro)
        menu.build()
        sm.add_widget(menu)
        play.build()
        sm.add_widget(play)
        sm.current = 'Intro'
        return sm

    def on_pause(self):
        return True


if __name__ in ('__main__', '__android__'):
    if platform == 'win':
        Window.size = (540, 960)
    SkyKivyApp().run()
