
import kivy
import os
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.app import App
from kivy.core.window import Window
from functools import partial
from kivy.uix.modalview import ModalView


ai_model = None
db_engine= None

Window.size=(300,500)

Builder.load_string(""" 
<Notification>:
    auto_dismiss: True
    BoxLayout:
        orientation : "vertical"
        Label:
            id          : lbl_notif
            text        : "This is sample notification"
        #     size_hint_y : 0.5 
        # Button:
        #     text        : "OK"
        #     size_hint_y : 0.5 
        #     on_release  : root.close_popup()
""")
class Notification(ModalView):
    def __init__(self, **kwargs) -> None:
        super(Notification, self).__init__(**kwargs)

    def show(self, notification):
        """ set notification and display popup 
            >>> @param:notification -> message to be displayed in notification box
        """
        self.ids.lbl_notif.text = notification
        self.open()
    
    def close_popup(self):
        self.dismiss()

Builder.load_string(""" 
<Setting>:
    size_hint   : (0.9, 0.65)
    auto_dismiss: False
    BoxLayout:
        orientation : "vertical"
        TextInput:
            id          : notifications
            multiline   : False
            text        : ""
            hint_text   : "# Notifications"
        
        TextInput:
            id          : name
            multiline   : False
            text        : ""
            hint_text   : "Name"
        
        TextInput:
            id          : age
            multiline   : False
            text        : ""
            hint_text   : "Age"
        
        TextInput:
            id          : weight
            multiline   : False
            text        : ""
            hint_text   : "Weight"
        
        TextInput:
            id          : height
            multiline   : False
            text        : ""
            hint_text   : "Height"
        
        TextInput:
            id          : position
            multiline   : False
            text        : ""
            hint_text   : "Job Position"
        
        TextInput:
            id          : profile
            multiline   : False
            text        : ""
            hint_text   : "Movement Profile"

        BoxLayout:
            Button:
                id          : btn_action
                text        : "Save"
                on_release  : root.save_records(self.text)
            
            Button:
                text        : "Close"
                on_release  : root.close_popup()

        
""")
class Setting(ModalView):
    def __init__(self, main_parent, **kwargs) -> None:
        super(Setting, self).__init__(**kwargs)
        self._main_parent = main_parent

    def _read_records(self):
        """ read & populate records from database table """
        data = None#db_engine.read("setting")
        if data is not None:
            for key, val in data.items():
                self.ids[key].text = val
            self.ids.btn_action.text = "Update"

    def show(self):
        """ display setting popup """
        self._read_records  ()
        self.open           ()
    
    def save_records(self, type):
        """ save records into the database 
            >>> @param:type -> [Save/Update] flag to decide db operation 
        """
        data = {}
        for key in ("notifications", "name", "age", "weight", "height", "position", "profile"):
            data[key] = self.ids[key].text
        
        if type == "Save":
            pass#db_engine.save("setting", data)
        
        else:
            pass#db_engine.update("setting", data)

        self.close_popup()

    def close_popup(self):
        self.dismiss()

Builder.load_string(""" 
<Motivation>:
    size_hint   : (0.9, 0.55)
    auto_dismiss: False
    BoxLayout:
        orientation : "vertical"
        BoxLayout:
            CheckBox:
                id          : sitting
                size_hint_x : 0.2
                group       : "motivation"
                on_active   : root.on_option(sitting.active, "lbl_sitting")
            
            Label:
                id  : lbl_sitting
                size_hint_x : 0.8
                text: "Task For Sitting"
        BoxLayout:
            CheckBox:
                id      : walking
                size_hint_x : 0.2
                group   : "motivation"
                on_active   : root.on_option(walking.active, "lbl_walking")
            
            Label:
                id  : lbl_walking
                size_hint_x : 0.8
                text: "Task For Walking"
        BoxLayout:
            CheckBox:
                id      : running
                size_hint_x : 0.2
                group   : "motivation"
                on_active   : root.on_option(running.active, "lbl_running")
            
            Label:
                id  : lbl_running
                size_hint_x : 0.8
                text: "Task For Running"
        BoxLayout:
            Label:
                size_hint_x : 0.05
            Button:
                text        : "Close"
                size_hint_x : 0.9
                on_release  : root.close_popup()
            Label:
                size_hint_x : 0.05
        Label:
            size_hint_y : 0.1

        
""")
class Motivation(ModalView):
    def __init__(self, main_parent, **kwargs) -> None:
        super(Motivation, self).__init__(**kwargs)
        self._main_parent = main_parent
        self._ignore        = False

    def on_option(self, value, task):
        if self._ignore:
            self._ignore = False
            return

        if value:
            keys        = ["sitting", "walking", "running"]
            t           = task.split("_")[1]
            keys.remove (t)
            data        = {t:self.ids[task].text}
            for key in keys:
                data[key] = ""

            if False:#db_engine.read("motivation") is None:
                db_engine.save("motivation", data)

            else:
                pass#db_engine.update("motivation", data) 
    
    def show(self):
        data = None #db_engine.read("motivation")
        if data is not None:
            for key, val in data.items():
                if val != "":
                    self._ignore = True
                    self.ids[key].active = True
                    break
        
        self.open()

    def close_popup(self):
        self.dismiss()

