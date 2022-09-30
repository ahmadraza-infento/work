
from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
Config.set('kivy', 'keyboard_mode', 'system'                        )
Config.set('kivy', 'window_icon', './assets/logo/logo.png'          )
Config.set('graphics', 'show_cursor', '1'                           )
Config.set('graphics', 'resizable',   '1'                           )
Config.set('graphics', 'borderless',  '0'                           )
Config.set('graphics', 'fullscreen',  '0'                           )
Config.set('graphics','window_state', 'maximized'                   )
Config.write()

from kivy.app import App
from loges import Logger
from kivy.clock import Clock
from video_player import ProdVideoPlayer
from data_reader import DataReader
from gdrive import DriveDownloader
from utils import Configs, JobScheduler
from kivy.uix.boxlayout import BoxLayout



Configs.init        ()
Logger.init("videoplayer", "s")
class MainWindow(BoxLayout):
    videoplayer = ProdVideoPlayer()
    datareader  = DataReader()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.scrn_video.add_widget  (self.videoplayer)
        self.ids.scrn_data.add_widget   (self.datareader)
        self.datareader.set_parent      (self)
        Clock.schedule_interval         (self.datareader.focus_textinput, 0.05)
    
        
class MainApp(App):

    def _download_videos(self, arg):
        try:
            self._drive_downloader.download_files()
        except Exception as e:
            Logger.exception(e, '_download_videos', 'main')

    def build(self):
        self._drive_downloader = DriveDownloader()
        JobScheduler.schedule(self._download_videos, Configs.SYNC_SPAN)
        return MainWindow   ()


if __name__=='__main__':

    MainApp().run()

