from platform import python_version
import kivy
kivy.require('1.9.1')

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window, platform
from os.path import join, dirname

# KIVY LAUNCHER uses KIVY 1.9.1 and PYTHON 2.7.2 !!
# Things that DO NOT WORK with KIVY LAUNCHER (but work on desktop)
# - Overriding App __init__
# - Formatted strings in Label: ie Label(text=f"toto{var}", ... (however, string concat works)

curdir = dirname(__file__)


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
        super().on_touch_down(touch)
        print(self.children[1].text)


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
        for i in range(20):
            tvb = TreeViewButton()
            tvb.build('Level ' + str(i), i>3)
            #tv.add_node(TreeViewLabel(text='[color=ff0000][size=60]Level ' + str(i) + '[/size][/color]', markup=True, halign='center', size_hint=(1, .4)))
            tv.add_node(tvb)
        sv = ScrollView(bar_width=50, do_scroll_x=False)
        #sv = ScrollView(size_hint=(1, None), size=(Window.width, Window.height), bar_width=50, do_scroll_x=False)
        sv.add_widget(tv)
        layout.add_widget(sv)
        self.add_widget(layout)


sm = ScreenManager()
intro = Intro()
intro.build()
sm.add_widget(intro)
menu = Menu()
menu.build()
sm.add_widget(menu)


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
