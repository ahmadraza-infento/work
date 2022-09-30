
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from movement_detector import MovementDetector
from encrypted_db import EncryptedDB

enc_db          = EncryptedDB("mov_db.db", b"UINBY5F956L6sb0rU3hSJUHEuo_gKmrCGsV_m-ErHKM=")
mov_detector    = MovementDetector()
Window.size     = (350, 600)


kv = '''
ScreenManager:
    Login:
    Main:
    GraphForm:
    Setting:
    Information:
              

# ------------------------------- login page--------------------------------
<Login>:
    name:'login'
    
    BoxLayout:
        orientation:'vertical'
        size_hint_x:1
        size_hint_y:1
        MDToolbar:
            title: "English"
        BoxLayout:
            orientation:'vertical'
            size_hint_x:1
            size_hint_y:0.6
            padding:5
            spacing:10
            MDLabel:
                text:'Login Form'
                font_style: 'H6'
                halign: 'center'
                size_hint: (1,0.26)
                # pos_hint : {'center_y':0.085}
            MDLabel:
                id : statusbar
                text:''
                halign: 'center'
                size_hint:1,0.2
                font_size:15

            MDTextField:
                id:username
                size_hint: (1,0.22)
                hint_text : 'Username'
                helper_text: 'Required'
                helper_text_mode: 'on_error'
                icon_right: 'account'
                icon_right_color: app.theme_cls.primary_color
                required : True
            MDTextField:
                id:password
                # pos_hint: {'center_x':0.5,'center_y':0.6}
                size_hint: (1,0.22)
                hint_text : 'Password'
                helper_text: 'Required'
                password:True
                helper_text_mode: 'on_error'
                icon_right: 'eye'
                icon_right_color: app.theme_cls.primary_color
                required : True
            MDRoundFlatButton:
                text:'Login'
                font_size:18
                size_hint_x:1
                size_hint_y:0.15
                forground_color:(.8,0,0,.8)
                on_release: root.login(username.text, password.text)
            MDRoundFlatButton:
                text:'Create Account'
                font_size:18
                size_hint_x:1
                size_hint_y:0.15
                forground_color:(.8,0,0,.8)
        Widget:
            size_hint_y:0.2

            

# ------------------------------- main page -----------------------
<Main>:
    name:'main'
    BoxLayout:
        orientation:'vertical'
        size_hint_x:1
        size_hint_y:1
        spacing:2
        BoxLayout:
            orientation:'vertical'
            size_hint:(1, 0.2)
            canvas.before:
                Color:
                    rgba:(0.2,0.2,0.4,1)
                Rectangle:
                    pos:self.pos
                    size:self.size
            MDLabel:
                id:lbl_status
                text:""
                halign:'center'
                font_size:14
                color:1,1,1,1
                size_hint_y:0.4
            BoxLayout:
                orientation:'horizontal'
                size_hint: (1, 0.2)
                spacing:3
                padding:2
               
            BoxLayout:
                orientation:'horizontal'
                size_hint: (1, 0.4)
                spacing:1
                padding:1
                MDFillRoundFlatIconButton:
                    text: "Check-In"
                    icon: "location-enter"
                    size_hint: (0.25, 1)
                    on_release:root.checkin_detector()
                MDFillRoundFlatIconButton:
                    text: "Check-Out"
                    icon: "location-exit"
                    size_hint: (0.25, 1)
                    on_release:root.checkout_detector()
                MDFillRoundFlatIconButton:
                    text: "Notification"
                    icon: "alarm"
                    size_hint: (0.25, 1) 
        BoxLayout:
            orientation:'vertical'
            size_hint: (1, 0.5)
            canvas.before:
                Color:
                    rgba:(1,1,1,1)
                Rectangle:
                    pos:self.pos
                    size:self.size
            MDLabel:
                text:"Motivational Task"
                halign:'center'
                font_style: 'H6'
                color:0,0,0,1
                size_hint_y:0.2
            MDBoxLayout:
                id:contents
                size_hint: (1, 0.80)
                orientation : "vertical"
                padding:5
                MDBoxLayout:
                    orientation:'vertical'
                    size_hint: (1, 1)
                    spacing:2
                    BoxLayout:
                        MDCheckbox:
                            id          : sitting
                            size_hint_x : 0.2
                            group       : "task"
                            active: True
                        Label:
                            id  : lbl_task_sitting
                            size_hint_x : 0.8
                            text: "Task For Sitting"
                            color:0,0,1,1
                    BoxLayout:
                        MDCheckbox:
                            id      : walking
                            size_hint_x : 0.2
                            group   : "task"
                            
                        Label:
                            id  : lbl_task_walking
                            size_hint_x : 0.8
                            text: "Task For Walking"
                            color:0,0,1,1
                    BoxLayout:
                        MDCheckbox:
                            id      : running
                            size_hint_x : 0.2
                            group   : "task"
                        
                        Label:
                            id  : lbl_task_running
                            size_hint_x : 0.8
                            text: "Task For Running"
                            color:0,0,1,1
        BoxLayout:
            orientation:'vertical'
            size_hint: (1, 0.1)
            padding:2
            spacing:5
            canvas.before:
                Color:
                    rgba:(0.7,.7,.7,1)
                Rectangle:
                    pos:self.pos
                    size:self.size
            MDLabel:
                text:"Accelerometer / Input data"
                halign:'center'
                font_style: 'H6'
                color:0,0,0,1
                size_hint_y:0.7
            MDLabel:
                id:lbl_input
                text:""
                halign:'center'
                font_size:15
                color:0,0,0,1
        Widget:
            size_hint:(1, 0.1)    
        BoxLayout:
            orientation:'horizontal'
            size_hint:(1, 0.1)
            spacing:5
            padding:3
            canvas.before:
                Color:
                    rgba:(1,1,1,1)
                Rectangle:
                    pos:self.pos
                    size:self.size
            
            MDRoundFlatButton:
                text:'Back'
                font_size:12
                size_hint_x:0.24
                size_hint_y:1
                forground_color:(.8,0,0,.8)
                on_release:root.manager.current='login'
            MDRoundFlatButton:
                text:'Setting'
                font_size:12
                size_hint_x:0.24
                size_hint_y:1
                forground_color:(.8,0,0,.8)
                on_release:root.load_setting()
            MDRoundFlatButton:
                text:'Information'
                font_size:12
                size_hint_x:0.24
                size_hint_y:1
                forground_color:(.8,0,0,.8)
                on_release:root.manager.current='information'
            MDRoundFlatButton:
                text:'Graph'
                font_size:12
                size_hint_x:0.24
                size_hint_y:1
                forground_color:(.8,0,0,.8)
                on_release:root.manager.current='graphForm'
        
# ------------------------------- graphic page -----------------------
<GraphForm>:
    name:'graphForm'
    MDBoxLayout:
        orientation:'vertical'
        size_hint_x:1
        size_hint_y:1
        padding:0
        spacing:2
        MDBoxLayout:
            size_hint: (1, 0.10)
            canvas.before:
                Color:
                    rgba:(0,0,1,1)
                Rectangle:
                    pos:self.pos
                    size:self.size
            MDLabel:
                text:"Graph View"
                halign:'center'
                font_style: 'H5'
                color:1,1,1,1
        MDBoxLayout:
            size_hint: (1, 0.90)
            padding:5
            spacing:10
            orientation:'vertical'
            MDBoxLayout:
                id: box
                size_hint_y: 0.55
                pos_hint: {"top":1}
                # graph place
                canvas.before:
                    Color:
                        rgba:(1,1,1,1)
                    Rectangle:
                        pos:self.pos
                        size:self.size
            MDBoxLayout:
                size_hint: (1, 0.075)
                orientation:"horizontal"
                padding:0
                spacing:5
                MDRaisedButton:
                    text:'Daily'
                    font_size:18
                    size_hint_x:1
                    size_hint_y:1
                    forground_color:(.8,0,0,.8)
                MDRaisedButton:
                    text:'Weekly'
                    font_size:18
                    size_hint_x:1
                    size_hint_y:1
                    forground_color:(.8,0,0,.8)
                MDRaisedButton:
                    text:'Monthly'
                    font_size:18
                    size_hint_x:1
                    size_hint_y:1
                    forground_color:(.8,0,0,.8)
            MDBoxLayout:
                size_hint: (1 , 0.25)
            MDBoxLayout:
                size_hint: (1, 0.075)
                orientation:"horizontal"
                MDRoundFlatButton:
                    text:'Back'
                    font_size:18
                    size_hint_x:1
                    size_hint_y:1
                    forground_color:(.8,0,0,.8)
                    on_release:root.manager.current='main'
                Widget:

                
        
        

# ------------------------------- setting page -----------------------
<Setting>:
    name:'setting'
    BoxLayout:
        orientation:'vertical'
        size_hint_x:1
        size_hint_y:1
        BoxLayout:
            size_hint: (1, 0.12)
            canvas.before:
                Color:
                    rgba:(0,0,1,1)
                Rectangle:
                    pos:self.pos
                    size:self.size
            
            MDLabel:
                text:"Setting"
                halign:'center'
                font_style: 'H5'
                color:1,1,1,1
                    
        MDBoxLayout:
            id:contents
            size_hint: (1, 0.88)
            orientation : "vertical"
            padding:10
            MDBoxLayout:
                orientation:'vertical'
                size_hint:(1, 0.40)
                MDTextField:
                    id:name
                    hint_text: "Name"
                    helper_text: "Enter Name"
                    helper_text_mode: "on_focus"
                MDTextField:
                    id:age
                    hint_text: "Age"
                    helper_text: "Enter Age"
                    helper_text_mode: "on_focus"
                MDTextField:
                    id:weight
                    hint_text: "Weight"
                    helper_text: "Enter Weight"
                    helper_text_mode: "on_focus"
                MDTextField:
                    id:height
                    hint_text: "Height"
                    helper_text: "Enter Height"
                    helper_text_mode: "on_focus" 
                MDTextField:
                    id:job
                    hint_text: "Job Designation"
                    helper_text: "Enter Job designtaion"
                    helper_text_mode: "on_focus"
                  
              
            Widget:
                size_hint: (1, 0.10)  
            
            MDBoxLayout:
                orientation:'horizontal'
                size_hint: (1, 0.07)
                spacing:5
                MDRoundFlatButton:
                    text:'Back'
                    font_size:18
                    size_hint_x:1
                    size_hint_y:1
                    forground_color:(.8,0,0,.8)
                    on_release:root.load_main()

                MDRoundFlatButton:
                    id:btn_view
                    text:'View'
                    font_size:18
                    size_hint_x:1
                    size_hint_y:1
                    forground_color:(.8,0,0,.8)
                    on_release: root.view_settings(self.text)
            Widget:
                size_hint: (1, 0.20)  
# ------------------------------- information page -----------------------
<Information>:
    name:'information'
    BoxLayout:
        orientation:'vertical'
        size_hint_x:1
        size_hint_y:1
        BoxLayout:
            size_hint: (1, 0.12)
            canvas.before:
                Color:
                    rgba:(0,0,1,1)
                Rectangle:
                    pos:self.pos
                    size:self.size
            MDLabel:
                text:"Information"
                halign:'center'
                font_style: 'H6'
                color:1,1,1,1
                    
        MDBoxLayout:
            id:info_box
            size_hint: (1, 0.81)
        MDBoxLayout:
            orientation:'horizontal'
            size_hint: (1, 0.07)
            spacing:5
            MDRoundFlatButton:
                text:'Back'
                font_size:18
                size_hint_x:1
                size_hint_y:1
                forground_color:(.8,0,0,.8)
                on_release:root.manager.current='main'

'''
# classes

