# USAGE
# python search.py --index index.csv --query queries/103100.png --result-path dataset

# import the necessary packages
import cv2

import face_recognition
import sys
import multiprocessing
import time
def main(args):
  path = '/home/wizdojotech/detect_faces/input/'+args[0]
  
  print('Processing Started:')
  img = cv2.imread(path)
  locs = face_recognition.batch_face_locations([img])
  print('Processing Ended:')
  
  
if __name__ == '__main__':
  main(sys.argv[1:])
      



def print_fn(num, id, val):
  time.sleep(5)
  val = num
  print('fn: ', val)
  
  
def print_sq(num, id):
  time.sleep(2)
  print('sq: ', num**2)
  
for i in range(0, 10):
  if i % 5 == 0:
    v = None
    process = multiprocessing.Process(target=print_fn, args=(i, 1, v))
    process.start()
  else:
    time.sleep(1)
    print(i)