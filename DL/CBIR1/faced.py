#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 11:10:49 2019

@author: wizdojotech
"""

import cv2
from mtcnn import MTCNN
from faced import FaceDetector
from faced.utils import annotate_image

def detect_faces_mtcnn(frame):
  detector = MTCNN()
  result = detector.detect_faces(frame)
  boxes = [r['box'] for r in result] 
  det_faces = [ frame[y:y+h, x:x+w]
                for (x,y,w,h) in boxes]
  return det_faces

def detect_faces_haar(frame):
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  print(gray.shape)
  face_cascade = cv2.CascadeClassifier('/home/wizdojotech/CBIR1/haarcascade_frontalface_default.xml')
  result = face_cascade.detectMultiScale(gray, 1.3, 5)
  det_faces = [ frame[y:y+h, x:x+w]
                for (x,y,w,h) in boxes]
  return det_faces

img_path = '/home/wizdojotech/detect_faces/input/img1.jpg'
img = cv2.imread(img_path)
rgb_img = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGB)


# Receives RGB numpy image (HxWxC) and
# returns (x_center, y_center, width, height, prob) tuples. 
face_detector = FaceDetector()

bboxes = face_detector.predict(rgb_img, thresh)

faces = detect_faces_mtcnn(img)

 