class Login(Screen):
    def login(self, username, password):
        if username == "ruchita" and password == "ruchita":
            self.manager.current='main'

        else:
            self.ids.statusbar.text = "Wrong Username or Password"

class Main(Screen):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.__DETECTOR_ENABLED = False
        Clock.schedule_interval(self._set_input, 2)
    
    def _set_input(self, dt):
        inp                     = ", ".join( [ "{:.2f}".format(i) for i in mov_detector.single_input] )
        self.ids.lbl_input.text = inp
    
    def notify(self, message):
        self.ids.lbl_status.text = message

    def detect_movement(self, dt):
        def callback(result, dt):
            if result:
                self.notify(f"Your are [{result}]")
        mov_detector.detect(mov_detector.read_input, callback)

    def checkin_detector(self):
        if not self.__DETECTOR_ENABLED:
            Clock.schedule_interval(self.detect_movement, 5)
            self.__DETECTOR_ENABLED = True
            self.notify("Movement Analysis Started")

    def checkout_detector(self):
        if self.__DETECTOR_ENABLED:
            Clock.unschedule(self.detect_movement)
            self.__DETECTOR_ENABLED = False
            self.notify("Movement Analysis Stopped")

    def load_setting(self):
        self.manager.current='setting'


class GraphForm(Screen):
    pass

class Setting(Screen):
    pass

    def _save_settings(self, source):
        data = {}
        for key in ("name", "age", "weight", "height", "job"):
            data[key] = self.ids[key].text
        
        if source == "Save":
            enc_db.save("setting", data)
            
        else:
            enc_db.update("setting", data)
        
        self.load_main()

    def view_settings(self, source):
        if source in ("Save", "Update"):
            self._save_settings(source)

        else:
            result = enc_db.read("SELECT * FROM setting")
            if result is None:
                self.ids.btn_view.text = "Save"

            else:
                self.ids.btn_view.text = "Update"
                for key, value in result.items():
                    self.ids[key].text = value

    def load_main(self):
        for key in ("name", "age", "weight", "height", "job"):
            self.ids[key].text = ""
        
        self.manager.current    = 'main'
        self.ids.btn_view.text  = "View"

class Information(Screen):
    pass


class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = 'Blue'
        return Builder.load_string(kv)
        
       
    
MainApp().run()
