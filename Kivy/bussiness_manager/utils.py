from sqlite import SQLite
from datetime import datetime

from loges import Logger

class AppData():
    def __init__(self) -> None:
        
        self._dbengine      = SQLite.get_driver("./", "app_data.db")

    @property
    def bussinesses(self):
        return [{"id":0, "name":"Fiver"}, {"id":1, "name":"Job"}]
        

    def bussiness_entries(self, bussiness_id:int):
        return {0:[{"id":0, "detail":"entry detail", "amount":5400}], 
                1:[{"id":1, "detail":"detail 1", "amount":3200}]}[bussiness_id]

    def save_bussiness(self, name:str):
        pass

    def save_entry(self, bussiness_id:int, cat_id:int, detail:str):
        pass

    def reset_cursor(self, _type:str):
        pass
    
if __name__ == "__main__":
    input("press enter to exit")