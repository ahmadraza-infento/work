import cv2				# Import OpenCV for image processing
import sys				# Import for time
import os				# Import for reading files
import threading		# Import for separate thread for image classification
import numpy as np 		# Import for converting vectors

import tensorflow as tf # Import tensorflow for Inception Net's backend

language = 'en'

class Rectangle:
    start   = (70, 70) 
    end     = (350, 350)
    color   = (0,255,0)
    size    = 2

class AIModel():
    def __init__(self) -> None:
        self.label_lines = [line.rstrip() for line in tf.gfile.GFile("assets/training_set_labels.txt")]

        # Load trained model's graph
        with tf.gfile.FastGFile("assets/trained_model_graph.pb", 'rb') as f:
            # Define a tensorflow graph
            self.graph_def = tf.GraphDef()

            # Read and import line by line from the trained model's graph
            self.graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(self.graph_def, name='')

    def predict_letter(self, img):
        with tf.Session() as sess:
            # Feed the image_data as input to the graph and get first prediction
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

            # Global variable to keep track of time
            time_counter = 0

            # Flag to check if 'c' is pressed
            captureFlag = False

            # Toggle real time processing
            realTime = True

            # Toggle spell checking
            spell_check = False

            # Focus on Region of Interest (Image within the bounding box)
            resized_image = img[Rectangle.start[0]:Rectangle.end[0], Rectangle.start[1]:Rectangle.end[1]]
            
            # Resize to 200 x 200
            resized_image = cv2.resize(resized_image, (200, 200))
            
            image_data = cv2.imencode('.jpg', resized_image)[1].tostring()

            predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})

            # Sort to show labels of first prediction in order of confidence
            top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

            max_score = 0.0
            letter = ''
            for node_id in top_k:
                # Just to get rid of the Z error for demo
                if self.label_lines[node_id].upper() == 'Z':
                    human_string = self.label_lines[node_id+1]
                else:
                    human_string = self.label_lines[node_id]
                score = predictions[0][node_id]
                if score > max_score:	
                    max_score = score
                    letter = human_string
            self._result = (letter, max_score )
        return letter, max_score

    def pred_result(self):
        """ To be used in case you have called predict_threaded.
            @return: prediction result 
        """
        return (None, None) if self._result is None else self._result


    def predict_threaded(self, frame):
        """ predict results in as separate thread """
        self._result = None
        self._th = threading.Thread(target=self.predict_letter, args=(frame,))
        self._th.setDaemon(True)
        self._th.start()


        
class Camera():

    def __init__(self):
        self._Max_Size      = 5
        self._frame_queue   = []
        self._stop          = False

    @property
    def counter(self):
        self._counter += 1
        return self._counter

    def read(self):
        """ read camera frame and return"""
        return self._frame_queue.pop(0) if len(self._frame_queue) > 0 else None



    def read_frame(self):
        """ save next frame and return its path and frame """
        frame = self.read()
        if frame is not None:
            try     : os.remove(f"tmp/image_{self._counter}.jpg")
            except  : pass

            frame_path = f"tmp/image_{self.counter}.jpg"
            cv2.imwrite(frame_path, frame)
            return frame_path, frame
        
        else:
            return "", None

    def _push(self, frame):
        if len(self._frame_queue) >= self._Max_Size:
            _ = self._frame_queue.pop(0)
        self._frame_queue.append(frame)

    def _worker(self):
        live_stream = cv2.VideoCapture(0)
        while self._stop is False:
            img = live_stream.read()[1]
            # Set a region of interest
            cv2.rectangle(img, Rectangle.start, Rectangle.end, Rectangle.color, Rectangle.size)
            self._push(img)
        live_stream.release()
    
    def start(self):
        self._stop = False
        self._counter = 0
        self._th = threading.Thread(target=self._worker)
        self._th.setDaemon(True)
        self._th.start()

    def stop(self):
        self._stop = True
        self._frame_queue.clear()
        try     : del self._th
        except  : pass


        

if __name__ == "__main__":

    model   = AIModel()
    img     = cv2.imread("W_test.jpg")
    letter, score = model.predict_letter(img)
    print("letter is: ", letter, " and score is: ", score)
    letter, score = model.predict_letter(img)
    print("letter is: ", letter, " and score is: ", score)
    