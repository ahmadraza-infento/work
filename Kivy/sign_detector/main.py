
import kivy
import os
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.app import App
from kivy.core.window import Window
from random import randint
from functools import partial
from model import Camera, AIModel
mycamera = Camera()
ai_model = AIModel()
Window.size=(300,500)

class Mode:
    EASY    = "Easy"
    MEDIUM  = "Medium"
    EXPERT  = "Expert"  

class Questions:
    """ This module contains questions to ask from user """

    _index_to_letter    = { 0:'A', 1:"B", 2:"C", 3:"D", 4:"E", 5:"F", 6:"G", 7:"H",
                            8:"I", 9:"J", 10:"K", 11:"L", 12:"M", 13:"N", 14:"O",
                            15:"P", 16:"Q", 17:"R", 18:"S", 19:"Space", 20:"T", 21:"U",
                            22:"V", 23:"W", 24:"X", 25:"Y", 26:"Z"}
    _question_ranges    = {
                            (Mode.EASY,1):(0, 5),  (Mode.EASY,2):(4, 8), 
                            (Mode.EASY,3):(5, 11), (Mode.EASY,4):(1, 9), 
                            (Mode.EASY,5):(0, 11),

                            (Mode.MEDIUM,1):(12, 14), (Mode.MEDIUM,2):(13, 16),
                            (Mode.MEDIUM,3):(15, 19), (Mode.MEDIUM,4):(17, 20),
                            (Mode.MEDIUM,5):(12, 20),

                            (Mode.EXPERT,1):(21, 23), (Mode.EXPERT,2):(22, 25),
                            (Mode.EXPERT,3):(11, 24), (Mode.EXPERT,4):(),
                            (Mode.EXPERT,5):(0, 26)
                            }
    @classmethod
    def get_question(cls, mode, level):
        """ return a question according to current mode and level
            >>> @param:mode -> one of the modes [EASY, MEDIUM, EXPERT]
            >>> @param:level-> one of the available levels [1, 2, 3, 4, 5]
        """
        _range      = cls._question_ranges[(mode, level)] 
        letter_idx  = randint(_range[0], _range[1])
        return cls._index_to_letter[letter_idx]

class FileHandler:

    @classmethod
    def readline(cls, file):
        """ read first line in file """

        with open(file, 'r') as f:
            line  = f.readline()
        
        return line

    @classmethod
    def writeline(cls, file, line, overwrite=True):
        """ writeline in a file, overwrite content if overwrite is True"""
        mode = "w" if overwrite else "a"
        with open(file, mode) as f:
            f.write(line)
            


# Home Window
class Home(BoxLayout):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent = _parent

    def modes_window(self):
        self._parent.load_mode_selection()

    def tutorial_window(self):
        self._parent.load_tutorials_form()


# tutorial_window
class Tutorials(BoxLayout):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent = _parent
    
    def btn_back_click(self):
        self._parent.home_form()

# PlayScreen form class
class PlayScreen(BoxLayout):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent    = _parent
        self._mode      = None
        self._level     = None
        self._points    = None
        self._result    = False
        self._init_span = 0
        self._max_wait  = 8

    @property
    def init_span_ended(self):
        """ return True if init span is ended else False"""
        self._init_span +=1
        return True if self._init_span > self._max_wait else False

    def init_camera(self):
        mycamera.start()

    def stop_camera(self):
        mycamera.stop()

    def set_status(self, text):
        self.ids.lbl_status.text = text

    def set_data(self, mode, level, points):
        """ set mode, level and points for current question """
        self._mode  = mode
        self._level = level
        self._points= points
        self._result= False 

        self._build_ui()

    def _build_ui(self):
        """ set ui based on user selection """

        self.set_status                 ("")
        self.init_camera                ()
        self.ids.lbl_header.text        = self._mode
        self._asked_char                = Questions.get_question(self._mode, self._level)
        self.ids.lbl_description.text   = f"How to represent '{self._asked_char}' ?"

    def start(self):
        self._init_span = 0
        self.set_status("Please bring your hand inside rectangle")
        self._work_event = Clock.schedule_interval(self._work, 1)
    
    def _work(self, dt=None):
        frame_path, frame       = mycamera.read_frame()
        if frame is not None:
            if self.init_span_ended:
                self._work_event.cancel()
                self.set_status("processing frame - please wait")
                Clock.schedule_once(partial(self._process_frame, frame), 1)
            else:
                self.ids.img_box.source = frame_path

    def _process_frame(self, frame, dt=None):
        letter, score = ai_model.predict_letter(frame)
        if letter == self._asked_char:
            message = f"Success: You have earned {self._points} points"
            self._result= True
            self._parent.add_score(self._points)

        else:
            self._result= False
            message= f"Failed[{letter}]: Please Try Again!"
        
        Clock.schedule_once(partial(self._display_result, message), 1)
        
    def _display_result(self, message, dt):

        self.set_status(message)
        Clock.schedule_once(self.btn_back_click, 3)

    def btn_back_click(self, dt=None):
        self.stop_camera                ()
        self._parent.load_choice_form   (result=self._result, level=self._level)

    
