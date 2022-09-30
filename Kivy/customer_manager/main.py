from functools import partial
import sqlite3
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label  
from kivy.uix.button import Button
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.factory import Factory
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.core.window import Window 
from kivy.uix.modalview import ModalView
# from numpy import record

Window.size = (370, 600) 
# helping widgets
Builder.load_string(
"""
<LabelButton@Button+ButtonBehavior>:
    size_hint_y:1
    size_hint_x:None
    width:50  
    background_color:0,0,0,0
    color:(57/255.0,177/255.0,204/255.0,255/255.0)
    font_size:16
    bold:True
""")



#custome defined 
Builder.load_string(
"""
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

# rounded button
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

# row for data table
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

# modal view popup
Builder.load_string("""
<PopupModal>:
    size_hint:1,1
    size_hint: 0.8, 0.6
    auto_dismiss:True
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
        Label:
            id:pop_msg
            text:"Record is selected"
            text_size:self.size
            halign:"center"
            valign:"center"
            font_size:15
            color:(0,0,1,1)
            size_hint:1,None
            height:40
        BoxLayout:
            orientation:"horizontal"
            size_hint:1,None
            height:40
            spacing:2
            padding:2
            CircularButton:
                id      :btn_delete
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Delete"
                bold    :True
                font_size:15
                color:(1,0,0,1)
                size_hint_y:None
                height:35
                on_press:root.remove_record()
            CircularButton:
                id      :btn_edit
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Edit"
                bold    :True
                font_size:15
                size_hint_y:None
                height:35
                on_press:update_section.opacity=1
        BoxLayout:
            orientation:"vertical"
            id:update_section
            size_hint:1,0.7
            spacing:6
            opacity:0
           
                
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
                    id:up_name
                    text:''
                    multiline:False
                    background_color: 0,0,0,0
                    foreground_color: 0,0,0,1
                    font_size:15
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
                    id:up_phone
                    text:''
                    multiline:False
                    background_color: 0,0,0,0
                    foreground_color: 0,0,0,1
                    font_size:15
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
                    id:up_location
                    text:''
                    multiline:False
                    background_color: 0,0,0,0
                    foreground_color: 0,0,0,1
                    font_size:15
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
                    id:up_date
                    text:''
                    multiline:False
                    background_color: 0,0,0,0
                    foreground_color: 0,0,0,1
                    font_size:15
            CircularButton:
                id      :btn_update
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Update"
                bold    :True
                font_size:15
                size_hint_y:None
                height:35
                on_press:root.update_record()
            BoxLayout:
                size_hint:1,0.071
                
""")

# welcome page
Builder.load_string("""
<Login_page>:
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
            text:'Customer Management'
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
                    text:"Login"
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
                        id:txt_email
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
                        id:txt_password
                        text:''
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
                    on_press:root.call_dashboard_page()
                BoxLayout:
                    orientation:'horizontal'
                    size_hint:1,None
                    height:30
                    # Label:
                    #     text:"Don't have an admin account?"
                    #     size_hint:1,1
                    #     color:(0,0,0,1)
                    # LabelButton: 
                    #     id:btn_register
                    #     text:"Register"
                    #     on_press:root.signup();
                        
            BoxLayout:
                size_hint: 1,.30
""")

# register page
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
            text:'Customer Management'
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
                size_hint:1,0.1
                # height:40
            
                Label:
                    id:register_heading
                    text:"Registeration"
                    font_size:25
                    bold:True
                    text_size:self.size
                    halign:'center'
                    valign:'top'
                    color:(0,0,0,1)
            BoxLayout:
                size_hint:1,0.70
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
                        id:txt_name
                        text:''
                        multiline:False
                        background_color: 0,0,0,0
                        foreground_color: 0,0,0,1
                        font_size:15
                Label:
                    id:lbl_phone
                    text:"Phone:"
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
                        id:txt_phone
                        text:''
                        multiline:False
                        background_color: 0,0,0,0
                        foreground_color: 0,0,0,1
                        font_size:15
                Label:
                    id:lbl_email
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
                        id:txt_email
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
                        id:txt_password
                        text:''
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
                    id      :btn_register
                    args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                    text    :"Register"
                    bold    :True
                    font_size:15
                    size_hint_y:None
                    height:35
                    on_press:root.register_user()
               
                   
                        
            BoxLayout:
                size_hint: 1,.20
""")
# dashboardpage
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
            text:'Customer Management'
            font_size:18
            bold:True
            text_size:self.size
            valign:'center'
            halign:'center'
            
        # IconPress:
        #     size_hint_x:None
        #     width:30

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
            padding:1
            spacing:10
            BoxLayout:
                orientation:"horizontal"
                size_hint:1,None
                height:40
                Label:
                    text:"Name"
                    font_size:12
                    color:(0,0,0,1)
                    text_size:self.size
                    halign:'center'
                    valign:'bottom'
                    bold:True
                Label:
                    text:"Phone"
                    font_size:12
                    color:(0,0,0,1)
                    text_size:self.size
                    halign:'center'
                    valign:'bottom'
                    bold:True
                Label:
                    text:"Location"
                    font_size:12
                    color:(0,0,0,1)
                    text_size:self.size
                    halign:'center'
                    valign:'bottom'
                    bold:True
                Label:
                    text:"Date"
                    font_size:12
                    color:(0,0,0,1)
                    text_size:self.size
                    halign:'center'
                    valign:'bottom'
                    bold:True
            BoxLayout:
                size_hint:1,1
                orientation:'vertical'
                spacing:4
                canvas.before:
                    Color:
                        rgba:(1,1,1,1)
                    Rectangle:
                        pos:self.pos
                        size:self.size
                
                ScrollView:
                    do_scroll_x: False
                    do_scroll_y: True
                    size:self.size
                    bar_width:10
                    bar_color: 0, 0, 0, .21   # red
                    effect_cls: "ScrollEffect"
                    scroll_type: ['bars', 'content']
                    GridLayout:
                        id:row_widget_box
                        height:self.minimum_height
                        cols:1
                        size_hint_y: None
                        orientation: 'tb-lr'#'vertical'
                        spacing:1
                        padding:1
                        # RowButton:
                        # RowButton:

            BoxLayout:
                size_hint:1,.30  
                padding:15
                CircularButton:
                    id      :btn_add_customer
                    args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0),'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                    text    :"Add Customer"
                    bold    :True
                    font_size:14
                    size_hint_y:None
                    height:35
                    on_press:root.call_add_customer_page()
                
            
