import email
from pydoc import isdata
import sqlite3
from functools import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.utils import asynckivy
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager,Screen

Window.size = (350, 600)


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

# for delete or edit confirmation
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
            spacing:5
            padding:2
            MDRoundFlatButton:
                id      :btn_delete
                text:"Delete"
                font_size:15
                size_hint_x:1
                size_hint_y:None
                height:35
                theme_text_color: "Custom"
                text_color: 1, 0, 0, 1
                on_release: root.remove_record()
            
            MDRoundFlatButton:
                text:"Edit"
                id  :btn_edit
                font_size:15
                size_hint_x:1
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
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
            MDRoundFlatButton:
                
                id      :btn_update
                size_hint_x:1
                theme_text_color: "Custom"
                text_color: 0, 0, 0, 1
                    
                text    :"Update"
                bold    :True
                font_size:15
                size_hint_y:None
                height:35
                on_press:root.update_record()
           
            
            BoxLayout:
                size_hint:1,0.071
                
""")

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
  
class WindowManager(ScreenManager):
    pass

class Login(Screen):
    
    def call_dashboard_page(self):
        conn=sqlite3.connect('cm_db.db')
        c=conn.cursor()
        c.execute("SELECT * FROM Registeration")
        admins=c.fetchall()
        if admins:
            for ad in admins:
                if ad[2]==self.ids.txt_email.text:
                    if ad[3]==self.ids.txt_password.text:
                        self.manager.current = 'DashboardPage'
                    else:
                        self.ids.lbl_msg.text="**Password Not Matched**"
                else:
                    self.ids.lbl_msg.text="**Email Not Matched**"
                        
            
        else:
            self.ids.lbl_msg.text="**You don't have any account! Register first**"
            self.ids.btn_register.opacity=1
        conn.commit()
        conn.close()
        self.ids.txt_email.text=''
        self.ids.txt_password.text=''


class DashboardPage(Screen):
    def __init__(self, **kwargs) -> None:
        super(DashboardPage, self).__init__(**kwargs)
        

    def reload_box(self):
        table_box=self.ids.row_widget_box
        table_box.clear_widgets()
        self.show_records()
         
    def show_records(self):
        table_box=self.ids.row_widget_box
        table_box.clear_widgets()
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
            row.bind(on_press=partial(self.call_popup, id))
            table_box.add_widget(row)
        conn.commit()
        conn.close()


    def load_Add_customer_page(self):
        self.manager.current = 'Add_customer_page'

    def call_popup(self, rowid, source):
        
        popup=PopupModal(self,rowid)
        popup.open()

class RegisterPage(Screen):
    def __init__(self, **kwargs) -> None:
        super(RegisterPage, self).__init__(**kwargs)
        # self.auths()

    def auths(self):
        conn=sqlite3.connect('cm_db.db')
        c=conn.cursor()
        c.execute("SELECT * FROM Registeration")
        admins=c.fetchall()
        if admins:
            self.manager.current = 'DashboardPage'
        conn.commit()
        conn.close()
        
    def register_user(self):
        email=self.ids.txt_email.text
        pas=self.ids.txt_password.text
        if email=='':
            self.ids.rg_msg.text="*** Email is Must ***"
        elif pas=='':
            self.ids.rg_msg.text="*** Password is Must ***"
        else:
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
            self.manager.current = 'Login'

class Add_customer_page(Screen):
    def load_main(self):
        name=self.ids.cust_name.text
        if name=='':
            self.ids.form_mesg.text="Customer name field is Must"
        else:
            self.ids.form_mesg.text=""
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

            self.manager.get_screen('DashboardPage').reload_box()
            self.manager.current ='DashboardPage'
class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = 'Blue'
        # self.strng = Builder.load_string(kv)
        sm              = ScreenManager()
        self._RegisterPages  = RegisterPage(name='RegisterPage')
        sm.add_widget   (self._RegisterPages)
        sm.add_widget   (Login(name='Login'))
        sm.add_widget   (DashboardPage(name='DashboardPage'))
        

        self.string=Builder.load_file('main.kv')
        return self.string

    def on_start(self):
        
        conn=sqlite3.connect('cm_db.db')
        c=conn.cursor()
        c.execute("SELECT * FROM Registeration")
        admins=c.fetchall()
        if admins:
            self.root.current= 'Login'
            logedin=True
            conn.commit()
            conn.close()
        else:
            self.root.current= 'RegisterPage'
        
        # for auto load records
        
        
        table_box=self.string.get_screen('DashboardPage').ids.row_widget_box
        table_box.clear_widgets()
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
            row.bind(on_press=partial(self.string.get_screen('DashboardPage').call_popup, id))
            table_box.add_widget(row)
        conn.commit()
        conn.close()
        # self.string.get_screen('Add_customer_page').ids.graph_box.add_widget(Label(text='new button'))

if __name__ == '__main__':
    MainApp().run()