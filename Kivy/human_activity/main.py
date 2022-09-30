
from socket import AI_PASSIVE
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label  
from kivy.uix.button import Button
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.core.window import Window 
from kivy.uix.modalview import ModalView

import numpy as np
from utils import DB, RSA
from matplotlib import pyplot as plt
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from activity_analyser import Senser, ActivityAnalyser

RSA.init    ()
Senser.init ()
_db         = DB("db.db")
analyser    = ActivityAnalyser()

Window.size = (370, 600) 

class Session:
    _user = None

    @classmethod
    def create(cls, user):
        cls._user = user
    
    @classmethod
    def get_user(cls):
        return cls._user
    
    @classmethod
    def clear(cls):
        cls._user = None

Builder.load_string("""
<LabelButton@Button+ButtonBehavior>:
    size_hint_y:1
    size_hint_x:None
    width:50  
    background_color:0,0,0,0
    color:(57/255.0,177/255.0,204/255.0,255/255.0)
    font_size:16
    bold:True
""")

Builder.load_string("""
<IconPress>:
    background_color: 0,0,0,0
    orientation     : 'vertical'
    padding         : 1   
    color           : (1, 1, 1, 1) 
    size_hint       : 1,1 
    on_state        : root.on_state_change(self.state)    
""")
class IconPress(BoxLayout, Button, ButtonBehavior):
    def __init__(self, **kwargs) -> None:
        super(IconPress, self).__init__()
        background_normal=''
        self.canvas.clear()
        self._image     = None
        self._args      = {'normal':(29/255.0,26/255.0,69/255.0,1), 'down':(0,.7,.7,1) }
        self._color     = Color()
        self._color.rgba= self._args['normal']
        self._rect      = RoundedRectangle(pos=self.pos, size=self.size, radius= [5])
        self.canvas.add(self._color)
        self.canvas.add(self._rect)
         
    def _set_background(self, color):
        if color:
            self._color.rgba = color

    def on_state_change(self, state):
        self.background_normal  = ""
        self._set_background(self._args.get(state))
   
    def _set_args(self, value):
        """ set initial args for Button as dict
            >>>@param:value -> python dict containing args for button
                                @required ('pos', 'size')
                                @optional ('normal', 'down', 'radius')
        """ 
        for key, val in value.items():
            self._args[key]   = val
        
        self._color.rgba= self._args.get("normal")
        self._rect.pos  = value['pos']
        self._rect.size = value['size'] 
        self._rect.radius=value.get("radius", [5])  

    args = property(lambda arg: None, _set_args)
    
    @property
    def icon_source(self):
        if self._image:
            return self._image.source

    @icon_source.setter
    def icon_source(self, value):
        if self._image is None:
            self.text               = ""
            self._image             = Image()
            self._image.size_hint_y = 1
            self._image.source      = value
            self.add_widget         (self._image)
        
        else:
            self._image.source = value

Builder.load_string(
"""
<CircularButton>:
    background_color: 0,0,0,0
    orientation     : 'vertical'
    padding         : 1   
    color           : (1, 1, 1, 1) 
    size_hint       :1,1 
    on_state        : root.on_state_change(self.state)
    
    Label:
        id:lbl
        size_hint_y:.01
""")
class CircularButton(BoxLayout, Button):
    def __init__(self, **kwargs) -> None:
        super(CircularButton, self).__init__()
        self.canvas.clear()
        self._image     = None
        self._args      = {'normal':(230/255, 184/255, 26/255,1), 'down':(0,.7,.7,1) }
        self._color     = Color()
        self._color.rgba= self._args['normal']
        self._rect      = RoundedRectangle(pos=self.pos, size=self.size, radius= [10])
        self.canvas.add(self._color)
        self.canvas.add(self._rect)
         
    def _set_background(self, color):
        if color:
            self._color.rgba = color

    def on_state_change(self, state):
        self._set_background(self._args.get(state))
   
    def _set_args(self, value):
        """ set initial args for Button as dict
            >>>@param:value -> python dict containing args for button
                                @required ('pos', 'size')
                                @optional ('normal', 'down', 'radius')
        """ 
        for key, val in value.items():
            self._args[key]   = val
        
        self._color.rgba= self._args.get("normal")
        self._rect.pos  = value['pos']
        self._rect.size = value['size'] 
        self._rect.radius=value.get("radius", [10])  

    args = property(lambda arg: None, _set_args)
    
    @property
    def icon_source(self):
        if self._image:
            return self._image.source

    @icon_source.setter
    def icon_source(self, value):
        """ set image source in case Circle Button is using icon"""
        if self._image is None:
            
            self._image             = Image()
            self._image.size_hint_y = 0.70
            self._image.source      = value
            self.ids.lbl.size_hint_y= 0.3
            self.ids.lbl.text       = self.text
            self.text               = ""
            self.add_widget         (self._image)
        
        else:
            self._image.source = value

