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
from os.path import join, dirname
import struct

# KIVY LAUNCHER uses KIVY 1.9.1 and PYTHON 2.7.2 !!
# Things that DO NOT WORK with KIVY LAUNCHER (but work on desktop)
# - Overriding App __init__
# - Formatted strings in Label: ie Label(text=f"toto{var}", ... (however, string concat works)

curdir = dirname(__file__)
epsilon = 0.01
wall = [0., 0., 0., 1.]
charge = [1., 0., 0., 1.]
win = [0., 1., 0., 1.]


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
        layout.add_widget(Label(text='[color=ff0000][size=60]Touch the SKY[/size][/color]', markup=True, halign='center',
                                size_hint=(.5, .25), pos_hint={'x': .25, 'y': .7}))
        layout.add_widget(Label(text='[size=20]Kivy v.' + kivy.__version__ + '[/size]', markup=True,
                                halign='center', size_hint=(.5, .15), pos_hint={'x': .25, 'y': .45}))
        layout.add_widget(Label(text='[size=20]Python v.' + python_version() + '[/size]', markup=True,
                                halign='center', size_hint=(.5, .15), pos_hint={'x': .25, 'y': .55}))
        layout.add_widget(Label(text='[color=ff0000][size=30]Tap to start[/size][/color]', markup=True,
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


class TreeViewButton(BoxLayout, TreeViewNode):
    def build(self, text, lock):
        self.add_widget(Label(text='[color=ff0000][size=60]' + text + '[/size][/color]', markup=True, halign='center'))
        self.add_widget(Image(source=join(curdir, 'images', 'Lock.png' if lock else 'Play.png')))
        if lock:
            self.disabled = True

    def on_touch_down(self, touch):
        super(TreeViewButton, self).on_touch_down(touch)
        # switch to game screen
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
        max_level = 1
        for i in range(1, 20):
            tvb = TreeViewButton()
            tvb.build('Level ' + str(i), i > max_level)
            tv.add_node(tvb)
        sv = ScrollView(bar_width=50, do_scroll_x=False)
        sv.add_widget(tv)
        layout.add_widget(sv)
        self.add_widget(layout)


def damper_it(value, damper_value):
    if value > epsilon:
        value -= damper_value
        if value < epsilon:
            value = 0
    elif value < -epsilon:
        value += damper_value
        if value > -epsilon:
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

    def collide(self, last_pos, got_wall):
        (x, y) = self.pos
        _y = last_pos[1] + self.radius
        # wall collision
        if got_wall is not None:
            (got_wall_bt, got_wall_top) = got_wall
            if _y < got_wall_bt:
                y = got_wall_bt - self.radius * 2
            else:
                y = got_wall_top
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

    def build(self):
        self.name = 'Playground'  # On donne un nom a l'ecran
        # map + TODO background
        self.map = Image(source=join(curdir, 'images', 'map1.png'), allow_stretch=True, keep_ratio=False)
        self.add_widget(self.map)
        # custom widget
        widget = Widget()
        #widget._hue = 0.55
        #widget.bind(size=self.update_bounds, pos=self.update_bounds)
        widget.texture = Image(source=join(curdir, 'images', 'circle.png'), mipmap=True).texture
        self.add_widget(widget)
        self.init_physics()
        self.event = None

    def on_enter(self, *args):
        self.event = Clock.schedule_interval(self.step, 1 / 30.)

    def on_leave(self, *args):
        self.event.cancel()

    def init_physics(self):
        # create the space for physics simulation
        pass

    def scan_map(self, x, y, radius):
        # translate to texture coordinates
        image_size = self.map.size
        texture_size = self.map.texture.size
        x = int((x + radius) * texture_size[0] // image_size[0])
        y = int(y * texture_size[1] // image_size[1])
        dy = int(2 * radius * texture_size[1] // image_size[1])
        got_charge = False
        got_wall = None
        for i in range(dy):
            pixel = self.map.texture.get_region(x, y + i, 1, 1)
            bp = pixel.pixels
            data = struct.unpack('4B', bp)
            color = [c / 255.0 for c in data]
            if color == wall:
                if got_wall is None:
                    got_wall_bt = (y + i) * image_size[1] // texture_size[1]
                else:
                    got_wall_bt = got_wall[0]
                got_wall_top = (y + i + 1) * image_size[1] // texture_size[1]
                got_wall = (got_wall_bt, got_wall_top)
            got_charge = color == charge if not got_charge else True
        return got_wall, got_charge

    def step(self, dt):
        # Update animations
        if self.circle is not None:
            # Apply mvt + gravity
            last_pos = self.circle.pos
            self.circle.step(dt)
            # Detect if charged (near floor for now)
            (x, y) = self.circle.pos
            (got_wall, got_charge) = self.scan_map(x, y, self.circle.radius)
            if got_charge:
                if not self.charged:
                    self.color.v = 1
                    self.charged = True
            elif self.charged:
                self.color.v = .2
                self.charged = False
            # compute collisions
            self.circle.collide(last_pos, got_wall)

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


sm = ScreenManager()
intro = Intro()
intro.build()
sm.add_widget(intro)
menu = Menu()
menu.build()
sm.add_widget(menu)
play = Playground()
play.build()
sm.add_widget(play)


class SkyKivyApp(App):
    # !!overriding __init__ crashes the android kivy launcher!!
    title = 'Touch the SKY'
    icon = 'icon.png'

    def build(self):
        sm.current = 'Intro'
        return sm

    def on_pause(self):
        return True


if __name__ in ('__main__', '__android__'):
    if platform == 'win':
        Window.size = (540, 960)
    SkyKivyApp().run()
