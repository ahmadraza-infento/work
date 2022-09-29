#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 16:55:20 2019

@author: wizdojotech
"""
import tkinter
import cv2
from tkinter import messagebox
import PIL.Image, PIL.ImageTk
import time

 
class App:
  def __init__(self, window, window_title, video_source=0):
    self.window = window
    self.window.title(window_title)
    self.video_source = video_source
    
    # open video source (by default this will try to open the computer webcam)
    self.vid = MyVideoCapture(self.video_source)
    
    self.counter = 0
    self.skip_frames = 5
    # Create a canvas that can fit the above video source size
    self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height)
    self.canvas.pack()
    
    # Button that lets the user take a snapshot
    #self.btn_snapshot=tkinter.Button(window, text="Snapshot", width=50, command=self.snapshot)
    #self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)
    ''' For demo'''
    #self.recognized_faces = []
    #self.y = 50
    #self.photos = {}
    #self.btns = {}
    #self.labels = {}
    #self.count = 0
    ''' demo end''' 
    # After it is called once, the update method will be automatically called every delay milliseconds
    self.delay = 15#15
    self.update()
     
    self.window.mainloop()
  '''
  def add_details(self):
    messagebox.showinfo("Add Details", "I will add details")
  
  #Draw face on form  
  def draw_face(self, data):
    self.photos[self.count] = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(data[0]))
    self.canvas.create_image(self.vid.vid_width, self.y , image=self.photos[self.count], anchor = tkinter.NW)
    #print(data[1])
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
    '''
  def update(self):
    '''Here each frame is being added to form'''
    # Get a frame from the video source
    ret, frame = self.vid.get_frame()
   
    if ret:
      self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
      self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
    self.counter = self.counter + 1  
    self.window.after(self.delay, self.update)
    
 
class MyVideoCapture:
  def __init__(self, video_source=0):
    self.counter = 0
    self.skip_frames = 5
    # Open the video source
    self.vid = cv2.VideoCapture(video_source)
    if not self.vid.isOpened():
      raise ValueError("Unable to open video source", video_source)
    # Width and height to display video frame
    self.vid_width = 700
    self.vid_height = 800
    # Get video source width and height
    self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
 
  def get_frame(self):
    if self.vid.isOpened():
      ret, frame = self.vid.read()
      if ret:
        # Return a boolean success flag and the current frame converted to BGR
        '''Here We have frame and we need to perform all our 
           processing here
        '''
        
        
        '''
        Return the processed frame
        '''
        return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
      else:
        return (ret, None)
    else:
      return (ret, None)
 
  # Release the video source when the object is destroyed
  def __del__(self):
    if self.vid.isOpened():
      self.vid.release()
      
      
 
if __name__ == '__main__':
  # Create a window and pass it to the Application object
  video_path = './dataset/videos/dojo_team.MOV'
  App(tkinter.Tk(), "Anova- A New Journey", video_source=video_path)
