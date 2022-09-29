#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 16:55:20 2019

@author: wizdojotech
"""
import tkinter
import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import time
from tksheet import Sheet 
 
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
    self.sheet_demo = Sheet(window, height = self.vid.height, width=self.vid.width)
    self.sheet_demo.place(x=10, y=600, width=690, height=120)
    self.d = self.sheet_demo.set_sheet_data([[f"Row {r} Column {c}" for c in range(5)] for r in range(5)], verify = False)
    self.sheet_demo.set_all_cell_sizes_to_text()
    
    # Button that lets the user take a snapshot
    self.btn_snapshot=tkinter.Button(window, text="Snapshot", width=50, command=self.snapshot)
    self.btn_snapshot.place(x=710, y=600, width=100, height=100)
    # After it is called once, the update method will be automatically called every delay milliseconds
    self.delay = 15
    self.update()
     
    self.window.mainloop()
 
  def snapshot(self):
    # Get a frame from the video source
    #ret, frame = self.vid.get_frame()
    #self.data = self.sheet_demo.set_sheet_data([[f"Row {r} Column {c}" for c in range(5)] for r in range(3)], verify = False)
    self.update_table()
    #if ret:
    #  cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
  def update_table(self):
    data  = [['Name', 'Location', 'Last Detected', 'Frequency'],
              ['Umair Mateen Khan', 'Lahore', 'March 19 2019', '1']]
    self.d = self.sheet_demo.set_sheet_data(data)
  def update(self):
    # Get a frame from the video source
    ret, frame = self.vid.get_frame()
   
    if ret:
      self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
      self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
   
    self.window.after(self.delay, self.update)
  
  def draw_face(self, img):
    self.canvas.create_image()
 
 
class MyVideoCapture:
  def __init__(self, video_source=0):
    # Open the video source
    self.vid = cv2.VideoCapture(video_source)
    if not self.vid.isOpened():
      raise ValueError("Unable to open video source", video_source)
   
    # Get video source width and height
    self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.height =self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    # Width and height to display video frame
    self.vid_width = 700
    self.vid_height = 600
 
  def get_frame(self):
    if self.vid.isOpened():
      ret, frame = self.vid.read()
      if ret:
        # Return a boolean success flag and the current frame converted to BGR
        frame = cv2.resize(frame, (self.vid_width, self.vid_height))
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
  #video_path = input("Enter Path of video: \n")
  video_path = './dataset/videos/dojo_team.MOV'
  #video_path = './dataset/videos/dojo_team.MOV'
  App(tkinter.Tk(), "Tkinter and OpenCV", video_source=video_path)
