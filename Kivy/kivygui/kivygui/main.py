from kivymd.app import MDApp
from kivy.uix.widget import Widget
from kivy.lang import Builder   
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.button import MDRaisedButton
from kivy.properties import StringProperty
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.clock import Clock

from dbengine import DBEngine
from model_data import AIModel, DataReader

import numpy as np
from matplotlib import pyplot as plt
from kivy.garden.matplotlib import FigureCanvasKivyAgg

DataReader.init()
ai_model    = AIModel()
db_engine   = DBEngine.init("app_db.db")
Window.size = (400, 650)

class Login(Screen):
    def verify_credencials(self):
        if self.ids.user.text == "m" and self.ids.Pass.text == 'm':
            self.ids.approved.text = "Sign In approved, Welcome!"
            self.ids.approved.color = (2/255,168/255,63/255,1)
            self.manager.current='mainpage'

        else:
            self.ids.approved.text = "Oop! Sorry, Wrong login data, Try again"
            self.ids.approved.color = (247/255,20/255,20/255,1)

class MainPage(Screen):
    def __init__(self, **kwargs) -> None:
        super(MainPage, self).__init__(**kwargs)
        self._predict_span  = 5
        self._ai_enabled    = False
        self._disable_notif = False
        Clock.schedule_interval(self.update_sensor_input, 1)

    def load_setting(self):
        self.manager.current='setting'

    def load_graphicForm(self):
        self.manager.current = 'graphicform'

    def push_notification(self, notification):
        self.ids.notification_bar.text = notification
        print("[NOTIFICATION] ", notification)

    def predict_state(self, dt):
        def callback(result, dt):
            if result is not None:
                if not self._disable_notif:
                    self.push_notification(f"You are actually [b]{result}[/b].")
                else:
                    self.push_notification("")
            else:
                self.push_notification("Sorry, failed to predict your state!")
            
        ai_model.predict_threaded(DataReader.model_input(200), callback)

    def on_check_in(self):
        if not self._ai_enabled:
            Clock.schedule_interval(self.predict_state, self._predict_span)
            self._ai_enabled = True
            self.push_notification("AI Started!")

    def on_check_out(self):
        if self._ai_enabled:
            Clock.unschedule( self.predict_state )
            self.push_notification("AI Stopped!")
            self._ai_enabled = False

    def on_notif(self, source):
        if self._disable_notif is False:
            source.text         = "Notification Off"
            self._disable_notif = True
        else:
            source.text         = "Notification On"
            self._disable_notif = False

    def update_sensor_input(self, dt): 
        inp = ", ".join( [ "{:.2f}".format(i) for i in DataReader.sensor_input()] )
        try:self.ids.sensor_input.text= inp
        except:pass

class Setting(Screen):
    def __init__(self, **kwargs) -> None:
        super(Setting, self).__init__(**kwargs)
        
    def _read_records(self):
        """ read & populate records from database table """
        data = db_engine.read_setting()
        if data is not None:
            for key, val in data.items():
                self.ids[key].text = val
            self.ids.btn_action.text = "Update"
    
    def load(self):
        self._read_records  ()

    def save_records(self, type):
        """ save records into the database 
            >>> @param:type -> [Save/Update] flag to decide db operation 
        """
        data = {}
        for key in ("name", "age", "weight", "height", "position", "notification"):
            data[key]           = self.ids[key].text
        
        if type == "Save":
            db_engine.save_setting(data)
        
        else:
            db_engine.update_setting(data)
        
        self.clear()

    def clear(self):
        self.ids.btn_action.text    = "Save"
        for key in ("name", "age", "weight", "height", "position", "notification"):
            self.ids[key].text      = ""
        self.manager.current        = 'mainpage'

class MotivationTask(Screen):
    def load_main(self):
        self.manager.current        = 'mainpage'

class GraphicForm(Screen):
    def load_main(self):
        self.manager.current        = 'mainpage'
    
    def _generate_plot(self):
        signal =  np.random.uniform(low=-0.5, high=13.3, size=(5,)) #np.array(signal)
        plt.clf()
        plt.plot(signal)
        plt.xlabel('Time(s)')
        plt.ylabel('signal (norm)')
        plt.grid(True, color='lightgray')
        
    def on_weekly(self):
        self.ids.graph_box.clear_widgets()
        self._generate_plot()
        self.ids.graph_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
    
    def on_monthly(self):
        self.ids.graph_box.clear_widgets()
        self._generate_plot()
        self.ids.graph_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def on_daily(self):
        self.ids.graph_box.clear_widgets()
        self._generate_plot()
        self.ids.graph_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))


class WindowManager(ScreenManager):
    pass

        
class MainApp(MDApp):

    def build(self):
        sm              = ScreenManager()
        sm.add_widget   (Login(name='login'))
        sm.add_widget   (MainPage(name='mainpage'))
        self._settings  = Setting(name='setting')
        sm.add_widget   (self._settings)
        sm.add_widget   (Setting(name='motivation task'))
        self.kv_str     = Builder.load_file('main11.kv')
        return self.kv_str
    
    #def on_start(self):
    #    self.kv_str.get_screen('graphicform').ids.graph_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
if __name__ == '__main__':
    MainApp().run()