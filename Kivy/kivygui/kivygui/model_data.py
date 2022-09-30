import numpy as np
from threading import Thread
from kivy.clock import Clock
from functools import partial
import tensorflow as tf
import random
from kivy.utils import platform
import pickle

class DataReader():
    _labels_to_be_used = ('Sitting', "Running", 'Walking')
    
    @classmethod
    def init(cls):
        if platform == 'android':
            # set-up plyer to read sensor data
            from plyer import notification, vibrator, tts, email, accelerometer
            try:
                accelerometer.enable()
            except Exception as e:
                print(e)

        else:
            # set-up test data from file
            f           = open("test_data.pickle", "rb")
            cls._data   = pickle.load(f)
            f.close     ()
              
    @classmethod
    def model_input(cls, num_samples):
        if platform == 'android':
            # read sensor data and build model input
            try:
                inp = []
                for i in range(num_samples):
                    s = [accelerometer.acceleration[0], accelerometer.acceleration[1], accelerometer.acceleration[2]]
                    s = [float(item) for item in s]
                    inp.append(np.array(s, dtype=np.float32) )
                return np.array([inp], dtype=np.float32)
            except Exception as e:
                print(e)
                return np.array([np.random.random_sample( (num_samples, 3) )], dtype=np.float32)
        
        else:
            # build model input from test data
            try:
                inp= []
                key = cls._labels_to_be_used[random.randint(0, 1)]
                return cls._data[key]
            except Exception as e:
                print(e)
                return np.array([np.random.random_sample( (num_samples, 3) )], dtype=np.float32)
    
    @classmethod
    def sensor_input(cls):
        if platform == 'android':
            # read sensor input and return
            try:
                s = [accelerometer.acceleration[0], accelerometer.acceleration[1], accelerometer.acceleration[2]]
                return [float(i) for i in s]
            except Exception as e:
                print(e)
                return np.random.random_sample( (1, 3) )[0]
        else:
            # read a random sample from test data
            try:
                return np.random.random_sample( (1, 3) )[0]
            except Exception as e:
                print(e)
                return np.random.random_sample( (1, 3) )[0]

class AIModel():
    def __init__(self) -> None:
        self._load_model()
        self._labels = { 0:'Sitting', 1:'Walking', 2:'Running' }

    def _load_model(self):
        """ load pretrained model from file """
        try:
            self._model             = tf.lite.Interpreter(model_path="tflitemodel")
            self._model.allocate_tensors()
            self._input_details     = self._model.get_input_details()
            self._output_details    = self._model.get_output_details()
        
        except Exception as e:
            print(f"[EXCEPTION] {e}")
            self._model = None

    def predict(self, data):
        """ predict current state using given data by pre-trained model 
            >>> @param:data -> data to be passed to model
            >>> @return     -> predicted class or None [if there is any issue]
        """
        try:
            if self._model is not None:
                self._model.set_tensor  (self._input_details[0]['index'], data)
                self._model.invoke      ()
                lbls    = self._model.get_tensor(self._output_details[0]['index'])[0]
                cls_idx = np.argmax(np.array([lbls]))
                return self._labels[cls_idx]
            else:
                print("[ERROR] model is not available")
        
        except Exception as e:
            print(f"[EXCEPTION] {e}")

    def predict_threaded(self, data, callback):
        """ predict current state using given data by pre-trained model in threaded job
            >>> @param:data     -> data to be passed to model
            >>> @param:callback -> function to be called on job finish
            >>> @return         -> init a call to callback funct with model result """
        def job(job_data, clbk):
            result      = self.predict(job_data)
            Clock.schedule_once(partial(clbk, result), 0.5)
        
        self._th = Thread(target=job, args=(data, callback))
        self._th.setDaemon(True)
        self._th.start()



    

if __name__ == "__main__":
    DataReader.init()
    print(DataReader.model_input(200).shape)
    model   = AIModel()
    print("result is -> ", model.predict( DataReader.model_input(200) ) ) 
    
    