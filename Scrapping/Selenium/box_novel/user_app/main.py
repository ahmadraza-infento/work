from ast import Load
from tkinter import N
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button 
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.app import App


from utils import DataReader, Sync
from loges import Logger
import pyperclip


Logger.init ("istorian")
data_reader = DataReader()
Sync.init   ()

Builder.load_string(""" 
<Loading>:
    size_hint   : 0.25, 0.08
    auto_dismiss: True
    orientation : "vertical"
    padding     : 2
    canvas.before:
        Color: 
            rgba: (.9, .9, .9, 0)
        Rectangle: 
            pos : self.pos
            size: self.size
    BoxLayout:
        orientation : "horizontal"
        size_hint_x : 1
        size_hint_y : 1
        padding     : 3
        spacing     : 3
        canvas.before:
            Color: 
                rgba:(1,1,1,0)
            Rectangle: 
                pos:self.pos
                size:self.size
        Label:
            id          : lbl
            font_size   : 18
            text        : ""    
""")
class Loading(ModalView):
    _self = None

    @classmethod
    def show(cls, callback, text=None):
        if cls._self is None:
            cls._self = Loading()

        cls._self._callback = callback
        if text is not None:
            cls._self.ids.lbl.text = text
        else:
            cls._self.ids.lbl.text = "Loading - Please wait..."
        cls._self.open()

    @classmethod
    def close(cls):
        if cls._self is not None:
            cls._self.dismiss()
            if cls._self._callback is not None:
                cls._self._callback()

    def __init__(self, **kwargs):
        super(Loading, self).__init__(**kwargs)
        self._callback = None


Builder.load_string("""
<Chapter>
    orientation:"horizontal"
    background_color:0,0,0,0
    size_hint_x:1
    size_hint_y:None
    height:100
    text_size:self.size
    padding:1
    canvas.before:
        Color:
            rgba:(128/255,191/255,255/255,1)if self.state=='normal' else (0,153/255,150/255,1)
        RoundedRectangle:
            pos:self.pos
            size:self.size 
            radius:[10]
    on_release:root.on_box_clicked()
    BoxLayout:
        orientation:'vertical'
        size_hint_x:.7
        size_hint_y:1
        padding_x:2
        spacing:2
        BoxLayout:
            id:description_box
            size_hint_x:1
            size_hint_y:.7
            padding:2
            Label:
                id:event_desc
                text:""
                font_size:18
                bold:True
                text_size:self.size
                halign:'left'
                valign:'middle'
                color:(0,0,0,1)
        
        BoxLayout:
            id:datetime_box
            size_hint_x:1
            size_hint_y:.3
            padding:2
            Label:
                id:event_dt
                text:""
                font_size:17
                text_size:self.size
                halign:'left'
                color:(0,0,0,1)
    
    BoxLayout:
        id:days_box
        size_hint_x:.3
        size_hint_y:1
        Label:
            id:event_leftdt
            text:""
            font_size:17 
            bold:True
            text_size:self.size
            halign:'left'
            valign:'middle'
            color:(0,0,0,1)
""")
class Chapter(BoxLayout, Button, ButtonBehavior):
    def __init__(self, parent, data, **kwargs):
        super().__init__(**kwargs)

        self._parent = parent
        self._set_values(data)

    def _set_values(self, data):
        """ set values for event box """
        self._id                = data['logid']
        self._copied_count      = int(data['copied'])
        self.ids.event_desc.text= data['chaptername']
        self.ids.event_dt.text  = "Again Copy" if data['copied'] > 0 else "Copy"
        self.ids.event_leftdt.text= f"Released: {data['releaseddate']}"

    def on_box_clicked(self):
        def callback(dt):
            Loading.close()

        content         = data_reader.read_chapter_content(self._id, self._copied_count)
        if content is not None:
            pyperclip.copy  (content)
            Loading.show(None, text="Content Copied")
            Clock.schedule_once(callback, 0.5)

        else:
            print("content is not available")

