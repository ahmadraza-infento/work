#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 12:30:34 2019

@author: wizdojotech
"""
#import required libraries
import pickle
import cv2
import face_recognition
import sys

from searcher import Searcher
from clusterer import Cluster


  
def main(args):
  
  # Connect with stream:(for now we are working stored faces)
  #read faces, features and names of faces
  '''filee = open('./dataset/faces_red.pickle', 'rb')
  faces, features, names = pickle.load(filee)
  filee.close()
  '''
  filee = open('./dataset/faces_dt.pickle', 'rb')
  faces = pickle.load(filee)
  filee.close()
  filee = open('./dataset/features_dt.pickle', 'rb')
  features = pickle.load(filee)
  filee.close()
  #To hold computed features
  curr_features = []
  
  clusterer = Cluster(max_limit=15)
  #Iterate over detected faces 
  for i, face in enumerate(faces):
    # compute features of current face, for now just read pre-computed
    q_features = features[i] #face_recognition.face_encodings(face)
    
    # If no features are extrcted, skip this face
    if q_features == []:
      continue
    else:
      if len(q_features) == 1:
        q_features =  q_features[0] 
    
    key = None # Key for a cluster
    index = None # Index of face in 'q_features'
    
    # if there is not any cluster, create first one
    if len(curr_features) == 0:
      #get key for new cluster
      key = clusterer.get_next_key()
      index = 0
      print('Creating cluster {}...'.format(key))
      clusterer.store_clutered_image(key, index)
      curr_features.append(q_features)
    else:
      #perform searching
      #Use Searcher class to search for matched images
      s = Searcher(curr_features)
      matched_indices = s.search(q_features, limit=5)
      
      # if returned with -1 --> No Match found, create new cluster
      if matched_indices == -1:
        #get key for new cluster
        key = clusterer.get_next_key()
        index = len(curr_features)# current len is next index.
        print('Creating cluster {}...'.format(key))
        clusterer.store_clutered_image(key, index)
        curr_features.append(q_features)
      else:
        # key for matching cluster
        key = clusterer.get_key(matched_indices)
        index = len(curr_features)# current len is next index.
        clusterer.store_clutered_image(key, index)
        curr_features.append(q_features)
    
    # save clusterd face
    clusterer.save_face(index, key, face)
    
    
if __name__ == '__main__':
  main(sys.argv[1:])