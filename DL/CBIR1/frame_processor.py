#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 11:22:52 2019

@author: wizdojotech
"""

# Packages to import 
import face_recognition 
import cv2
from mtcnn import MTCNN
import numpy as np
'''
  Detect faces from a given frame
  input: a frame 
  output: list of detected faces
'''
def detect_faces(frame):
  boxes = face_recognition.face_locations(frame)
  det_faces = [frame[box[0]:box[2], box[3]:box[1], :] 
      for box in boxes] # y1:y2, x1:x2
  return det_faces

def detect_faces_haar(frame):
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  print(gray.shape)
  face_cascade = cv2.CascadeClassifier('./files/haarcascade_frontalface_default.xml')
  boxes = face_cascade.detectMultiScale(gray, 1.3, 5)
  det_faces = [ frame[y:y+h, x:x+w]
                for (x,y,w,h) in boxes]
  return det_faces

def detect_faces_mtcnn(frame):
  detector = MTCNN()
  result = detector.detect_faces(frame)
  boxes = [r['box'] for r in result] 
  det_faces = [ frame[y:y+h, x:x+w]
                for (x,y,w,h) in boxes]
  return det_faces

def detect_faces_dnn(frame):
  proto = './files/deploy.prototxt.txt'
  model = './files/res10_300x300_ssd_iter_140000.caffemodel'
  net = cv2.dnn.readNetFromCaffe(proto, model)
  (h, w) = frame.shape[:2]
  blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
	(300, 300), (104.0, 177.0, 123.0))
  net.setInput(blob)
  detections = net.forward()
  det_faces = []
  for i in range(0, detections.shape[2]):
    confidence = detections[0, 0, i, 2]
    if confidence > 0.25:
      #print(confidence)
      box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
      (x1, y1, x2, y2) = box.astype("int")
      det_faces.append(frame[y1:y2, x1:x2])
  return det_faces
'''
  Find quality faces from give faces 
  input: list of faces
  output: list of quality faces
'''
def get_quality_faces(frame):
  #print('Entring detect_faces...')
  detected_faces = detect_faces_dnn(frame)
  #print('Detected: ', len(detected_faces))
  #print('returned from detect_faces')
  quality_faces = []
  for face in detected_faces:
    land_mark = face_recognition.face_landmarks(face)

    if len(land_mark) > 0:
      #print(len(land_mark[0].keys()), ' land_marks detected.')
      quality_faces.append(face)
  #print('Quality faces: ', len(quality_faces))
  return quality_faces