Builder.load_string(""" 
<NextButton>:
    background_color:0,0,0,0
    canvas.before:
        Color:
            rgba:(128/255,191/255,255/255,1)if self.state=='normal' else (0,153/255,150/255,1)
        RoundedRectangle:
            pos:self.pos
            size:self.size 
            radius:[10]
    size_hint_x : 1
    size_hint_y : None
    height      : 100
    text        : "Next"
    color       : (0, 0, 0, 1)
    font_size   : 18
""")
class NextButton(BoxLayout, Button, ButtonBehavior):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

Builder.load_string("""
<Chapters>:
    id:events_window
    size_hint_y:1
    size_hint_x:1
    orientation:"vertical"
    canvas.before:
        Color:
            rgba:(0,0,0,1)
        Rectangle:
            pos:self.pos
            size:self.size
    BoxLayout:
        orientation:"vertical"
        size_hint_x:1
        size_hint_y:1
        spacing:1
        padding:2
        canvas.before:
            Color:
                rgba:(1,1,1,1)
            Rectangle:
                pos:self.pos
                size:self.size
        BoxLayout:
            id:heading
            size_hint_x:1
            size_hint_y:.08
            canvas.before:
                Color:
                    rgba:(1,1,1,1)
                Rectangle:
                    pos:self.pos
                    size:self.size
            Label:
                text :"Chapters"
                color:(0,153/255,153/255,1)
                bold :True
                font_size:20
    
        BoxLayout:
            id:detail_box
            orientation:'vertical'
            size_hint_x:1
            size_hint_y:1
            spacing:1
            padding:1
            canvas.before:
                Color:
                    rgba:(.9,.9,.9,.9)
                Rectangle:
                    pos:self.pos
                    size:self.size
            # scrollview
            ScrollView:
                do_scroll_x: False
                do_scroll_y: True
                size_hint_y:1
                bar_width:10
                bar_color: 0, 0, 0, .5 
                effect_cls: "ScrollEffect"
                scroll_type: ['bars', 'content']
                GridLayout:
                    id:gd_events
                    height:self.minimum_height
                    cols:1
                    size_hint_y: None
                    spacing:2
                    padding_y:1
""")
class Chapters(BoxLayout):
    def __init__(self, parent,**kwargs):
        super(Chapters, self).__init__(**kwargs)
        self._parent = parent

    def load_chapters(self, storyid):
        self._storyid = storyid
        self.ids.gd_events.clear_widgets()
        sources = data_reader.read_chapters(storyid)
        nb = NextButton()
        nb.bind(on_release=self._next_button)
        if sources is not None:
            if len(sources) > 0:
                for source in sources:
                    c = Chapter(self._parent, source)
                    self.ids.gd_events.add_widget(c)
            else:
                nb.text = "Back"
                data_reader.reset_count("chapters")
        else:
            nb.text = "Back"
            data_reader.reset_count("chapters")
        self.ids.gd_events.add_widget(nb)
        
    
    def _next_button(self, source=None):
        self.load_chapters(self._storyid)


Builder.load_string(""" 
<StoryChapters>:
    size_hint_y: 1
    size_hint_x: 1
    orientation: "vertical"
    BoxLayout:
        orientation : "vertical"
        size_hint_x : 1
        size_hint_y : 1
        spacing     : 1
        padding     : 2
        canvas.before:
            Color:
                rgba    : (1, 1, 1 , 1)
            Rectangle:
                pos     : self.pos
                size    : self.size   
                        
        BoxLayout:
            id:working_area
            size_hint_x:1
            size_hint_y:1
            orientation:'vertical'
            canvas.before:
                Color:
                    rgba:(.9,.9,.9,.9)
                Rectangle:
                    pos:self.pos
                    size:self.size
""")    
class StoryChapters(BoxLayout):
    def __init__(self, main_parent, storyid, **kwargs):
        super(StoryChapters, self).__init__(**kwargs)
        self.working_box    = self.ids.working_area
        self._main_parent   = main_parent
        self._storyid       = storyid
        Loading.show        (None)
        Clock.schedule_once (self._start_loading, 0.5)

    def _start_loading(self, dt):
        self.load_chapters()
        Loading.close()

    def load_chapters(self):
        self.working_box.clear_widgets  ()
        self.chapters                   = vars(self).get("chapters", Chapters(self._main_parent))
        self.working_box.add_widget     ( self.chapters )
        self.chapters.load_chapters     (self._storyid)



