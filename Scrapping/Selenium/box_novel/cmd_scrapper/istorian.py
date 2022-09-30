
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
from pysqlite import Sqlite
import firebase_admin
import os

from selenium.webdriver.common.by import By
from boxnovel import BoxNovelTracker
import chromedriver_autoinstaller
from selenium import webdriver
import time

class IStorian():

    def __init__(self):
        self._max_records_to_upload = 5000

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
        return "".join([c for c in string if c.isalpha() or c.isdigit() ])
    
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

    def _setup_chrome(self):
        try:
            chromedriver_autoinstaller.install()
            return True
        except Exception as e:
            print(e)

    def _scrap(self):
        if self._setup_chrome():
            opt = webdriver.ChromeOptions()
            opt.add_argument("--start-maximized")
            driver  = webdriver.Chrome(options=opt)
            tracker = BoxNovelTracker()

            #region scrap stories
            page_no = 1
            MAX_TRY = 3

            while True:
                url = f"https://boxnovel.com/page/{page_no}/"
                count = 0
                while count < MAX_TRY:
                    try:
                        driver.get(url)
                        break
                    except:
                        print(f"[{count}/{MAX_TRY}] failed to fetch url ({url}) - retrying ", end="\r")
                        count += 1
                        time.sleep(2)
                
                if count < MAX_TRY:
                    if driver.title == "Page not found – BoxNovel":
                        print('stories scrapped successfully')
                        break
                        
                    stories = driver.find_elements(By.CLASS_NAME, "item-summary")
                    if len(stories) > 0:
                        for s in stories:
                            atag = s.find_element(By.TAG_NAME, "a")
                            name = atag.text
                            url  = atag.get_attribute("href")
                            if not tracker.exists(name):
                                tracker.save(name, url)
                    
                    else:
                        print('no stroy found at ', url)
                
                else: 
                    print('skipping ', url)
                page_no += 1      
            #endregion

            """ region scrapping chapters """
            driver1 = webdriver.Chrome(options=opt)
            stories = tracker.stories
            c = 0
            for key, story in stories.items():
                count = 0
                while count < 3:
                    try   : driver.get(story["url"]); break
                    except: count +=1 
                time.sleep(3)
                if count < 3:
                    try: driver.find_element(By.CLASS_NAME, 'chapter-readmore').click(); time.sleep(1)
                    except:pass
                    chapters = driver.find_elements(By.CLASS_NAME, 'wp-manga-chapter    ')
                    
                    latest_record = tracker.latest_update(story['id'])
                    if latest_record is None:
                        print(f'no record found for {story["id"]} - fethcing all of its chapters')

                        print(f'fetching {len(chapters)} for ', story["id"])
                        for i, chapter in enumerate(chapters):
                            try:
                                atag     = chapter.find_element(By.TAG_NAME, 'a')
                                chaplink = atag.get_attribute("href")
                                chapname = atag.text
                                rdate    = chapter.find_element(By.XPATH, "//span[@class='chapter-release-date']").text
                                driver1.get(chaplink)
                                time.sleep(1)
                                content      = driver1.find_element(By.CLASS_NAME, "entry-content")
                                chapter_text = content.find_element(By.CLASS_NAME, "text-left")

                                ps           = chapter_text.find_elements(By.TAG_NAME, "p")
                                ps_text      = "\n".join( [p.text for p in ps] )

                                tracker.save_storydata(story["id"], chapname, rdate, ps_text)

                            except:print('failed to fetch chapter ', i)
                            print(f'[{i}/{len(chapters)}]', end='\r')
                    
                    else:
                        print(f'chapters found for {story["id"]} - fetching its latest chapters')
                        saved_chapters  = [c['chaptername'] for c in tracker.get_existing_chapters( story["id"] ) ]
                        new_chapters    = [ (chapter.find_element(By.TAG_NAME, 'a').get_attribute("href"),
                                            chapter.find_element(By.TAG_NAME, 'a').text,
                                            chapter.find_element(By.XPATH, "//span[@class='chapter-release-date']").text)
                                        for chapter in chapters]
                        chapters_to_save= [c for c in new_chapters if c[1] not in saved_chapters]
                        print(f'fetching {len(chapters_to_save)} new chapters for ', story["id"])
                        for i, chap in enumerate(chapters_to_save):
                            try:
                                driver1.get(chap[0])
                                time.sleep(1)
                                content      = driver1.find_element(By.CLASS_NAME, "entry-content")
                                chapter_text = content.find_element(By.CLASS_NAME, "text-left")

                                ps           = chapter_text.find_elements(By.TAG_NAME, "p")
                                ps_text      = "\n".join( [p.text for p in ps] )

                                tracker.save_storydata(story["id"], chap[1], chap[2], ps_text)
                            except:pass
                            print(f'[{i}/{len(chapters_to_save)}]', end='\r')
                
                else:
                    print('failed to load ', story['url'], ' - skipping it')
             
        else:
            print('failed to setup chrome - please try again')

    def _upload(self):
        """ upload stories for simple console app """
        def authenticate():
            try:
                cred = credentials.Certificate("storyscrapper-privatekey.json")
                firebase_admin.initialize_app(cred)
                return True
            
            except Exception as e:
                print(e)

        def sync_data():
            mydb = Sqlite('story_data.db')
            sync = mydb.read('sync', "*", single=True)
            if sync is None:
                sync = {'entrydate':'1970-02-09 00:00:00.000000'}
                mydb.save('sync', sync)

            nowdt 		= datetime.now().strftime("%Y-%d-%m %H:%M:%S.%f")
            latestdt    = nowdt
            query 		= f"""  SELECT s.name as story, s.source, sd.chaptername, 
                                sd.datafile as content, sd.entrydate 
                                FROM storydata as sd JOIN story as s  
                                ON sd.storyid=s.id 
                                WHERE sd.entrydate >  '{sync['entrydate']}' 
                                AND sd.entrydate <= '{nowdt}' ORDER BY sd.entrydate DESC 
                                LIMIT {self._max_records_to_upload}"""

            stories 	= mydb.execute_select(query, True)
            if stories is not None:
                for i, s in enumerate(stories):
                    with open(s['content'], 'r') as f:
                        datalines 	= f.readlines()
                        s['content']= "".join( datalines )
                        if i == 0:
                            latestdt = s['entrydate']
                        s.pop('entrydate', None)

            
            try:
                stories		= {} if stories is None else stories
                print       ('pushing {} records - please be patient'.format(len(stories)) )
                storiesRef 	= ref.child("stories")
                storiesRef.set	(stories)
                status.set		({'value':0})
                mydb.update('sync', {'entrydate':latestdt})
                print('records pushed successfully')
            except Exception as e:
                print(e)
                print('failed to push records - please try again')
                storiesRef 	= ref.child("stories")
                storiesRef.set	({})
        
        if authenticate() is True:
            
            ref     = db.reference(url="https://storyscrapper-1292e-default-rtdb.firebaseio.com/")
            status 	= ref.child("status")
            s 		= status.get()
            if s is None: 
                sync_data()
            
            else:
                if s['value'] == 1:
                    print('resyncing data')
                    sync_data()
                
                elif s['value'] == 0:
                    print("previous record is not downloaded by client yet")	
        
        else:
            print('failed to connect with db - please try again')


    def run(self):
        op = input("enter operation type Scrap(S)/Upload(U) ? >>>").lower()
        
        if op == 's':
            self._scrap()
        elif op == 'u':
            self._upload()
        
        else:
            print("unable to connect with database - please try again later")

        _ = input("\n press enter to exit >>>")
    


if __name__=="__main__":
    IStorian().run()