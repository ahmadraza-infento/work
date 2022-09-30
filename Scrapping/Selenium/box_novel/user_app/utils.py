import ast
import time
import firebase_admin
from sqlite import SQLite
from datetime import datetime
from firebase_admin import db
from jobsched import JobScheduler
from firebase_admin import credentials

from loges import Logger

class Sync():
    _self = None

    @classmethod
    def init(cls):
        if cls._self is None:
            cls._self = Sync()

    def __init__(self) -> None:
        try:
            cred = credentials.Certificate("storyscrapper-privatekey.json")
            firebase_admin.initialize_app(cred)
        except Exception as e:Logger.exception(e, '__init__', 'utils')
        JobScheduler.schedule(self.job, 10)

    def _block_ui(self, dt=None):
        from main import Loading
        Loading.show(None, "inserting new records- please wait")

    def _unblock_ui(self, dt=None):
        from main import Loading
        Loading.close()

    def _job(self):
        ref = db.reference(url="https://storyscrapper-1292e-default-rtdb.firebaseio.com/")
        status 	= ref.child("status")
        s 		= status.get()
        if s is None:
            Logger.info("no data available")
        
        else:
            if s['value'] == 1:
                Logger.info("no new update available")
            
            else:
                from kivy.clock import Clock
                storiesRef 	= ref.child("stories")
                stories 	= storiesRef.get()
                storydataRef= ref.child("storydata")
                storydata 	= storydataRef.get()
                mydb        = SQLite('app_data.db')
                if stories is not None:
                    if len(stories) > 0:
                        Clock.schedule_once(self._block_ui, 0.05)
                        mydb.save('story', stories)
                        Clock.schedule_once(self._unblock_ui, 0.05)
                    else:
                        Logger.info("no new stories available")
                else:
                    Logger.info("stories not available")
                
                if storydata is not None:
                    if len(storydata) > 0:
                        Clock.schedule_once(self._block_ui, 0.05)
                        mydb.save('storydata', storydata)
                        Clock.schedule_once(self._unblock_ui, 0.05)
                    else:
                        Logger.info("no new storydata available")
                else:
                    Logger.info("storydata not available")
                status.update( {"value":1} )

    def job(self, source):
        from kivy.clock import Clock
        try:self._job()
        except Exception as e:
            Logger.exception(e, 'job', 'utils')
            Clock.schedule_once(self._unblock_ui, 0.5)
        

class DataReader():
    def __init__(self) -> None:
        self._counts        = {'stories':0, 'chapters':0} 
        self._batch_size    = 50
        self._dbengine      = SQLite.get_driver("./", "app_data.db")

    def reset_count(self, key):
        self._counts[key] = 0

    def read_sources(self):
        query= "SELECT source, count(*) as story_count FROM story GROUP By source"
        return self._dbengine.execute_select(query, True)
        

    def read_stories(self, source):
        ignore = self._counts['stories']
        stories =  self._dbengine.read('story', ['id', 'name', 'source'], 
                                    where=f"source='{source}'", limit=f"{ignore}, {self._batch_size}")
        self._counts['stories'] += self._batch_size
        return stories

    def read_chapters(self, storyid):
        ignore = self._counts['chapters']
        chaps = self._dbengine.read('storydata', ['logid', 'chaptername', 'releaseddate', 'copied'], 
                                    where=f"storyid='{storyid}'", limit=f"{ignore}, {self._batch_size}")
        self._counts['chapters'] += self._batch_size
        return chaps

    def read_chapter_content(self, logid, copied):
        content = self._dbengine.read('storydata', ['content'], where=f"logid={logid}", single=True)
        if content is not None:
            self._dbengine.update('storydata', {'copied':copied+1}, where=f"logid={logid}") 
            try:
                return " ".join( ast.literal_eval(content['content']) )
            except:pass


if __name__ == "__main__":
    s = Sync()
    input("press enter to skip")