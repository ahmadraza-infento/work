#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 16:55:20 2019

@author: wizdojotech
"""
import tkinter
from tkinter import messagebox
import cv2
import PIL.Image, PIL.ImageTk
import time

from frame_processor import *
from clusterer import Cluster

class App:
  def __init__(self, window, window_title, video_source=0):
   
    
    
    
    self.window = window
    self.window.title(window_title)
    self.video_source = video_source
     
    # open video source (by default this will try to open the computer webcam)
    self.vid = MyVideoCapture(self.video_source)
     
    # Create a canvas that can fit the above video source size
    self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height)
    self.canvas.pack()
    ''' For demo'''
    self.recognized_faces = []
    self.y = 50
    self.photos = {}
    self.btns = {}
    self.labels = {}
    self.count = 0
    ''' demo end'''
    # After it is called once, the update method will be automatically called every delay milliseconds
    self.delay = 1
    self.update()
     
    self.window.mainloop()
 
  def add_details(self):
    messagebox.showinfo("Add Details", "I will add details")
  def update(self):
    # Get a frame from the video source
    ret, frame, faces, result = self.vid.get_frame()
   
    if ret:
      self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
      self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
      
      imgs2display = list(set(result.keys()) - set(self.recognized_faces))
      if len(imgs2display) > 0:
        for im in imgs2display:
          self.draw_face([faces[result[im]['imgs'][0]], result[im]['info']])
          self.recognized_faces.append(im)
      
    self.window.after(self.delay, self.update)
  
  def draw_face(self, data):
    self.photos[self.count] = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(data[0]))
    self.canvas.create_image(self.vid.vid_width, self.y , image=self.photos[self.count], anchor = tkinter.NW)
    print(data[1])
    if data[1] == '':
      # Detail not exist
      self.btns[self.count]=tkinter.Button(self.window, text="Add Details", width=10, height=25, command=self.add_details)
      self.btns[self.count].place(x=self.vid.vid_width+100, y=self.y, width=100, height=30)
      
    else:
      # draw label
      #info = data[1]
      #t = info['Name']+'\n\nLocation: '+info['Location']+'\n\nDetected: '+info['Last Detected']
      #t = str(info[1])+'\n\nLocation: '+str(info[2])+'\n\nDetected: '+str(info[3])
      self.labels[self.count] = tkinter.Label(self.window, justify=tkinter.LEFT, text=data[1])
      self.labels[self.count].place(x=self.vid.vid_width+100, y =self.y)
    self.y += 110
    self.count += 1
 
class MyVideoCapture:
  def __init__(self, video_source=0):
    # Open the video source
    self.vid = cv2.VideoCapture(video_source)
    if not self.vid.isOpened():
      raise ValueError("Unable to open video source", video_source)
   
    # Get video source width and height
    self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.height =self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    # cluster object to cluster faces in a frame
    self.clusterer = Cluster(max_limit=25)
    self.counter = 0
    self.skip_frames = 5
    # Width and height to display video frame
    self.vid_width = 700
    self.vid_height = 800
 
  def get_frame(self):
    if self.vid.isOpened():
      ret, frame = self.vid.read()
      if ret:
        # Return a boolean success flag and the current frame converted to BGR
        '''Here We have frame and we need to perform all our 
           processing here
        '''
        if self.counter % self.skip_frames == 0:
          #get quality faces
          #print('Entring get_quality_faces...')
          quality_faces = get_quality_faces(frame)
          #print('Returned from get_quality_faces')
          #Put the quality faces into database 
          #print('Enting cluster_faces')
          result = self.clusterer.cluster_faces(quality_faces)
          #print('Returned from cluster_faces')
        
          frame = cv2.resize(frame, (self.vid_width, self.vid_height))
          return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), quality_faces, result)
        self.counter = self.counter + 1
      else:
        return (ret, None, None, None)
    else:
      return (ret, None, None, None)
 
  # Release the video source when the object is destroyed
  def __del__(self):
    if self.vid.isOpened():
      self.vid.release()
 
if __name__ == '__main__':
  # Create a window and pass it to the Application object
  #video_path = input("Enter Path of video: \n")
  video_path = './dataset/videos/dojo_team.MOV'
  App(tkinter.Tk(), "Facial Recognition Demo", video_source=video_path)
  
  
'''  
path = '/home/wizdojotech/CBIR1/'

store = {}
features = []
index_to_key = {}
index = 0
key = 1
for root, dirs, files in os.walk(path+'Clustered/1'):
  for file in files:
    try:
      p = os.path.join(root, file)
      img = cv2.imread(p)
      f = face_recognition.face_encodings(img)
      features.append(f[0])
      if key in store.keys():
        store[key]['data'].append(index)
      else:
        store[key] = {'data':[index], 'is_full':False}
      index_to_key[index] = key
      index = index + 1
    except Exception as e:
      print('error processing ', file)
      
import pickle
file = open(path+'Clustered/st_ft_i2k.pickle', 'wb')
pickle.dump((store, features, index_to_key), file)
file.close()
    
'''