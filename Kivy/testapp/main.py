import os
from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget

class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Purple"

    def add_item(self, text):
        new_list_item = OneLineIconListItem(text=text)
        new_list_item.add_widget(
            IconLeftWidget(icon = "language-python")
            )
        self.root.ids.listcontainer.add_widget(new_list_item)
        self.root.ids.listinput.text = ''

    def button_pressed(self):
        try:
            status = os.path.abspath(os.path.dirname(__file__))
            from playsound import playsound
            file_name = os.path.join(status, "testfile.mp3")
            playsound(file_name)
            status = file_name + " played successfully"
        except Exception as e:
            status = status + f" [E] {e}" 

        finally:
            self.root.ids.lbl.text = status

if __name__ == "__main__":
    app = MainApp()
    app.run()