""")
# main page
Builder.load_string("""
<Add_customer_page>:
    size_hint:1,1
    orientation:'vertical'
    canvas.before:
        Color:
            rgba:(.9,.9,.9,1)
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
        IconPress:
            id      :btn_back
            args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[1]}
            icon_source:'arrow.png'
            size_hint_y:1
            size_hint_x:None
            width:30
            on_press:root.call_dashboard_page()
        Label:
            text:'Customer Management'
            font_size:18
            bold:True
            text_size:self.size
            valign:'center'
            halign:'center'
    BoxLayout:
        id:register_page
        size_hint:1,1
        orientation:'vertical'
        padding:15
        spacing:5
        canvas.before:
            Color:
                rgba:(.9,.9,.9,1)
            Rectangle:
                pos:self.size
                size:self.size
        BoxLayout:
            size_hint:1,0.1
            # height:40
        
            Label:
                id:form_heading
                text:"Add Customer"
                font_size:25
                bold:True
                text_size:self.size
                halign:'center'
                valign:'top'
                color:(0,0,0,1)
        BoxLayout:
            size_hint:1,1
            # height:0
            padding:0
            spacing:2
            orientation:"vertical"
            Label:
                id:form_mesg
                text:""
                font_size:15
                text_size:self.size
                halign:'center'
                valign:'top'
                color:(0.2,0.2,1,1)
            Label:
                id:lbl_name
                text:"Customer Name:"
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
                    id:cust_name
                    text:''
                    multiline:False
                    background_color: 0,0,0,0
                    foreground_color: 0,0,0,1
                    font_size:15
            Label:
                id:lbl_telephone
                text:"Telephone:"
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
                    id:cust_phone
                    text:''
                    multiline:False
                    background_color: 0,0,0,0
                    foreground_color: 0,0,0,1
                    font_size:15
            Label:
                id:lbl_location
                text:"Delivery Location:"
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
                    id:cust_location
                    text:''
                    multiline:False
                    background_color: 0,0,0,0
                    foreground_color: 0,0,0,1
                    font_size:15
            
            
            Label:
                id:lbl_date
                text:"Insertion Date:"
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
                    id:cust_date
                    text:''
                    hint_text:'dd/mm/yyyy'
                    multiline:False
                    background_color: 0,0,0,0
                    foreground_color: 0,0,0,1
                    font_size:15
            Label:
                text:''
                size_hint:1,None
                height:40
            CircularButton:
                id      :btn_Add
                args    :{'normal':(57/255.0,177/255.0,204/255.0,255/255.0), 'down':(.12,.32,.54,1), 'size':self.size, 'pos':self.pos, 'radius':[7]}
                text    :"Save Record"
                bold    :True
                font_size:15
                size_hint_y:None
                height:35
                on_press:root.register_admin()   
                                        
        BoxLayout:
            size_hint: 1,.2
        
