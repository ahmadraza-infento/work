import cv2
import pickle
import random
import numpy as np
from kivy.clock import Clock
from functools import partial
from tensorflow.keras.models import load_model


class MovementDetector():
    def __init__(self):
        try     : self.__detector=load_model(f"movementanalysisModel.h5")
        except  : print("failed to load detector"); self.__detector=None
        self.__labels       = { 0:'Sitting', 1:'Walking', 2:'Jogging' }
        self.__num_samples  = 200
        self._load_data     ()

    def _load_data(self):
        try:
            with open("test_data.pickle", "rb") as f:
                self._test_data = pickle.load(f)
        except Exception as e:
            print(e)

    @property
    def read_input(self):
        try:
            data= []
            key = self.__labels[random.randint(0, 2)]
            for i in range(self.__num_samples):
                s = self._test_data[key][ random.randint(0, len( self._test_data[key] )-1) ][3:]
                s = [float(item) for item in s]
                data.append(np.array(s) )
            return np.array(data)
        except Exception as e:
            print(e)
            return np.array(np.random.random_sample( (self.__num_samples, 3) ), dtype=np.float32)
    
    @property
    def single_input(self):
        try:
            key = self.__labels[random.randint(0, 2)]
            s   = self._test_data[key][random.randint(0, len(self._test_data[key])-1)][3:]
            return [float(i) for i in s]
        except Exception as e:
            print(e)
            return np.random.random_sample( (1, 3) )[0]

    def detect(self, data, callback):
        def _detect_job():
            result = None
            if self.__detector is not None:
                try :
                    res     = self.__detector.predict( np.array( [data]) )[0]
                    max_idx = np.argmax(res)
                    result  = self.__labels[max_idx]
                except Exception as e:
                    print(e)
            Clock.schedule_once( partial(callback, result), 0.05)
                    
        _detect_job()


if __name__ == "__main__":
    def func(result, dt):
        print("result is -> ", result)

    detector= MovementDetector()
    detector.detect( detector.read_input, func )
    _       = input("press enter to exit")