Builder.load_string(
"""
<RowButton@BoxLayout+Button>:
    orientation:"horizontal"
    background_color: 0,0,0,0
    text_size:self.size
    bold: True
    font_size:14
    size_hint_y:None
    height:30
    color:(1,1,1,1)
    valign:'middle'
    halign:'center'
    canvas.before:
        Color:
            rgba: (0.92,0.96,0.97,.9) if self.state=='normal' else (0.2,.7,.7,1) 
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [0]
"""
)
class RowButton(BoxLayout, Button):
    def __init__(self, **kwargs) -> None:
        super(RowButton, self).__init__()

Factory.register("IconPress",       IconPress) 
Factory.register("CircularButton",  CircularButton)

Builder.load_string("""
<LoginPage>:
    size_hint:1,1
    orientation:'vertical'
    BoxLayout:
        size_hint:1,None
        height:34
        orientation:'horizontal'
        canvas.before:
            Color:
                rgba:(57/255.0,177/255.0,204/255.0,255/255.0)
            Rectangle:
                pos:self.pos
                size:self.size
        
        Label:
            text:'User Authentication'
            font_size:18
            bold:True
            text_size:self.size
            valign:'center'
            halign:'center'

    BoxLayout:
        id:working_area
        size_hint:1,1
        padding:2
        canvas.before:
            Color:
                rgba:(.9,.9,.9,1)
            Rectangle:
                pos:self.pos
                size:self.size
        BoxLayout:
            id:welcome_page
            size_hint:1,1
            orientation:'vertical'
            padding:15
            spacing:5
            BoxLayout:
                size_hint:1,0.2
                orientation:"vertical"
                # height:40
            
                Label:
                    id:login_heading
                    text:"Login Form"
                    font_size:30
                    bold:True
                    text_size:self.size
                    halign:'center'
                    valign:'top'
                    color:(0,0,0,1)
                Label:
                    id:lbl_msg
                    text:""
                    font_size:12
                    text_size:self.size
                    halign:'center'
                    valign:'center'
                    color:(1,0.23,0.2,1)
            BoxLayout:
                size_hint:1,0.55
                # height:0
                padding:0
                spacing:2
                orientation:"vertical"
                Label:
                    id:lbl_username
                    text:"Email:"
                    size_hint:1,1
                    font_size:17
                    text_size:self.size
                    halign:'left'
                    valign:'center'
                    color:(0,0,0,1)
                BoxLayout:
                    size_hint:1,None
                    height:33
                    padding:0
                    canvas.before:
                        Color:
                            rgba:(1,1,1,1)
                        RoundedRectangle:
                            pos:self.pos
                            size:self.size
                            radius:[4]
                    TextInput:
                        id  : username
                        text: ''
                        multiline:False
                        background_color: 0,0,0,0
                        foreground_color: 0,0,0,1
                        font_size:15

                Label:
                    id:lbl_password
                    text:"Password:"
                    size_hint:1,1
                    font_size:17
                    text_size:self.size
                    halign:'left'
                    valign:'center'
                    color:(0,0,0,1)
                BoxLayout:
                    size_hint:1,None
                    height:33
                    padding:0
                    canvas.before:
                        Color:
                            rgba:(1,1,1,1)
                        RoundedRectangle:
                            pos:self.pos
                            size:self.size
                            radius:[4]
                    TextInput:
                        id  : password
                        text: ''
                        multiline:False
                        password:True
                        background_color: 0,0,0,0
                        foreground_color: 0,0,0,1
                        font_size:15
                Label:
                    text:''
                    size_hint:1,None
                    height:40
                CircularButton:
                    id      :btn_login
                    args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                    text    :"Login"
                    bold    :True
                    font_size:15
                    size_hint_y:None
                    height:35
                    on_press:root.login(username.text, password.text)
                BoxLayout:
                    orientation:'horizontal'
                    size_hint:1,None
                    height:30
                    Label:
                        text:"Don't have an account?"
                        size_hint:1,1
                        color:(0,0,0,1)
                    LabelButton: 
                        id:btn_register
                        text:"Register"
                        on_press:root.call_signup();
                        
            BoxLayout:
                size_hint: 1,.30
""")
class LoginPage(BoxLayout):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent=_parent

    def login(self, username, password):
        users= _db.select(f"SELECT * FROM user", False)
        for u in users:
            if u['username'] == username and u['password']:
                Session.create(u)
                print(f"User [{username}] loged-in")
                self._parent.load_dashboard_page() 
                break

        if Session.get_user() is None:
            print(f"user[{username}] is not available")        
        
    def call_signup(self):
        self._parent.load_signup()     

