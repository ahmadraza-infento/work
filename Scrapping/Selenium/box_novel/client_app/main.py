import json
import firebase_admin
from datetime import datetime
from firebase_admin import db
from firebase_admin import credentials
from pysqlite import Sqlite

def create():
	cred = credentials.Certificate("storyscrapper-privatekey.json")
	firebase_admin.initialize_app(cred)
	ref = db.reference(url="https://storyscrapper-1292e-default-rtdb.firebaseio.com/stories")
	data = {"God of Fishing":
				{
					"chapters":
						{	
							"Chapter 1":{"content":"This is content", "entrydate":"2022-09-06 04:54:00"},
							"Chapter 2":{"content":"This is 2 content", "entrydate":"2022-09-06 05:00:00"} 
						},
					"entrydate":"2022-09-06 05:00:00"
				},
			"Astral Pet Store":
				{
					"chapters":
						{	
							"Chapter 1":{"content":"This is 1 content", "entrydate":"2022-09-06 04:58:00"},
							"Chapter 2":{"content":"This is 2 content", "entrydate":"2022-09-06 05:02:00"} 
						},
					"entrydate":"2022-09-06 05:00:00" 
				}
			}
	json_data = data#json.dumps(data)
	ref.set(json_data)

def read():
	cred 	= credentials.Certificate("storyscrapper-privatekey.json")
	firebase_admin.initialize_app(cred)
	ref 	= db.reference(url="https://storyscrapper-1292e-default-rtdb.firebaseio.com/stories")
	stories = ref.get	()#json.loads( ref.get	() )
	print( type(stories) )
	print( stories )

def update():
	cred 	= credentials.Certificate("storyscrapper-privatekey.json")
	firebase_admin.initialize_app(cred)
	ref 	= db.reference(url="https://storyscrapper-1292e-default-rtdb.firebaseio.com/stories")
	stories = ref.get	() #json.loads( ref.get	() )

	for storykey, chaps in stories.items():
		if storykey == 'God of Fishing':
			for chapkey, chapcontent in chaps['chapters'].items():
				ref.child(storykey).child('chapters').child(chapkey).update({'content':'changed content'})

def delete(da=False):
	cred 	= credentials.Certificate("storyscrapper-privatekey.json")
	firebase_admin.initialize_app(cred)
	ref 	= db.reference(url="https://storyscrapper-1292e-default-rtdb.firebaseio.com/stories")
	
	if da:
		ref.set({})

	else:
		stories = ref.get	()
		for storykey, chaps in stories.items():
			if storykey == 'God of Fishing':
				ref.child(storykey).set({})

def upload_stories():
	def sync_data():
		mydb = Sqlite('story_data.db')
		sync = mydb.read('sync', "*", single=True)
		if sync is None:
			sync = {'entrydate':'1970-02-09 00:00:00.000000'}
			mydb.save('sync', sync)

		nowdt 		= datetime.now().strftime("%Y-%d-%m %H:%M:%S.%f")
		stories 	= mydb.read('story', ['id', 'source', 'name'], where=f"entrydate > '{sync['entrydate']}' AND entrydate <= '{nowdt}'")
		story_data 	= mydb.read('storydata', ['storyid', 'chaptername', 'releaseddate', 'datafile as content'], where=f"entrydate > '{sync['entrydate']}' AND entrydate <= '{nowdt}'") 
	
		if story_data is not None:
			for sd in story_data:
				with open(sd['content'], 'r') as f:
					content = "".join( f.readlines() )
					sd['content'] = content
	
		stories		= {} if stories is None else stories
		storydata 	= {} if story_data is None else story_data
		storiesRef 	= ref.child("stories")
		storiesRef.set	(stories)
		storydataRef= ref.child("storydata")
		storydataRef.set(storydata)
		status.set		({'value':0})
		mydb.update('sync', {'entrydate':nowdt})

	cred = credentials.Certificate("storyscrapper-privatekey.json")
	firebase_admin.initialize_app(cred)
	ref = db.reference(url="https://storyscrapper-1292e-default-rtdb.firebaseio.com/")
	
	status 	= ref.child("status")
	s 		= status.get()
	if s is None: 
		sync_data()
	
	else:
		if s['value'] == 1:
			print('resyncing data')
			sync_data()
		
		elif s['value'] == 0:
			if input("Would you like to set value to 1(y/n)?>>>") == 'y':
				status.update({"value":1})

