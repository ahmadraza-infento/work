#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 12:12:23 2019

@author: wizdojotech
"""

import tkinter as tk
from tkinter import *
import cv2
import numpy as np
from PIL import Image, ImageTk


class DisplayImage:
  def __init__(self, master, images):
    self.images = images
    self.cur_index = 0                
    self.master = master
    master.title("Input")
    self.image_frame = Frame(master, borderwidth=0, highlightthickness=0, height=20, width=30, bg='white')
    self.image_frame.pack()
    self.image_label = Label(self.image_frame, highlightthickness=0, borderwidth=0)
    self.image_label.pack()
    self.Next_image = Button(master, command=self.read_image, text="Next image", width=17, default=ACTIVE, borderwidth=0)
    self.Next_image.pack()

  def display_image(self, event=None):
    self.cv2image = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGBA)
    self.from_array = Image.fromarray(self.cv2image)
    self.imgt = ImageTk.PhotoImage(image=self.from_array)
    self.image_label.configure(image=self.imgt)
    
  def read_image(self, event=None):
    if self.cur_index == len(self.images):
      self.master.destroy()
      return
    if self.cur_index == 1:
      self.master.title("Matched")
    self.img = self.images[self.cur_index]
    self.cur_index = self.cur_index+1
    self.master.after(10, self.display_image)     