Builder.load_string("""
<RegisterPage>:
    size_hint:1,1
    orientation:'vertical'
    BoxLayout:
        size_hint:1,None
        height:34
        orientation:'horizontal'
        canvas.before:
            Color:
                rgba:(57/255.0,177/255.0,204/255.0,255/255.0)
            Rectangle:
                pos:self.pos
                size:self.size
        
        Label:
            text:'Registeration'
            font_size:18
            bold:True
            text_size:self.size
            valign:'center'
            halign:'center'

    BoxLayout:
        id:working_area
        size_hint:1,1
        padding:2
        canvas.before:
            Color:
                rgba:(.9,.9,.9,1)
            Rectangle:
                pos:self.pos
                size:self.size
        BoxLayout:
            id:register_page
            size_hint:1,1
            orientation:'vertical'
            padding:15
            spacing:5
            BoxLayout:
                size_hint:1,0.08
                # height:40
            
                Label:
                    id:register_heading
                    text:"Signup Form"
                    font_size:25
                    bold:True
                    text_size:self.size
                    halign:'center'
                    valign:'top'
                    color:(0,0,0,1)
            BoxLayout:
                size_hint:1,0.87
                # height:0
                padding:0
                spacing:2
                orientation:"vertical"
                Label:
                    id:lbl_name
                    text:"Name:"
                    size_hint:1,1
                    font_size:17
                    text_size:self.size
                    halign:'left'
                    valign:'center'
                    color:(0,0,0,1)
                BoxLayout:
                    size_hint:1,None
                    height:33
                    padding:0
                    canvas.before:
                        Color:
                            rgba:(1,1,1,1)
                        RoundedRectangle:
                            pos:self.pos
                            size:self.size
                            radius:[4]
                    TextInput:
                        id:name
                        text:''
                        multiline:False
                        background_color: 0,0,0,0
                        foreground_color: 0,0,0,1
                        font_size:15
                Label:
                    id:lbl_age
                    text:"Age:"
                    size_hint:1,1
                    font_size:17
                    text_size:self.size
                    halign:'left'
                    valign:'center'
                    color:(0,0,0,1)
                BoxLayout:
                    size_hint:1,None
                    height:33
                    padding:0
                    canvas.before:
                        Color:
                            rgba:(1,1,1,1)
                        RoundedRectangle:
                            pos:self.pos
                            size:self.size
                            radius:[4]
                    TextInput:
                        id:age
                        text:''
                        multiline:False
                        background_color: 0,0,0,0
                        foreground_color: 0,0,0,1
                        font_size:15
                Label:
                    id:lbl_dob
                    text:"Birth Date"
                    size_hint:1,1
                    font_size:17
                    text_size:self.size
                    halign:'left'
                    valign:'center'
                    color:(0,0,0,1)
                BoxLayout:
                    size_hint:1,None
                    height:33
                    padding:0
                    canvas.before:
                        Color:
                            rgba:(1,1,1,1)
                        RoundedRectangle:
                            pos:self.pos
                            size:self.size
                            radius:[4]
                    TextInput:
                        id:dob
                        text:''
                        multiline:False
                        background_color: 0,0,0,0
                        foreground_color: 0,0,0,1
                        font_size:15
                Label:
                    id:lbl_height
                    text:"Height"
                    size_hint:1,1
                    font_size:17
                    text_size:self.size
                    halign:'left'
                    valign:'center'
                    color:(0,0,0,1)
                BoxLayout:
                    size_hint:1,None
                    height:33
                    padding:0
                    canvas.before:
                        Color:
                            rgba:(1,1,1,1)
                        RoundedRectangle:
                            pos:self.pos
                            size:self.size
                            radius:[4]
                    TextInput:
                        id:height
                        text:''
                        multiline:False
                        background_color: 0,0,0,0
                        foreground_color: 0,0,0,1
                        font_size:15
                Label:
                    id:lbl_jd
                    text:"Job Designation"
                    size_hint:1,1
                    font_size:17
                    text_size:self.size
                    halign:'left'
                    valign:'center'
                    color:(0,0,0,1)
                BoxLayout:
                    size_hint:1,None
                    height:33
                    padding:0
                    canvas.before:
                        Color:
                            rgba:(1,1,1,1)
                        RoundedRectangle:
                            pos:self.pos
                            size:self.size
                            radius:[4]
                    TextInput:
                        id:job
                        text:''
                        multiline:False
                        background_color: 0,0,0,0
                        foreground_color: 0,0,0,1
                        font_size:15
                Label:
                    id:lbl_username
                    text:"Username:"
                    size_hint:1,1
                    font_size:17
                    text_size:self.size
                    halign:'left'
                    valign:'center'
                    color:(0,0,0,1)
                BoxLayout:
                    size_hint:1,None
                    height:33
                    padding:0
                    canvas.before:
                        Color:
                            rgba:(1,1,1,1)
                        RoundedRectangle:
                            pos:self.pos
                            size:self.size
                            radius:[4]
                    TextInput:
                        id:username
                        text:''
                        multiline:False
                        background_color: 0,0,0,0
                        foreground_color: 0,0,0,1
                        font_size:15
                Label:
                    id:lbl_password
                    text:"Password:"
                    size_hint:1,1
                    font_size:17
                    text_size:self.size
                    halign:'left'
                    valign:'center'
                    color:(0,0,0,1)
                BoxLayout:
                    size_hint:1,None
                    height:33
                    padding:0
                    canvas.before:
                        Color:
                            rgba:(1,1,1,1)
                        RoundedRectangle:
                            pos:self.pos
                            size:self.size
                            radius:[4]
                    TextInput:
                        id:password
                        text:''
                        multiline:False
                        password:True
                        background_color: 0,0,0,0
                        foreground_color: 0,0,0,1
                        font_size:15
                Label:
                    text:''
                    size_hint:1,None
                    height:20
                CircularButton:
                    id      :btn_register
                    args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                    text    :"Register"
                    bold    :True
                    font_size:15
                    size_hint_y:None
                    height:35
                    on_press:root.register_user()
               
                   
                        
            BoxLayout:
                size_hint: 1,.05
""")
class RegisterPage(BoxLayout):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent=_parent

    def register_user(self):
        data = {key:self.ids[key].text for key in ("username", "password", "name" , 
                                                "age", "dob", "height", "job") }
        if _db.insert("user", data):
            print("user registered successfully")
            self.home()
        
        else:
            print("failed to register user - please try again")
    
    def home(self):
        self._parent.homepage()
  
