#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 10:26:36 2019

@author: wizdojotech
"""

# import required libraries=
import cv2
import os
import face_recognition
import numpy as np
import pickle
import pandas as pd

from searcher import Searcher

class Cluster:
  def __init__(self, max_limit=15):
    '''
      temporary code for demo
    '''
    # file = open('./Clustered/st_ft_i2k.pickle', 'rb')
    # data = pickle.load(file)
    # file.close()
    # self.store = data[0]
    # self.features = data[1]
    # self.index_to_key = data[2]
    # self.curr_key = len(self.store)-1
    '''End'''
    # Searcher object, to search for specific image
    self.searcher = Searcher()
    #Max limit for number of samples in a cluster
    self.limit = max_limit
    #dictionary to hold clustered Images
    self.store = {}
    
    #features and indices of clustered objecs
    self.features = []
    #Current key for 'store' 
    self.curr_key = -1
    # Look-up table to compute address of stored image
    self.index_to_key = {}
  
  def compute_image_address(self, index):
    '''compute the address of image
        >>> @param:index  -> index of Image
    '''
    return './Clustered/' + str(self.index_to_key[index]) + '/' + str(index) + '.jpg'
  
  def is_full(self, key):
    '''Check if a cluster is full or not
      >>> @param:key  -> key of a cluster
      >>> @return:    -> True, if max limit is reached
                          Otherwise, indices of images in this cluster 
    '''
    
    if self.store[key]['is_full']:
      return True
    else:
      return False#self.store[key]['data']
    
  def get_next_key(self):
    ''' Get Key for next cluster '''
    self.curr_key += 1
    return self.curr_key
  
  def get_key(self, indices):
    ''' Get key of cluster with max match
        >>> @param:indices  -> list of indices of existed images
        >>> @return:        -> cluster ID 
    '''
    clusters = [self.index_to_key[i] for i in indices]
    # return most frequent cluster 
    return max(set(clusters), key=clusters.count)
  
  def store_clutered_image(self, key, index, create_new=False):
    ''' store a clusterd image
        >>> @param:   -> key for 'store'
        >>> @return:  -> index of Image
    '''
    
    #if key already exists
    if create_new == False:
      self.store[key]['data'].append(index)
      # If we reach the max limit: then set is_full
      if self.store[key]['is_full'] is False:
        if len(self.store[key]['data']) == self.limit:
          self.store[key]['is_full']  = True
    else:
      #Create a new cluster
      self.store[key] = {'data':[index], 'is_full':False}
    # Maintain look up table
    self.index_to_key[index] = key
    
  def save_face(self, index, key, face):
    '''store clusterd image
        >>> @param:index  -> index of image 
        >>> @param:key    -> key of cluster
        >>> @param:face   -> cv2 face image
    '''
    path = './Clustered/'+str(key)
    
    #if dir does't exist: make dir
    if os.path.exists(path) is False:
      os.makedirs(path)
    
    file_path = path + '/'+str(index)+'.jpg'
    cv2.imwrite(file_path, face)\
  
  def get_info(self, key):
    '''get Information of recognized face from database
        >>> @param:key  -> key of recognized face
        >>> @return:    -> info regarding input face
    '''
    data = pd.read_excel('./Clustered/Info.xlsx')
    tmp = list(data['Id'])
    if key in tmp:
      info = data.iloc[tmp.index(key)]
      t = str(info[1])+'\n\nLocation: '+str(info[2])+'\n\nDetected: '+str(info[3])
      
      return t
    else:
      return ''
      
  def cluster_faces(self, faces):
    '''put a face into respective cluster
        >>> @param:faces  -> list of faces
    '''
    result = {}
    for i, face in enumerate(faces):
      # get features of input image 
      q_features = face_recognition.face_encodings(face)
      # If no features are extrcted, skip this face
      if q_features == []:
        continue
      else:
        q_features =  q_features[0] 
      
      key = None # Key for a cluster
      index = None # Index of face in 'q_features'
      
      # if there is not any cluster, create first one
      if len(self.features) == 0:
        #get key for new cluster
        key = self.get_next_key()
        index = 0
        print('Creating cluster {}...'.format(key))
        self.store_clutered_image(key, index, create_new=True)
        self.features.append(q_features.reshape(128))
        
      else:
        #perform searching
        #Use Searcher class to search for matched images
        matched_indices = self.searcher.search_fc(np.array(self.features), q_features, limit=5)
        #matched_indices = self.searcher.search(self.features, q_features, limit=5)
        
        # if returned with -1 --> No Match found, create new cluster
        if matched_indices == -1:
          #get key for new cluster
          key = self.get_next_key()
          index = len(self.features)# current len is next index.
          print('Creating cluster {}...'.format(key))
          self.store_clutered_image(key, index, create_new=True)
          self.features.append(q_features.reshape(128))
          
        else:
          # key for matching cluster
          key = self.get_key(matched_indices)
          if not self.is_full(key):
            index = len(self.features)# current len is next index.
            self.store_clutered_image(key, index, create_new=False)
            self.features.append(q_features.reshape(128))
          else:
            continue
      # save clusterd face
      self.save_face(index, key, face)
      '''For demo '''
      if key in result.keys():
        result[key]['imgs'].append(i)
      else:
        result[key] = {'imgs':[i], 'info':self.get_info(key)}
      '''For demo'''
    return result
