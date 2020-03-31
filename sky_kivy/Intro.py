from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock


class Intro(FloatLayout):
    def __init__(self, **kwargs):
        super(Intro, self).__init__(**kwargs)
        # Une image de fond:
        self.cloud_image = Image(source='images/cloudysky.png')
        self.cloud_texture = self.cloud_image.texture
        self.cloud_texture.wrap = 'repeat'
        self.bgImage = Image(texture=self.cloud_texture, allow_stretch=True, keep_ratio=False)
        self.add_widget(self.bgImage)
        # labels
        self.add_widget(Label(text='[color=ff0000][size=60]Touch the SKY[/size][/color]', markup=True, halign='center',
                              size_hint=(.5, .25), pos_hint={'x':.25, 'y':.6}))
        self.add_widget(Label(text='[color=ff0000][size=30]Tap to start[/size][/color]', markup=True, halign='center',
                              size_hint=(.5, .15), pos_hint={'x':.25, 'y':.2}))

    def on_start(self):
        Clock.schedule_interval(self.scroll_textures, 1 / 60.)

    def scroll_textures(self, time_passed):
        # Update the uvpos of the texture
        self.cloud_texture.uvpos = ( self.cloud_texture.uvpos[0], (self.cloud_texture.uvpos[1] - time_passed/5.0)%self.width)

        # Redraw the texture
        texture = self.bgImage.property('texture')
        texture.dispatch(self.bgImage)