Builder.load_string("""
<DashboardPage>:
    size_hint:1,1
    orientation:'vertical'
    BoxLayout:
        size_hint:1,None
        height:34
        orientation:'horizontal'
        canvas.before:
            Color:
                rgba:(57/255.0,177/255.0,204/255.0,255/255.0)
            Rectangle:
                pos:self.pos
                size:self.size

        IconPress:
            id      :btn_back
            args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[1]}
            icon_source:'arrow.png'
            size_hint_y:1
            size_hint_x:None
            width:30
            on_press:root.call_login_form()

        Label:
            text:'Welcome'
            font_size:18
            bold:True
            text_size:self.size
            valign:'center'
            halign:'center'
            
        IconPress:
            size_hint_x:None
            width:30

    BoxLayout:
        id:working_area
        size_hint:1,1
        padding:0
        canvas.before:
            Color:
                # rgba:(159/255.0,159/255.0,159/255.0,1)
                rgba:(.9,.9,.9,1)
            Rectangle:
                pos:self.pos
                size:self.size
        BoxLayout:
            id:welcome_page
            size_hint:1,1
            orientation:'vertical'
            padding:15
            spacing:10
            Label:
                id:lbl_msg
                text:''
                size_hint:1,None
                height:60
                color:(0,0,1,1)
            CircularButton:
                id      :btn_checkin
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0),'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Check In"
                bold    :True
                font_size:14
                size_hint_y:1
                on_press:root.checkin_analyser()
            
           
            CircularButton:
                id      :btn_checkout
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0),'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Check Out"
                bold    :True
                font_size:14
                size_hint_y:1
                on_press:root.checkout_analyser()
            CircularButton:
                id      :btn_pause
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0),'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Pause"
                bold    :True
                font_size:14
                size_hint_y:1
                on_press:root.call_pause_modal()
            
            CircularButton:
                id      :btn_motivational_task
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0),'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Motivational Task"
                bold    :True
                font_size:14
                size_hint_y:1
                on_press:root.call_motivational_task_modal()
            
            CircularButton:
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0),'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"View Graph"
                bold    :True
                font_size:14
                size_hint_y:1
                on_press:root.call_graph_modal()
            
            
""")  
class DashboardPage(BoxLayout):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent        = _parent

    @property
    def CHECHKED_IN(self):
        return getattr(self, "_checked_in", False)
    @CHECHKED_IN.setter
    def CHECHKED_IN(self, value):
        setattr(self, "_checked_in", value)

    @property
    def PAUSE(self):
        return getattr(self, "_pause", False)
    @PAUSE.setter
    def PAUSE(self, value):
        setattr(self, "_pause", value)

    def read_motivation_task(self, key):
        try:
            userid  = Session.get_user()['id'] 
            tasks   = _db.select(f"SELECT * FROM motivation WHERE userid='{userid}'", True)
            return tasks[key.lower()]
        
        except Exception as e:
            print(e)

    def set_message(self, message):
        self.ids.lbl_msg.text = message
    
    def analyse(self, dt):
        def _analyse(result, dt):
            if result is not None:
                if not self.PAUSE:
                    task = self.read_motivation_task(result)
                    if task is not None:
                        self.set_message(task)
                    else:
                        self.set_message("You are "+result)
                else:
                    self.set_message("notification paused")
            else:
                self.set_message("analyses failed - will try again")
        
        self.set_message("analysing ...")
        analyser.analyse( Senser.data_sequence(90), _analyse )
    
    def checkin_analyser(self):
        if not self.CHECHKED_IN:
            Clock.schedule_interval(self.analyse, 5)
            self.CHECHKED_IN = True
            self.set_message("Analyser Checked-in")
        
    def checkout_analyser(self):
        if self.CHECHKED_IN:
            Clock.unschedule(self.analyse)
            self.CHECHKED_IN = False
            self.set_message("Analyser Checked-out")

    def call_login_form(self):
        Session.clear()
        self._parent.homepage()

    def call_motivational_task_modal(self):
        popup=MotivationalTaskModal(self)
        popup.load_modal()

    def call_graph_modal(self):
        Graph().open()

    def call_pause_modal(self):
        self.PAUSE = not self.PAUSE