Builder.load_string("""
<Story>
    orientation:"horizontal"
    background_color:0,0,0,0
    size_hint_x:1
    size_hint_y:None
    height:100
    text_size:self.size
    padding:1
    canvas.before:
        Color:
            rgba:(128/255,191/255,255/255,1)if self.state=='normal' else (0,153/255,150/255,1)
        RoundedRectangle:
            pos:self.pos
            size:self.size 
            radius:[10]
    on_release:root.on_box_clicked()
    BoxLayout:
        orientation:'vertical'
        size_hint_x:.7
        size_hint_y:1
        padding_x:2
        spacing:2
        BoxLayout:
            id:description_box
            size_hint_x:1
            size_hint_y:.7
            padding:2
            Label:
                id:event_desc
                text:"Description Here"
                font_size:18
                bold:True
                text_size:self.size
                halign:'left'
                valign:'middle'
                color:(0,0,0,1)
        
        BoxLayout:
            id:datetime_box
            size_hint_x:1
            size_hint_y:.3
            padding:2
            Label:
                id:event_dt
                text:"12-01-2022 14:12:09"
                font_size:17
                text_size:self.size
                halign:'left'
                color:(0,0,0,1)
    
    BoxLayout:
        id:days_box
        size_hint_x:.3
        size_hint_y:1
        Label:
            id:event_leftdt
            text:"3 Days left"
            font_size:17 
            bold:True
            text_size:self.size
            halign:'left'
            valign:'middle'
            color:(0,0,0,1)
""")
class Story(BoxLayout, Button, ButtonBehavior):
    def __init__(self, parent, data, **kwargs):
        super().__init__(**kwargs)

        self._parent = parent
        self._set_values(data)

    def _set_values(self, data):
        """ set values for event box """
        self._id                    = data['id']
        self.ids.event_desc.text    = f"{data['name']}"
        self.ids.event_dt.text      = f"{data['source']}"
        self.ids.event_leftdt.text  = "Latest Update: 2 hours Ago"

    def on_box_clicked(self):
        self._parent.load_story_chapters(self._id)

        
Builder.load_string("""
<Stories>:
    id:events_window
    size_hint_y:1
    size_hint_x:1
    orientation:"vertical"
    canvas.before:
        Color:
            rgba:(0,0,0,1)
        Rectangle:
            pos:self.pos
            size:self.size
    BoxLayout:
        orientation:"vertical"
        size_hint_x:1
        size_hint_y:1
        spacing:1
        padding:2
        canvas.before:
            Color:
                rgba:(1,1,1,1)
            Rectangle:
                pos:self.pos
                size:self.size
        BoxLayout:
            id:heading
            size_hint_x:1
            size_hint_y:.08
            canvas.before:
                Color:
                    rgba:(1,1,1,1)
                Rectangle:
                    pos:self.pos
                    size:self.size
            Label:
                text :"Stories"
                color:(0,153/255,153/255,1)
                bold :True
                font_size:20
    
        BoxLayout:
            id:detail_box
            orientation:'vertical'
            size_hint_x:1
            size_hint_y:1
            spacing:1
            padding:1
            canvas.before:
                Color:
                    rgba:(.9,.9,.9,.9)
                Rectangle:
                    pos:self.pos
                    size:self.size
            # scrollview
            ScrollView:
                do_scroll_x: False
                do_scroll_y: True
                size_hint_y:1
                bar_width:10
                bar_color: 0, 0, 0, .5 
                effect_cls: "ScrollEffect"
                scroll_type: ['bars', 'content']
                GridLayout:
                    id:gd_events
                    height:self.minimum_height
                    cols:1
                    size_hint_y: None
                    spacing:2
                    padding_y:1
""")
class Stories(BoxLayout):
    def __init__(self, parent,**kwargs):
        super(Stories, self).__init__(**kwargs)
        self._parent = parent

    def load_stories(self, source):
        self._source = source
        self.ids.gd_events.clear_widgets()
        stories = data_reader.read_stories(source)
        nb = NextButton()
        nb.bind(on_release=self._next_button)
        if stories is not None:
            if len(stories) >0:
                for story in stories:
                    s = Story(self._parent, story)
                    self.ids.gd_events.add_widget(s)
            else:
                nb.text = "Back" 
                data_reader.reset_count("stories")
        else:
            nb.text = "Back" 
            data_reader.reset_count("stories")
        
        self.ids.gd_events.add_widget(nb)
    
    def _next_button(self, source=None):
        self.load_stories(self._source)

