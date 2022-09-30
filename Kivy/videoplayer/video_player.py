from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from loges import Logger

Builder.load_string("""
<ProdVideoPlayer>:
    orientation:'vertical'
    size_hint:1,1
    padding:0
    spacing:0
    canvas.before:
        Color:
            rgba:(1,1,1,1)
        Rectangle:
            pos:self.pos
            size:self.size
    BoxLayout:
        id:video_box
        orientation:'vertical'
        padding:1
        canvas.before:
            Color:
                rgba:(0,0,0,1)
            Rectangle:
                pos:self.pos
                size:self.size
        Video:
            id              : player
            state           : 'play'
            options         : {'eos':'loop'}
            allow_stretch   : True
            allow_fullscreen: True
            fullscreen      : True
            source          : "default.mp4"
            preview         : "preview.jpg"
            
        


""")

class ProdVideoPlayer(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vbox           = self.ids.video_box
        self._active_source = ""
        self.load_vplayer   ()

    def is_active(self, filename):
        """ return True if given file is currently active"""
        return True if filename == self._active_source else False

    def set_video_source(self, videosource):
        try:
            self._player.source = videosource
            self._active_source = videosource 
        except Exception as e:
            Logger.exception(e, "set_video_source", "video_player")

    def load_vplayer(self):
        self._player = self.ids.player


class VideoPlayerApp(App):
    def build(self):
        return ProdVideoPlayer()


if __name__ == '__main__':

    VideoPlayerApp().run()