Builder.load_string("""
<MotivationalTaskModal>:
    size_hint:1,1
    size_hint: 0.8, 0.6
    auto_dismiss:False
    id:popup_modal
    orientation: "vertical"
    padding:2
    canvas.before:
        Color: 
            rgba:(.9,.9,.9,.9)
        Rectangle: 
            pos:self.pos
            size:self.size
    BoxLayout:
        id:working_section
        orientation: "vertical"
        size_hint_x:1
        size_hint_y:1
        padding:3
        spacing:5
        canvas.before:
            Color: 
                rgba:(0.9,0.9,0.9,1)
            Rectangle: 
                pos:self.pos
                size:self.size
        
        BoxLayout:
            size_hint:1,None
            height:34
            orientation:'horizontal'
            canvas.before:
                Color:
                    rgba:(57/255.0,177/255.0,204/255.0,255/255.0)
                Rectangle:
                    pos:self.pos
                    size:self.size
            Label:
                text:'Add Task'
                font_size:18
                bold:True
                text_size:self.size
                valign:'center'
                halign:'center'

        Label:
            id:task_msg
            text:""
            text_size:self.size
            halign:"center"
            valign:"center"
            font_size:15
            color:(0,0,1,1)
            size_hint:1,None
            height:40
        BoxLayout:
            orientation:"vertical"
            size_hint:1,1
            Label:
                id:lbl_sitting
                text:"Task For Sitting:"
                size_hint:1,1
                font_size:17
                text_size:self.size
                halign:'left'
                valign:'center'
                color:(0,0,0,1)
            BoxLayout:
                size_hint:1,None
                height:33
                padding:0
                canvas.before:
                    Color:
                        rgba:(1,1,1,1)
                    RoundedRectangle:
                        pos:self.pos
                        size:self.size
                        radius:[4]
                TextInput:
                    id:sitting
                    text:''
                    multiline:False
                    background_color: 0,0,0,0
                    foreground_color: 0,0,0,1
                    font_size:15
            Label:
                id:lbl_walking
                text:"Task For Walking:"
                size_hint:1,1
                font_size:17
                text_size:self.size
                halign:'left'
                valign:'center'
                color:(0,0,0,1)
            BoxLayout:
                size_hint:1,None
                height:33
                padding:0
                canvas.before:
                    Color:
                        rgba:(1,1,1,1)
                    RoundedRectangle:
                        pos:self.pos
                        size:self.size
                        radius:[4]
                TextInput:
                    id:walking
                    text:''
                    multiline:False
                    background_color: 0,0,0,0
                    foreground_color: 0,0,0,1
                    font_size:15
            Label:
                id:lbl_jogging
                text:"Task For Jogging:"
                size_hint:1,1
                font_size:17
                text_size:self.size
                halign:'left'
                valign:'center'
                color:(0,0,0,1)
            BoxLayout:
                size_hint:1,None
                height:33
                padding:0
                canvas.before:
                    Color:
                        rgba:(1,1,1,1)
                    RoundedRectangle:
                        pos:self.pos
                        size:self.size
                        radius:[4]
                TextInput:
                    id:jogging
                    text:''
                    multiline:False
                    background_color: 0,0,0,0
                    foreground_color: 0,0,0,1
                    font_size:15

        BoxLayout:
            orientation:"horizontal"
            size_hint:1,None
            height:40
            spacing:2
            padding:2
            CircularButton:
                id      :btn_save
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Save"
                bold    :True
                font_size:15
                size_hint_y:None
                height:35
                on_release:root.save_tasks(self.text, sitting.text, walking.text, jogging.text)
            CircularButton:
                id      :btn_close
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Close"
                bold    :True
                font_size:15
                color:(1,0,0,1)
                size_hint_y:None
                height:35
                on_press:root.close_modal()
                
""")
class MotivationalTaskModal(ModalView):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent=_parent

    def read_motivation_tasks(self):
        try:
            userid  = Session.get_user()['id'] 
            tasks   = _db.select(f"SELECT * FROM motivation WHERE userid='{userid}'", True)
            return tasks
        
        except Exception as e:
            print(e)

    def load_modal(self):
        tasks = self.read_motivation_tasks()
        if tasks is not None:
            for key in ("sitting", "walking", "jogging"):
                self.ids[key].text = tasks[key]
            self.ids.btn_save.text = "Update"
        
        self.open()

    def set_message(self, message):
        self.ids.task_msg.text = message

    def save_tasks(self, source, sitting, walking, jogging):
        userid = Session.get_user()["id"]
        if source == "Save":
            data = {"userid":userid, "sitting":sitting, "walking":walking, "jogging":jogging}
            if _db.insert("motivation", data):
                self.set_message("tasks saved successfuly")
                self.ids.btn_save.text = "Update"
            else:
                self.set_message("failed to save tasks - try again")
        
        else:
            data = {"sitting":sitting, "walking":walking, "jogging":jogging}
            if _db.update("motivation", data, f"userid='{userid}'"):
                self.set_message("tasks updated successfuly")
                self.ids.btn_save.text = "Update"
            else:
                self.set_message("failed to update tasks - try again")

    def close_modal(self):
        self.dismiss()
        self.ids.btn_save.text = "Save"
        self.set_message("")