Builder.load_string(""" 
<SourceStories>:
    size_hint_y: 1
    size_hint_x: 1
    orientation: "vertical"
    BoxLayout:
        orientation : "vertical"
        size_hint_x : 1
        size_hint_y : 1
        spacing     : 1
        padding     : 2
        canvas.before:
            Color:
                rgba    : (1, 1, 1 , 1)
            Rectangle:
                pos     : self.pos
                size    : self.size   
                        
        BoxLayout:
            id:working_area
            size_hint_x:1
            size_hint_y:1
            orientation:'vertical'
            canvas.before:
                Color:
                    rgba:(.9,.9,.9,.9)
                Rectangle:
                    pos:self.pos
                    size:self.size
""")    
class SourceStories(BoxLayout):
    def __init__(self, main_parent, source, **kwargs):
        super(SourceStories, self).__init__(**kwargs)
        self.working_box    = self.ids.working_area
        self._main_parent   = main_parent
        self._source        = source
        Loading.show        (None)
        Clock.schedule_once(self.set_loading, 0.5)

    def set_loading(self, dt):
        self.load_stories   (self._source)
        Loading.close       ()

    def load_stories(self, source):
        self.working_box.clear_widgets()
        self._widget                = vars(self).get("stories", Stories(self._main_parent))
        self.working_box.add_widget (self._widget)
        self._widget.load_stories   (source)


Builder.load_string("""
<Source>
    orientation:"horizontal"
    background_color:0,0,0,0
    size_hint_x:1
    size_hint_y:None
    height:100
    text_size:self.size
    padding:1
    canvas.before:
        Color:
            rgba:(128/255,191/255,255/255,1)if self.state=='normal' else (0,153/255,150/255,1)
        RoundedRectangle:
            pos:self.pos
            size:self.size 
            radius:[10]
    on_release:root.on_box_clicked()
    BoxLayout:
        orientation:'vertical'
        size_hint_x:.7
        size_hint_y:1
        padding_x:2
        spacing:2
        BoxLayout:
            id:description_box
            size_hint_x:1
            size_hint_y:.7
            padding:2
            Label:
                id:event_desc
                text:""
                font_size:18
                bold:True
                text_size:self.size
                halign:'left'
                valign:'middle'
                color:(0,0,0,1)
        
        BoxLayout:
            id:datetime_box
            size_hint_x:1
            size_hint_y:.3
            padding:2
            Label:
                id:event_dt
                text:""
                font_size:17
                text_size:self.size
                halign:'left'
                color:(0,0,0,1)
    
    BoxLayout:
        id:days_box
        size_hint_x:.3
        size_hint_y:1
        Label:
            id:event_leftdt
            text:""
            font_size:17 
            bold:True
            text_size:self.size
            halign:'left'
            valign:'middle'
            color:(0,0,0,1)
""")
class Source(BoxLayout, Button, ButtonBehavior):
    def __init__(self, parent, data, **kwargs):
        super().__init__(**kwargs)

        self._parent = parent
        self._set_values(data)

    def _set_values(self, data):
        """ set values for event box """
        self._id                    = data['source']
        self.ids.event_desc.text    = data['source']
        self.ids.event_dt.text      = f"{data['story_count']} Stories"
        self.ids.event_leftdt.text  = f"More Info"

    def on_box_clicked(self):
        def callback(result):
            pass

        self._parent.load_source_stories(self._id)