def download_stories():
	cred = credentials.Certificate("storyscrapper-privatekey.json")
	firebase_admin.initialize_app(cred)
	ref = db.reference(url="https://storyscrapper-1292e-default-rtdb.firebaseio.com/")
	
	status 	= ref.child("status")
	s 		= status.get()
	if s is None:
		print("no data available")
	
	else:
		if s['value'] == 1:
			print("no new update available")
		
		else:
			storiesRef 	= ref.child("stories")
			stories 	= storiesRef.get()
			storydataRef= ref.child("storydata")
			storydata 	= storydataRef.get()
			mydb = Sqlite('app_data.db')
			if stories is not None:
				if len(stories) > 0:
					#stories = [val for key, val in stories.items() ]
					mydb.save('story', stories)
				else:
					print("no new stories available")
			else:
				print("stories not available")
			
			if storydata is not None:
				if len(storydata) > 0:
					#storydata = [val for key, val in storydata.items() ]
					mydb.save('storydata', storydata)
				else:
					print("no new storydata available")
			else:
				print("storydata not available")
			status.update( {"value":1} )

def upload_stories_cmd():
	""" upload stories for simple console app """
	def sync_data():
		mydb = Sqlite('story_data.db')
		sync = mydb.read('sync', "*", single=True)
		if sync is None:
			sync = {'entrydate':'1970-02-09 00:00:00.000000'}
			mydb.save('sync', sync)

		nowdt 		= datetime.now().strftime("%Y-%d-%m %H:%M:%S.%f")
		query 		= f"SELECT s.name as story, s.source, sd.chaptername, sd.datafile as content FROM storydata as sd JOIN story as s  ON sd.storyid=s.id WHERE sd.entrydate >  '{sync['entrydate']}' AND sd.entrydate <= '{nowdt}' "
		stories 	= mydb.execute_select(query, True)
		if stories is not None:
			for s in stories:
				with open(s['content'], 'r') as f:
					datalines 	= f.readlines()
					s['content']= "".join( datalines )
	
		stories		= {} if stories is None else stories
		storiesRef 	= ref.child("stories")
		storiesRef.set	(stories)
		status.set		({'value':0})
		mydb.update('sync', {'entrydate':nowdt})

	cred = credentials.Certificate("storyscrapper-privatekey.json")
	firebase_admin.initialize_app(cred)
	ref = db.reference(url="https://storyscrapper-1292e-default-rtdb.firebaseio.com/")
	
	status 	= ref.child("status")
	s 		= status.get()
	if s is None: 
		sync_data()
	
	else:
		if s['value'] == 1:
			print('resyncing data')
			sync_data()
		
		elif s['value'] == 0:
			if input("Would you like to set value to 1(y/n)?>>>") == 'y':
				status.update({"value":1})	


def test():
	mydb = Sqlite('story_data.db')
	sync = mydb.read('sync', "*", single=True)
	print("sync -> ", sync)
	if sync is None:
		sync = {'entrydate':'1970-09-02 00:00:00.000000'}
		mydb.save('sync', sync)

def test1():
	cred = credentials.Certificate("storyscrapper-privatekey.json")
	firebase_admin.initialize_app(cred)
	ref = db.reference(url="https://storyscrapper-1292e-default-rtdb.firebaseio.com/")
	status 	= ref.child('status')
	s		= status.get()
	s_value= None if s is None else s.get('value', None)
	if s_value is None:
		print('status value is not available')
		stories = ref.child("stories")
		stories.set	({"story1":{"chapters":{"chap1":{"content":"This is content"}}, "source":"BoxNovel"}})
		status.set	({'value':0})
	
	else:
		print('status value is ', s_value)
		if s_value == 0:
			if input("Would you like to change status to 1(y/n)? >>>") == "y":
				status.update({"value":1})
		elif s_value ==1:
			stories = ref.child("stories")
			stories.set({"story2":{"chapters":{"chap1":{"content":"This is content"}}, "source":"BoxNovel"}})
			status.update({"value":0})
			print("new story uploaded")
	
	#status.set({"value":0})
	
	

if __name__ == '__main__':
	""" https://console.firebase.google.com/u/0/project/storyscrapper-1292e/database/storyscrapper-1292e-default-rtdb/data/~2F
		https://www.freecodecamp.org/news/how-to-get-started-with-firebase-using-python/
	"""
	inp = input("(c/r/u/d/da/us/ds)>>>")
	if inp == "c":
		create()
	elif inp == "r":
		read()
	elif inp == "u":
		update()
	elif inp == "d":
		delete()
	elif inp == "da":
		delete(True)
	elif inp == "us":
		upload_stories()
	elif inp == "ds":
		download_stories()
	else:
		upload_stories_cmd()