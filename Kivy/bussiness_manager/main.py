from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button 
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.app import App


from utils import AppData
from loges import Logger


Logger.init ("BussinessManager")
app_data    = AppData()

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
<BussinessEntry>
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
class BussinessEntry(BoxLayout, Button, ButtonBehavior):
    def __init__(self, parent, data, **kwargs):
        super().__init__(**kwargs)

        self._parent = parent
        self._set_values(data)

    def _set_values(self, data):
        """ set values for event box """
        self._id                    = data['id']
        self.ids.event_desc.text    = f"{data['detail']}"
        self.ids.event_dt.text      = f"{data['amount']}"
        self.ids.event_leftdt.text  = "Latest Update: 2 hours Ago"

    def on_box_clicked(self):
        self._parent.load_story_chapters(self._id)

        
Builder.load_string("""
<BussinessEntries>:
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
                text :"Entries"
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
class BussinessEntries(BoxLayout):
    def __init__(self, parent,**kwargs):
        super(BussinessEntries, self).__init__(**kwargs)
        self._parent = parent

    def load_entries(self, source):
        self._source = source
        self.ids.gd_events.clear_widgets()
        entries = app_data.bussiness_entries(source)
        nb = NextButton()
        nb.bind(on_release=self._next_button)
        if entries is not None:
            if len(entries) >0:
                for entry in entries:
                    s = BussinessEntry(self._parent, entry)
                    self.ids.gd_events.add_widget(s)
            else:
                nb.text = "Back" 
                app_data.reset_cursor("entries")
        else:
            nb.text = "Back" 
            app_data.reset_cursor("entries")
        
        self.ids.gd_events.add_widget(nb)
    
    def _next_button(self, source=None):
        self.load_entries(self._source)

Builder.load_string(""" 
<BussinessDetail>:
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
class BussinessDetail(BoxLayout):
    def __init__(self, main_parent, source, **kwargs):
        super(BussinessDetail, self).__init__(**kwargs)
        self.working_box    = self.ids.working_area
        self._main_parent   = main_parent
        self._source        = source
        Loading.show        (None)
        Clock.schedule_once(self.set_loading, 0.5)

    def set_loading(self, dt):
        self.load_entries   (self._source)
        Loading.close       ()

    def load_entries(self, source):
        self.working_box.clear_widgets()
        self._widget                = vars(self).get("bentries", BussinessEntries(self._main_parent))
        self.working_box.add_widget (self._widget)
        self._widget.load_entries   (source)



Builder.load_string("""
<Bussiness>
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
class Bussiness(BoxLayout, Button, ButtonBehavior):
    def __init__(self, parent, data, **kwargs):
        super().__init__(**kwargs)

        self._parent = parent
        self._set_values(data)

    def _set_values(self, data):
        """ set values for event box """
        self._id                    = data['id']
        self.ids.event_desc.text    = data['name']
        self.ids.event_dt.text      = f"22 Stories"
        self.ids.event_leftdt.text  = f"More Info"

    def on_box_clicked(self):
        def callback(result):
            pass

        self._parent.load_bussiness_detail(self._id)

Builder.load_string("""
<Bussinesses>:
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
class Bussinesses(BoxLayout):
    def __init__(self, parent,**kwargs):
        super(Bussinesses, self).__init__(**kwargs)
        self._parent = parent

    def load(self):
        self.ids.gd_events.clear_widgets()
        self._sources = app_data.bussinesses
        if self._sources is not None:
            for source in self._sources:
                e = Bussiness(self._parent, source)
                self.ids.gd_events.add_widget(e)

Builder.load_string(""" 
<BussinessScreen>:
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
class BussinessScreen(BoxLayout):
    def __init__(self, main_parent, **kwargs):
        super(BussinessScreen, self).__init__(**kwargs)
        self.working_box    = self.ids.working_area
        self._main_parent   = main_parent
        self.load           ()

    def load(self):
        self.working_box.clear_widgets  ()
        self.bussinesses                = vars(self).get("bussinesses", Bussinesses(self._main_parent))
        self.working_box.add_widget     ( self.bussinesses )
        self.bussinesses.load           ()


Builder.load_string(""" 
<BussinessManager>:
    id          : main_window
    size_hint_x : 1
    size_hint_y : 1
    title       : "Bussiness Manager"
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
class BussinessManager(BoxLayout):
    def __init__(self, **kwargs):
        super(BussinessManager, self).__init__(**kwargs)
        self.main_box = self.ids.main_box
        self.load_bussinesses()

    def load_bussiness_detail(self, storyid):
        self.main_box.clear_widgets()
        self.bdetail = vars(self).get("bdetail", BussinessDetail(self, storyid))
        self.main_box.add_widget(self.bdetail)

    def load_bussinesses(self):
        self.main_box.clear_widgets()
        self.bscreen = vars(self).get("bscreen", BussinessScreen(self))
        self.main_box.add_widget(self.bscreen)

class BussinessManagerApp(App):
    def build(self):
        self.title = 'Manage Your Bussiness Records'
        return BussinessManager()

if __name__=="__main__":
    BussinessManagerApp().run()