import kivy
from kivy.app import App
from kivy.lang import Builder   
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

import os
from loges import Logger
from utils import Configs

Builder.load_string("""
<DataReader>:
    orientation:'vertical'
    size_hint:1,1
    canvas.before:
        Color:
            rgba:(1,1,1,1)
        Rectangle:
            pos:self.pos
            size:self.size
    AnchorLayout:
        anchor_x:'center'
        anchor_y:'center'
        BoxLayout:
            orientation:'vertical'
            size_hint:.3,.1
            padding:4
            spacing:4
            canvas.before:
                Color:
                    rgba:(.9,.9,.9,1)
                Rectangle:
                    pos:self.pos
                    size:self.size
            TextInput:
                id          : inp_txt
                text        : ''
                markup      : True
                multiline   : False
                size_hint   : 1,.5
                on_text_validate : root._on_text_change(self, self.text)
            
            Button:
                text:"Go"
                size_hint:None,None
                height:30
                width:50
                on_press:root.goNext()


""")
class DataReader(BoxLayout):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_parent(self, parent):
        self._main_parent = parent

    def focus_textinput(self, dt=None):
        self.ids.inp_txt.focus = True    

    def _get_video_file(self, barcode):
        files = {f.split(".")[0]:f for f in os.listdir(Configs.LCL_FOLDER)}
        if barcode in files.keys():
            return os.path.join(Configs.LCL_FOLDER, f"{files[barcode]}")
        else:
            return  None

    def _on_text_change(self, source, text):
        video_file = self._get_video_file(text)
        if video_file is not None:
            if not self._main_parent.videoplayer.is_active(video_file):
                self._main_parent.videoplayer.set_video_source(video_file)
                Logger.info(f"{video_file} set")
            source.text = ""
        
        else:
            Logger.info(f"{video_file} not found!")
            source.text = ""

    def goNext(self):
        self.parent.parent.current="scrn_video"

class DataReaderApp(App):
    def build(self):
        return DataReader()


if __name__=='__main__':

    DataReaderApp().run()

