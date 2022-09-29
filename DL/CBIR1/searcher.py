# import the necessary packages
import numpy as np
import csv
from itertools import compress
import math
import face_recognition

class Searcher:
  
  def search_fc(self, features, queryFeatures, limit = 10):
    distances = face_recognition.face_distance(features, queryFeatures)
    indices = list(np.where(distances < 0.45)[0])
    distances = list(distances)
    
    if len(indices)== 0:
      return -1
    if len(distances) > 1:
      # sort indices and distances to get top matchings
      distances, indices = zip(*sorted(zip(distances, indices))) 
      if len(distances) > limit:
        return indices[:limit]
      return indices
    else:
      return indices
    
  def search(self, features, queryFeatures, limit = 10):
	
	#compute distance of matched images
    distances, indices = zip(*[(self.euclidean_distance(queryFeatures, f), i) 
    		                      for i, f in enumerate(features)])
    ds = []
    ind = []
    for d, i in zip(distances, indices):
      if d < 0.40: #0.45
        ds.append(d)
        ind.append(i)
    distances = ds
    indices = ind
    if len(distances) == 0:
      return -1
    if len(distances) > 1:
      # sort indices and distances to get top matchings
      distances, indices = zip(*sorted(zip(distances, indices))) 
      if len(distances) > limit:
        return indices[:limit]
      return indices
    else:
      return indices
	
  def euclidean_distance(self, x, y):
    distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(x, y)]))
    return distance