Builder.load_string("""
<PauseModal>:
    size_hint:1,1
    size_hint: 0.5, 0.4
    auto_dismiss:False
    id:popup_modal
    orientation: "vertical"
    padding:2
    canvas.before:
        Color: 
            rgba:(.9,.9,.9,.9)
        Rectangle: 
            pos:self.pos
            size:self.size
    BoxLayout:
        id:working_section
        orientation: "vertical"
        size_hint_x:1
        size_hint_y:1
        padding:1
        spacing:5
        canvas.before:
            Color: 
                rgba:(1,1,1,1)
            Rectangle: 
                pos:self.pos
                size:self.size
        
        BoxLayout:
            size_hint:1,None
            height:34
            orientation:'horizontal'
            canvas.before:
                Color:
                    rgba:(57/255.0,177/255.0,204/255.0,255/255.0)
                Rectangle:
                    pos:self.pos
                    size:self.size
            Label:
                text:'Pause'
                font_size:18
                bold:True
                text_size:self.size
                valign:'center'
                halign:'center'

        Label:
            id:task_msg
            text:""
            text_size:self.size
            halign:"center"
            valign:"center"
            font_size:15
            color:(0,0,1,1)
            size_hint:1,None
            height:40
        BoxLayout:
            orientation : "vertical"

            BoxLayout:
                CheckBox:
                    id          : 2
                    size_hint_x : 0.2
                    group       : "pause"
                
                
                Label:
                    id  : lbl_pause_2
                    size_hint_x : 0.8
                    text: "Pause For 2"
                    color:0,0,1,1
            BoxLayout:
                CheckBox:
                    id      : 3
                    size_hint_x : 0.2
                    group   : "pause"
                  
                
                Label:
                    id  : lbl_pause_3
                    size_hint_x : 0.8
                    text: "Pause For 3"
                    color:0,0,1,1
            BoxLayout:
                CheckBox:
                    id      : 5
                    size_hint_x : 0.2
                    group   : "pause"
                  
                
                Label:
                    id  : lbl_pause_5
                    size_hint_x : 0.8
                    text: "Pause For 5"
                    color:0,0,1,1
        BoxLayout:
            orientation:"horizontal"
            size_hint:1,None
            height:40
            spacing:2
            padding:2
            CircularButton:
                id      :btn_save
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Save"
                bold    :True
                font_size:15
                size_hint_y:None
                height:35
            CircularButton:
                id      :btn_close
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Close"
                bold    :True
                font_size:15
                color:(1,0,0,1)
                size_hint_y:None
                height:35
                on_press:root.close_modal()
                
""")
class PauseModal(ModalView):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent=_parent
        self._ignore        = False

    def on_option(self, value, task):
        if self._ignore:
            self._ignore = False
            return

        if value:
            keys        = ["2", "3", "4"]
            t           = task.split("_")[1]
            keys.remove (t)
            data        = {t:self.ids[task].text}
            for key in keys:
                data[key] = "" 
    
    def close_modal(self):
        self.dismiss()

