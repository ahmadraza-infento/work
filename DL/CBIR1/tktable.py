#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 17:11:59 2020

@author: wizdojotech
"""

from tksheet import Sheet
import tkinter as tk

class demo(tk.Tk):
  
  def __init__(self):
    tk.Tk.__init__(self)
    #self.grid_columnconfigure(0, weight = 1)
    #self.grid_rowconfigure(0, weight = 1)
    self.sheet_demo = Sheet(self, height = 500, width=700)
    
    self.sheet_demo.place(x=100, y=100, width=500, height=100)
    #self.sheet_demo.grid(row = 0, column = 0, sticky = "nswe")
    self.data = self.sheet_demo.set_sheet_data([[f"Row {r} Column {c}" for c in range(5)] for r in range(5)], verify = False)
    self.sheet_demo.set_all_cell_sizes_to_text()
  



if(__name__ == '__main__'):
  app = demo()
  app.mainloop()
    
    