# USAGE
# python search.py --index index.csv --query queries/103100.png --result-path dataset

# import the necessary packages

import tkinter as tk
from tkinter import *
import numpy as np
from PIL import Image, ImageTk
from searcher import Searcher
from DisplayImage import *
import cv2
import pickle
import face_recognition
import sys
import numpy as np
    
def main(args):
  path = './dataset/faces/'
  file_name = args[0]
  
  #load already stored features
  filee = open('./dataset/faces_red.pickle', 'rb')
  _, features, names = pickle.load(filee)
  filee.close()
  # just for these features
  features, names = zip(*[(f[0].reshape(128), n) for f, n in zip(features, names) if f != []])
  features = np.array(features)
  #read query image and generate features 
  query_img = cv2.imread(path+'query_faces/'+file_name)
  q_features = face_recognition.face_encodings(query_img)
  
  # If no features are extrcted
  if q_features == []:
    print('unable to exteract features: ')
    print('Please select a good quality image:')
    return
  else:
    q_features = q_features[0]
  
  #Use Searcher class to search for matched images
  s = Searcher()
  matched_indices = s.search(features, q_features, limit=5)
  
  # if returned with -1 --> No Image found
  if matched_indices == -1:
    print('! No Image Found')
    return
  
  # Look for matched images
  matched_imgs = [cv2.resize(query_img, (250, 250))]
  #read matched_images
  for ind in matched_indices:
    img_path = path+'faces_red/'+names[ind]#+str(ind)+'.jpg'
    img = cv2.imread(img_path)
    img = cv2.resize(img, (250, 250))
    matched_imgs.append(img)

  #display matched images
  root = tk.Tk()
  GUI = DisplayImage(root, matched_imgs)
  GUI.read_image()
  root.mainloop()
  
if __name__ == '__main__':
  main(sys.argv[1:])
      