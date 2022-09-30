
from firebase_admin import credentials
from firebase_admin import db
import firebase_admin
import os

class IStorian():

    def _authenticate(self):
        try:
            cred = credentials.Certificate("storyscrapper-privatekey.json")
            firebase_admin.initialize_app(cred)
            return True
        except Exception as e:
            print(e); return False

    def _dst_folder(self):
        folder = input('enter folder path to save chapters >>>')
        if os.path.exists(folder):
            self._folder = folder; return True
        
        else:
            i=input(f'{folder} not available - Would you like to create directory (Y/n)? >>>')
            if i not in ("n", "N"):
                os.makedirs(folder); self._folder=folder; return True
            else:
                return False 

    def _remove_invalid_chars(self, string):
        string = string.replace(" ", "_")
        return "".join([c for c in string if c.isalpha() or c.isdigit() or c == '_' ])
    
    def _generate_filepath(self, source, story, chapter):
        try:
            story   = self._remove_invalid_chars(story)
            chapter = self._remove_invalid_chars(chapter)
            storydir= os.path.join(self._folder, source, story)
            if not os.path.exists(storydir):
                os.makedirs(storydir)
            return os.path.join(storydir, f"{chapter}.txt")

        except Exception as e:
            print(e); return None


    def _job(self):
        ref = db.reference(url="https://storyscrapper-1292e-default-rtdb.firebaseio.com/")
        status 	= ref.child("status")
        s 		= status.get()
        if s is None:
            print("no data available")
        
        else:
            if s['value'] == 1:
                print("no new update available")
                status.update( {"value":0} )
            
            else:
                storiesRef 	= ref.child("stories")
                print("downloading stories - please be patient")
                stories 	= storiesRef.get()
                if stories is not None:
                    if len(stories) > 0:
                        print(f"{len(stories)} new chapters found - saving")
                        for i, s in enumerate(stories):
                            f = self._generate_filepath(s['source'], s['story'], s['chaptername'])
                            if f is not None:
                                try:
                                    with open(f, 'w') as file:
                                        file.write(s['content'])
                                except Exception as e:
                                    print(e)
                            print(f'[{i}/{len(stories)}]', end='\r')
                    else:
                        print("no new chapter available")
                
                else:
                    print("chapters not available")
                
                status.update( {"value":1} )

    def run(self):
        
        if self._authenticate():
            if self._dst_folder():
                self._job()
                _ = input('press enter to exit >>>')
        else:
            print("unable to connect with database - please try again later")
    


if __name__=="__main__":
    IStorian().run()