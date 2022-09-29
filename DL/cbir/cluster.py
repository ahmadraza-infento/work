#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 12:30:34 2019

@author: wizdojotech
"""
#import required libraries
import os
import sys
from searcher import Searcher
from clusterer import Cluster
from feature_extractor import get_hog
from skimage.io import imread, imsave


  
def main(folder_to_search):
  img_paths     = os.listdir(folder_to_search)
  curr_features = []
  clusterer     = Cluster(max_limit=15)
  for i, ipath in enumerate(img_paths):
    imgpath   = os.path.join(folder_to_search, ipath)
    q_features= get_hog(imgpath)
    img       = imread(imgpath) 

    key = None # Key for a cluster
    index = None # Index of face in 'q_features'
    
    # if there is not any cluster, create first one
    if len(curr_features) == 0:
      #get key for new cluster
      key   = clusterer.get_next_key()
      index = 0
      print('Creating cluster {}...'.format(key))
      clusterer.store_clutered_image(key, index, True)
      curr_features.append(q_features)
    else:
      #perform searching
      #Use Searcher class to search for matched images
      s               = Searcher()
      matched_indices = s.search(curr_features, q_features, limit=5)
      
      # if returned with -1 --> No Match found, create new cluster
      if matched_indices == -1:
        #get key for new cluster
        key = clusterer.get_next_key()
        index = len(curr_features)# current len is next index.
        print('Creating cluster {}...'.format(key))
        clusterer.store_clutered_image(key, index, True)
        curr_features.append(q_features)
      else:
        # key for matching cluster
        key = clusterer.get_key(matched_indices)
        index = len(curr_features)# current len is next index.
        clusterer.store_clutered_image(key, index)
        curr_features.append(q_features)
    
    # save clusterd face
    clusterer.save_face(index, key, img)
    
    
if __name__ == '__main__':
  main(sys.argv[1])