""")

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
        conn=sqlite3.connect('cm_db.db')
        c=conn.cursor()
        conn.close()
        self.homepage()
        

    def homepage(self):
        self.admin_register=False
        conn=sqlite3.connect('cm_db.db')
        c=conn.cursor()
        c.execute("SELECT * FROM Registeration")
        admin=c.fetchall()
        if admin:
            if len(admin)>0:
                self.admin_register=True
        conn.commit()
        conn.close()

        self.login_form         = Login_page(self)
        self.register_page      = RegisterPage(self)

        self.dynamic_area.clear_widgets()
        if self.admin_register==True:
            self.dynamic_area.add_widget(self.login_form)
        else:
            self.dynamic_area.add_widget(self.register_page)

    def load_dashboard_page(self):
        self.dashboard_page=DashboardPage(self)
        self.dynamic_area.clear_widgets()
        self.dynamic_area.add_widget(self.dashboard_page)

    def load_new_customer_page(self):
        self.new_customer_page=Add_customer_page(self)
        self.dynamic_area.remove_widget(self.dashboard_page)
        self.dynamic_area.add_widget(self.new_customer_page)

class Login_page(BoxLayout):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent=_parent

    def call_dashboard_page(self):
        admin_auth=False
        conn=sqlite3.connect('cm_db.db')
        c=conn.cursor()
        c.execute("SELECT * FROM Registeration")
        admins=c.fetchall()
        if admins:
            for ad in admins:
                if ad[2]==self.ids.txt_email.text:
                    if ad[3]==self.ids.txt_password.text:
                        admin_auth=True
                    else:
                        self.ids.lbl_msg.text="**Password Not Matched**"
                else:
                    self.ids.lbl_msg.text="**Email Not Matched**"
                        
        conn.commit()
        conn.close()
        if admin_auth==True:
            self._parent.load_dashboard_page()
        else:
            print("Admin authentication error")

        self.ids.txt_email.text=''
        self.ids.txt_password.text=''

class RegisterPage(BoxLayout):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent=_parent

    def register_user(self):
        conn=sqlite3.connect('cm_db.db')
        c=conn.cursor()
        c.execute(" INSERT INTO Registeration VALUES (:name,:phone,:email,:password)",{
            'name':self.ids.txt_name.text ,
            'phone':self.ids.txt_phone.text ,
            'email':self.ids.txt_email.text ,
            'password':self.ids.txt_password.text ,
        })
        conn.commit()
        conn.close()
        self.ids.txt_name.text=''
        self.ids.txt_phone.text=''
        self.ids.txt_email.text=''
        self.ids.txt_password.text=''
        self._parent.homepage()
class DashboardPage(BoxLayout):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent=_parent
        self.show_records()

    def reload_box(self):
         table_box=self.ids.row_widget_box
         table_box.clear_widgets()
         self.show_records()
         

    def show_records(self):
        table_box=self.ids.row_widget_box
        conn=sqlite3.connect('cm_db.db')
        c=conn.cursor()
        c.execute("SELECT * FROM Customer")
        customers=c.fetchall()
        for cust in customers:
            row=RowButton()
            id=cust[0]
            name=Label(text=cust[1], color=(0,0,0,1),font_size=12) # ,,id='myname'
            phone=Label(text=cust[2],color=(0,0,0,1),font_size=12)
            location=Label(text=cust[3],color=(0,0,0,1),font_size=12)
            date=Label(text=cust[4],color=(0,0,0,1),font_size=12)
            row.add_widget(name)
            row.add_widget(phone)
            row.add_widget(location)
            row.add_widget(date)
            row.bind(on_press=partial(self.call_popup,  id))
            table_box.add_widget(row)
        conn.commit()
        conn.close()

    def call_login_form(self):
        self._parent.homepage()

    def call_add_customer_page(self):
        self._parent.load_new_customer_page()

    def call_popup(self, rowid, source):
        popup=PopupModal(self,rowid)
        popup.open()
        
        

# for delete or edit confirmation
class PopupModal(ModalView):
    def __init__(self,_parent,rowid,**kwargs):
        super().__init__(**kwargs)
        self._parent=_parent
        self.rowid=rowid
        self.selected_record()

    def selected_record(self):
        conn=sqlite3.connect('cm_db.db')
        c=conn.cursor()
        c.execute(f'SELECT * FROM Customer WHERE id = {self.rowid};')
        record=c.fetchall()
        for rec in record:
            self.ids.up_name.text=rec[1]
            self.ids.up_phone.text=rec[2]
            self.ids.up_location.text=rec[3]
            self.ids.up_date.text=rec[4]

        conn.commit()
        conn.close()
        self.dismiss()

    def update_record(self):
        conn=sqlite3.connect('cm_db.db')
        c=conn.cursor()
        c.execute(f"UPDATE Customer SET name = ('{self.ids.up_name.text}'),phone=('{self.ids.up_phone.text}'),location=('{self.ids.up_location.text}'),date=('{self.ids.up_date.text}') WHERE id = {self.rowid}")
        
        conn.commit()
        conn.close()
        self._parent.reload_box()
        self.dismiss()

    def remove_record(self):
        conn=sqlite3.connect('cm_db.db')
        c=conn.cursor()
        c.execute(f'DELETE FROM Customer WHERE id = {self.rowid};')
        # record=c.fetchall()
        conn.commit()
        conn.close()
        self._parent.reload_box()
        self.dismiss()
    
class Add_customer_page(BoxLayout):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent=_parent

    def register_admin(self):
        conn=sqlite3.connect('cm_db.db')
        c=conn.cursor()
        c.execute(f"""  INSERT INTO Customer(name, phone, location, date) 
                        VALUES ('{self.ids.cust_name.text}',
                            '{self.ids.cust_phone.text}',
                            '{self.ids.cust_location.text}',
                            '{self.ids.cust_date.text}')""")
            
            
        conn.commit()
        conn.close()
        self.ids.form_mesg.text="Record saved"
        self.ids.cust_name.text=''
        self.ids.cust_phone.text=''
        self.ids.cust_location.text=''
        self.ids.cust_date.text=''

    

    def call_dashboard_page(self):
        self._parent.load_dashboard_page()
        # self._parent.homepage()

# build & run application
class MainApp(App):
    def build(self):
        return Main()

if __name__=="__main__":
    pa=MainApp()
    pa.run()


Factory.register("IconPress", IconPress) 
Factory.register("CircularButton", CircularButton)