Builder.load_string("""
<Graph>:
    size_hint:1,1
    size_hint: 0.8, 0.6
    auto_dismiss:False
    orientation: "vertical"
    padding:2
    canvas.before:
        Color: 
            rgba:(.9,.9,.9,.9)
        Rectangle: 
            pos:self.pos
            size:self.size
    BoxLayout:
        id:working_section
        orientation: "vertical"
        size_hint_x:1
        size_hint_y:1
        padding:3
        spacing:5
        canvas.before:
            Color: 
                rgba:(0.9,0.9,0.9,1)
            Rectangle: 
                pos:self.pos
                size:self.size
        BoxLayout:
            size_hint_y : 0.2
            padding     : 5
            spacing     : 5
            CircularButton:
                id      : daily
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Daily"
                bold    :True
                font_size:15
                color:(1,0,0,1)
                size_hint_y:None
                height:35
                on_press:root.display_graph()
            CircularButton:
                id      :weekly
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Weekly"
                bold    :True
                font_size:15
                color:(1,0,0,1)
                size_hint_y:None
                height:35
                on_press:root.display_graph()
            CircularButton:
                id      :monthly
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Monthly"
                bold    :True
                font_size:15
                color:(1,0,0,1)
                size_hint_y:None
                height:35
                on_press:root.display_graph()
        BoxLayout:
            id          : graph
            size_hint_y : 0.6
            padding     : 5
            spacing     : 5
            canvas.before:
                Color:
                    rgba:(.9,.9,.9,.9)
                Rectangle:
                    pos:self.pos
                    size:self.size

        BoxLayout:
            size_hint_y:0.2
            padding:2
            CircularButton:
                id      :btn_close
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Close"
                bold    :True
                font_size:15
                color:(1,0,0,1)
                size_hint_y:None
                height:35
                on_press:root.close_modal()
                
""")
class Graph(ModalView):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def display_graph(self):
        values      =  np.random.uniform(low=-25.0, high=90.0, size=(10,))
        plt.clf     ()
        plt.plot    (values)
        plt.xlabel  ('X')
        plt.ylabel  ('Y')
        plt.grid    (True, color='lightgray')
        self.ids.graph.clear_widgets()
        self.ids.graph.add_widget(FigureCanvasKivyAgg(plt.gcf()))
    
    def close_modal(self):
        self.dismiss()



Builder.load_string("""
<Main>:
    size_hint:1,1
    padding:0
    spacing:0
    orientation:"vertical"
    canvas.before:
        Color:
            rgba:(1,1,1,1)
        Rectangle:
            pos:self.pos
            size:self.size
   
        
    BoxLayout:
        id:dynamic_box
        size_hint:1,1
        padding:0   
        orientation:'vertical'    
""")
class Main(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.dynamic_area=self.ids.dynamic_box
        self.homepage()

    def homepage(self):
        self.admin_register=True

        self.login_form         = LoginPage(self)
        self.register_page      = RegisterPage(self)

        self.dynamic_area.clear_widgets()
        if self.admin_register==True:
            self.dynamic_area.add_widget(self.login_form)
        else:
            self.dynamic_area.add_widget(self.register_page)

    def load_signup(self):
        self.dynamic_area.clear_widgets()
        self.dynamic_area.add_widget(self.register_page)

    def load_dashboard_page(self):
        self.dashboard_page=DashboardPage(self)
        self.dynamic_area.clear_widgets()
        self.dynamic_area.add_widget(self.dashboard_page)

class MainApp(App):
    def build(self):
        return Main()

if __name__=="__main__":
    pa=MainApp()
    pa.run()

