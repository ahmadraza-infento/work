import os, uuid
from pysqlite import Sqlite
from datetime import datetime, timedelta

class BoxNovelTracker:
    __url__    = "https://boxnovel.com/"
    __source__ = "BoxNovel"
    
    def __init__(self):
        self._db_engine     = Sqlite.init("story_data.db")
        self.load_stories   ()
        self.__filesfolder__= f"{self.__source__}_files"
        
        if not os.path.exists (self.__filesfolder__):
            os.makedirs(self.__filesfolder__)
    
    @property
    def datetime(self):
        return datetime.now().strftime("%Y-%d-%m %H:%M:%S.%f")
    
    @property
    def stories(self):
        self.load_stories()
        return self._stories
    
    def _get_file_path(self, storyid):
        uid    = str(uuid.uuid4()).replace("-", "")
        folder = f"{self.__filesfolder__}/{storyid}" 
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        return f"{folder}/{storyid}{uid}.txt"
    def process_releaseddate(self, released_date):
        if 'day ago' in released_date:
             dt = datetime.now() - timedelta(days=1)
        elif 'days ago' in released_date:
            dt = datetime.now() - timedelta( days=int( released_date.split(" ")[0] ) )
        elif 'hours ago' in released_date:
            dt = datetime.now() - timedelta( hours= int(released_date.split(" ")[0]) )
        elif 'hour ago' in released_date:
            dt = datetime.now() - timedelta( hours=1)
        else:
            dt = datetime.strptime(released_date, "%B %d, %Y")
        
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    
    def load_stories(self):
        data = self._db_engine.read("story", "*", where=f"source='{self.__source__}'")
        self._stories = { s['name']:s for s in data} if len(data) > 0 else {}
        
    def exists(self, name):
        """ return true if story already exists otherwise false """
        return True if name in self._stories.keys() else False
    
    def latest_update(self, storyid):
        """ return latest update of given story if update exists otherwise None """
        return self._db_engine.read('storydata', '*', where=f'storyid={storyid}', limit=1, orderby="entrydate DESC", single=True)
    
    def get_existing_chapters(self, storyid):
        """ return all of the scrapped chapters """
        return self._db_engine.read('storydata', '*', where=f'storyid={storyid}', orderby="entrydate DESC")
    
    def save(self, name, url):
        """ save new story into db and reload stories """
        story = {"name":name, "url":url, "source":self.__source__, "sourceurl":self.__url__, "entrydate":self.datetime}
        if self._db_engine.save("story", story):
            self.load_stories(); return True
        else:
            return False
        
    def save_storydata(self, storyid, chapname, releaseddate, content):
        filepath = self._get_file_path(storyid)
        with open(filepath, 'w') as file:
            file.write(content)
        
        released_date = self.process_releaseddate(releaseddate)
        record        = { 'storyid':storyid, 'chaptername':chapname, 'releaseddate':released_date, 
                          'datafile':filepath, 'entrydate':self.datetime}
        return self._db_engine.save('storydata', record)
    
        
    
        