Builder.load_string(""" 
<Login>:
    size_hint   : (0.95, 0.45)
    auto_dismiss: False
    BoxLayout:
        orientation : "vertical"
        Label:
            size_hint_y : 0.15
            text    : "Enter Credentials"

        BoxLayout:
            size_hint_y : 0.25
            Label:
                size_hint_x : 0.05
            TextInput:
                id          : username
                multiline   : False
                size_hint_x : 0.9
                text        : ""
                hint_text   : "Username"
            Label:
                size_hint_x : 0.05   
        BoxLayout:
            size_hint_y : 0.25
            Label:
                size_hint_x : 0.05
            TextInput:
                id          : password
                multiline   : False
                size_hint_x : 0.9
                text        : ""
                password    : True
                hint_text   : "Password" 
            Label:
                size_hint_x : 0.05  
            
        BoxLayout:
            size_hint_y : 0.25
            Label:
                size_hint_x : 0.05
            Button:
                text        : "Login"
                size_hint_x : 0.9
                on_release  : root.on_login(username.text, password.text)
            Label:
                size_hint_x : 0.05
        Label:
            size_hint_y : 0.1

        
""")
class Login(ModalView):
    def __init__(self, main_parent, **kwargs) -> None:
        super(Login, self).__init__(**kwargs)
        self._main_parent = main_parent

    def on_login(self, username, password):
        if username == "john" and password == "root":
            self.close_popup()
        
        else:
            self._main_parent.display_notification("Wrong username or password")
    
    def show(self):
        data = None #db_engine.read("motivation")
        if data is not None:
            for key, val in data.items():
                if val != "":
                    self._ignore = True
                    self.ids[key].active = True
                    break
        
        self.open()

    def close_popup(self):
        self.dismiss()

Builder.load_string("""
<Main>:
    orientation : "vertical"
    size_hint_x : 1
    size_hint_y : 1
    canvas.before:
        Color:
            rgba:(1,1,1,1)
        Rectangle:
            pos:self.pos
            size:self.size
    Label: 
        color       : (0, 0, 0, 1)
        text        : "Welcome"
        size_hint_y : 0.1

    Button:
        text        : "Check In"
        on_release  : root.on_check_in()
        size_hint_y : 0.2
    
    Button:
        text        : "Check Out"
        on_release  : root.on_check_out()
        size_hint_y : 0.2
    
    Button:
        text        : "Pause"
        on_release  : root.on_pause()
        size_hint_y : 0.2

    Button:
        text        : "Settings"
        on_release  : root.on_setting()
        size_hint_y : 0.2
    
    Button:
        text        : "Motivation Tasks"
        on_release  : root.on_motivation()
        size_hint_y : 0.2
""")
class Main(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self._notifier              = Notification()
        self._notifier.size_hint    = (0.9, 0.2) 
        self._notifier.pos_hint     = {'x': 0.05, 'y': 0.8}
        self._pause                 = False
        self._predict_span          = 5
        self._ai_enabled            = False
        Clock.schedule_once         (self.auth, 1)


    def auth(self, dt):
        Login(self).open()    

    def display_notification(self, notification):
        self._notifier.show(notification)

    def predict_state(self, dt):
        def callback(result, dt):
            if not self._pause:
                if result is not None:
                    self.display_notification(f"Your current state is '{result}'")
                
                else:
                    self.display_notification("Something bad has happened with AI!")
            
            else:
                print("notification is paused")

        #ai_model.test_predict_th(callback)
        
    def on_check_in(self):
        """ start AI state prediction """
        if not self._ai_enabled:
            Clock.schedule_interval(self.predict_state, self._predict_span)
            self._ai_enabled = True

    def on_check_out(self):
        """ Stop AI state prediction """
        if self._ai_enabled:
            Clock.unschedule( self.predict_state )
            self._ai_enabled = False

    def on_pause(self):
        self._pause = not self._pause

    def on_motivation(self):
        Motivation(self).show()

    def on_setting(self):
        Setting(self).show()

    def on_exit(self):
        App.get_running_app().stop()
        

    

class MainApp(App):

    def build(self):
        return Main()

if __name__=="__main__":
    mp=MainApp()
    mp.run()