# modes form
class ModeSelection(BoxLayout):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent = _parent

    def choicewindow(self, mode):
        self._parent.load_choice_form(mode=mode)
    
    def btn_back_click(self):
        self._parent.home_form()


# choice form 
class ChoiceForm(BoxLayout):
    def __init__(self,_parent,**kwargs):
        super().__init__(**kwargs)
        self._parent= _parent
        self._mode  = None
        self._levels= (1, 2, 3, 4, 5)
        self._points= {}
        self._multip= {Mode.EASY:2, Mode.MEDIUM:3, Mode.EXPERT:7}

    def _read_done(self, mode=None):

        data    = {}
        _done   = FileHandler.readline("done.dll")
        
        for d in _done.split("_"):
            key = d.split(":")[0]
            vals= d.split(":")[1]
            vals= vals.split(",") if len(vals) > 0 else []
            data[key] = vals 
        
        if mode:
            return [int(v) for v in data[mode]]
        
        else:
            return data

    def _write_done(self, _mode, level):
        data                = self._read_done()
        data[_mode].append  (level)
        _done_strs          = []

        for key, val in data.items():
            val_str             = ",".join([str(v) for v in val]) 
            _done_strs.append   (f"{key}:{val_str}")
        
        FileHandler.writeline("done.dll", "_".join(_done_strs))

    @property
    def mode(self):
        return self._mode

    def set_mode(self, mode):
        self._mode              = mode
        self.ids.lbl_header.text= mode 
        self._load_levels       ()

    def set_result(self, result, level):
        if result:
            self.ids[f'level_{level}'].text = "Done!"
            self._write_done(self._mode, level)
            


    def _load_levels(self):
        
        m   = self._multip.get(self._mode, 3)
        done= self._read_done(self._mode) 
        for level in self._levels:
            if level in done:
                self.ids[f'level_{level}'].text = "Done!"
            
            else:
                reward = level*m
                self.ids[f'level_{level}'].text = f"You will earn {reward} points"
                self._points[level] = reward

    def play_screen_window(self, level):
        if self.ids[f'level_{level}'].text != "Done!":
            self._parent.load_play_screen(level, self._points[level])

    def btn_back_click(self):
        self._parent.load_mode_selection()

# Main app code
class Main(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.main_box = self.ids.main_box
        self.home_form()
        self.add_score(0)

    # load home window
    def home_form(self):
        self.main_box.clear_widgets()
        self.home = vars(self).get("home", Home(self))
        self.main_box.add_widget(self.home)

    # load desc check window
    def load_play_screen(self, level, points):
        self.main_box.clear_widgets()
        self.play_screen = vars(self).get("play_screen", PlayScreen(self))
        self.main_box.add_widget(self.play_screen)
        self.play_screen.set_data(self.choiceform.mode, level, points)
        self.play_screen.start()

    # load modes window
    def load_mode_selection(self):
        self.main_box.clear_widgets()
        self._select_mode = vars(self).get("_select_mode", ModeSelection(self))
        self.main_box.add_widget(self._select_mode)
    
    # load tutorials form
    def load_tutorials_form(self):
        self.main_box.clear_widgets()
        self.tutorials = vars(self).get("tutorials", Tutorials(self))
        self.main_box.add_widget(self.tutorials)

    # load choice form
    def load_choice_form(self, mode=None, result=None, level=None):
        self.main_box.clear_widgets()
        self.choiceform = vars(self).get("choiceform", ChoiceForm(self))
        if mode:
            self.choiceform.set_mode(mode)
        
        if result is not None:
            self.choiceform.set_result(result, level)

        self.main_box.add_widget(self.choiceform)
    
    # add score points
    def add_score(self, points):

        earned_points = int(FileHandler.readline("points.dll"))
        earned_points += points
        FileHandler.writeline("points.dll", f"{earned_points}")
        self.home.ids.btn_score.text = f"Points Earned: {earned_points}"

class MainApp(App):
    def _clear_tmp(self):
        if os.path.exists("tmp"):
            for file in os.listdir("tmp"):
                try     : os.remove(os.path.join("tmp", file))
                except  : pass
        
        else:
            os.makedirs("tmp")


    def build(self):
        self._clear_tmp()
        return Main()

if __name__=="__main__":
    mp=MainApp()
    mp.run()