import kivy
kivy.require('1.9.1')

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window, platform
from os.path import join, dirname

# KIVY LAUNCHER uses KIVY version is 1.9.1
# Things that DO NOT WORK with KIVY LAUNCHER (but work on desktop)
# - Overriding App __init__
# - Formatted strings in Label: ie Label(text=f"toto{var}", ... (however, string concat works)


class Intro(FloatLayout):
    def __init__(self, **kwargs):
        super(Intro, self).__init__(**kwargs)
        # Une image de fond:
        curdir = dirname(__file__)
        cloud_image = Image(source=join(curdir, 'images', 'cloudysky.png'))
        self.cloud_texture = cloud_image.texture
        self.cloud_texture.wrap = 'repeat'
        self.bgImage = Image(texture=self.cloud_texture, allow_stretch=True, keep_ratio=False)
        self.add_widget(self.bgImage)
        self.speed = -0.2
        self.dy = 0.
        # labels
        self.grabing = False
        self.event = None
        self.add_widget(Label(text='[color=ff0000][size=60]Touch the SKY[/size][/color]', markup=True, halign='center', size_hint=(.5, .25), pos_hint={'x': .25, 'y': .6}))
        self.add_widget(Label(text='[color=ff0000][size=30]Version [/size][/color] '+kivy.__version__, markup=True, halign='center', size_hint=(.5, .15), pos_hint={'x': .25, 'y': .2}))

    def on_start(self):
        self.event = Clock.schedule_interval(self.scroll_textures, 1 / 60.)

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
        self.grabing = False


class SkyKivyApp(App):
    # !!overriding __init__ crashes the android kivy launcher!!
    title = 'Touch the SKY'
    icon = 'icon.png'

    def build(self):
        return Intro()

    def on_start(self):
        self.root.on_start()

    def on_pause(self):
        return True


if __name__ in ('__main__', '__android__'):
    if platform == 'win':
        Window.size = (540, 960)
    SkyKivyApp().run()