Builder.load_string("""
<Sources>:
    id:events_window
    size_hint_y:1
    size_hint_x:1
    orientation:"vertical"
    canvas.before:
        Color:
            rgba:(0,0,0,1)
        Rectangle:
            pos:self.pos
            size:self.size
    BoxLayout:
        orientation:"vertical"
        size_hint_x:1
        size_hint_y:1
        spacing:1
        padding:2
        canvas.before:
            Color:
                rgba:(1,1,1,1)
            Rectangle:
                pos:self.pos
                size:self.size
        BoxLayout:
            id:heading
            size_hint_x:1
            size_hint_y:.08
            canvas.before:
                Color:
                    rgba:(1,1,1,1)
                Rectangle:
                    pos:self.pos
                    size:self.size
            Label:
                text :"Sources"
                color:(0,153/255,153/255,1)
                bold :True
                font_size:20
    
        BoxLayout:
            id:detail_box
            orientation:'vertical'
            size_hint_x:1
            size_hint_y:1
            spacing:1
            padding:1
            canvas.before:
                Color:
                    rgba:(.9,.9,.9,.9)
                Rectangle:
                    pos:self.pos
                    size:self.size
            # scrollview
            ScrollView:
                do_scroll_x: False
                do_scroll_y: True
                size_hint_y:1
                bar_width:10
                bar_color: 0, 0, 0, .5 
                effect_cls: "ScrollEffect"
                scroll_type: ['bars', 'content']
                GridLayout:
                    id:gd_events
                    height:self.minimum_height
                    cols:1
                    size_hint_y: None
                    spacing:2
                    padding_y:1
""")
class Sources(BoxLayout):
    def __init__(self, parent,**kwargs):
        super(Sources, self).__init__(**kwargs)
        self._parent = parent

    def load_sources(self):
        self.ids.gd_events.clear_widgets()
        self._sources = data_reader.read_sources()
        if self._sources is not None:
            for source in self._sources:
                e = Source(self._parent, source)
                self.ids.gd_events.add_widget(e)

Builder.load_string(""" 
<StorySources>:
    size_hint_y: 1
    size_hint_x: 1
    orientation: "vertical"
    BoxLayout:
        orientation : "vertical"
        size_hint_x : 1
        size_hint_y : 1
        spacing     : 1
        padding     : 2
        canvas.before:
            Color:
                rgba    : (1, 1, 1 , 1)
            Rectangle:
                pos     : self.pos
                size    : self.size   
                        
        BoxLayout:
            id:working_area
            size_hint_x:1
            size_hint_y:1
            orientation:'vertical'
            canvas.before:
                Color:
                    rgba:(.9,.9,.9,.9)
                Rectangle:
                    pos:self.pos
                    size:self.size
""")    
class StorySources(BoxLayout):
    def __init__(self, main_parent, **kwargs):
        super(StorySources, self).__init__(**kwargs)
        self.working_box    = self.ids.working_area
        self._main_parent   = main_parent
        self.load_sources   ()

    def load_sources(self):
        self.working_box.clear_widgets  ()
        self.sources                    = vars(self).get("sources", Sources(self._main_parent))
        self.working_box.add_widget     ( self.sources )
        self.sources.load_sources       ()


Builder.load_string(""" 
<IStorian>:
    id          : main_window
    size_hint_x : 1
    size_hint_y : 1
    title       : "IStorian"
    canvas.before:
        Color:
            rgba:(0,0,0,1)
        Rectangle:
            pos:self.pos
            size:self.size
    BoxLayout:
        id          : main_box
        orientation : "vertical"
        size_hint_x : 1
        size_hint_y : 1
        spacing     : 1
        padding     : 2

        canvas.before:
            Color:
                rgba: (1,1,1,1)
            Rectangle:
                pos : self.pos
                size: self.size
""")
class IStorian(BoxLayout):
    def __init__(self, **kwargs):
        super(IStorian, self).__init__(**kwargs)
        self.main_box = self.ids.main_box
        self.load_story_sources()

    def load_story_chapters(self, storyid):
        self.main_box.clear_widgets()
        self.schapters = vars(self).get("schapters", StoryChapters(self, storyid))
        self.main_box.add_widget(self.schapters)

    def load_story_sources(self):
        self.main_box.clear_widgets()
        self.sources = vars(self).get("sources", StorySources(self))
        self.main_box.add_widget(self.sources)

    def load_source_stories(self, source):
        self.main_box.clear_widgets()
        self.sstories = vars(self).get("sstories", SourceStories(self, source))
        self.main_box.add_widget(self.sstories)

class IStorianApp(App):
    def build(self):
        self.title = 'Stories For You'
        return IStorian()

if __name__=="__main__":
    IStorianApp().run()