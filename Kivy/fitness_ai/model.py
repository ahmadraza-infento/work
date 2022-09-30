import numpy as np
from threading import Thread
from kivy.clock import Clock
from functools import partial
import tensorflow as tf

class AIModel():
    def __init__(self) -> None:
        self._load_model()
        self._labels = { 0:'Downstairs', 1:'Jogging', 2:'Sitting', 
                            3:'Standing', 4:'Upstairs', 5:'Walking'}

    def _load_model(self):
        """ load pretrained model from file """
        try:
            self._model             = tf.lite.Interpreter(model_path="final_human_activity.tflite")
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


    def test_predict_th(self, callback):
        """ just to test the working of model with dummy data 
            >>> @param:callback -> function to be called on job finish
        """
        input_shape = self._input_details[0]['shape'] 
        test_data   = np.array(np.random.random_sample(input_shape), dtype=np.float32)
        self.predict_threaded(test_data, callback)

    def test_predict(self):
        """ just to test the working of model with dummy data """
        input_shape = self._input_details[0]['shape'] 
        test_data   = np.array(np.random.random_sample(input_shape), dtype=np.float32)
        return self.predict(test_data)


    

if __name__ == "__main__":

    model   = AIModel()
    print("result is -> ", model.test_predict() )
    