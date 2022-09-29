#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 18:01:30 2019

@author: wizdojotech
"""

import numpy as np
import cv2
import math
import face_recognition

def euclidean_distance(x, y):
    distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(x, y)]))
    return distance
cls_path = '/home/wizdojotech/CBIR1/haarcascade_eye.xml'
img_path = '/home/wizdojotech/CBIR1/Clustered/'
img = cv2.imread(img_path + '1/127.jpg')

img1 = cv2.imread(img_path+'0/0.jpg')

hist, _ = np.histogram(img, bins=100, density=True)
hist1, _ = np.histogram(img1, bins=100, density=True)

euclidean_distance(hist, hist1)*100
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
land_mark = face_recognition.face_landmarks(img, model='small')
land_mark1 = face_recognition.face_landmarks(img1, model='small')

#detect eyes
eye_cascade = cv2.CascadeClassifier(cls_path)
eyes = eye_cascade.detectMultiScale(img1)