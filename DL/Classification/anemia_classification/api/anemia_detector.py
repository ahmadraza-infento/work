import cv2
import numpy as np
from tensorflow.keras.models import load_model


class AnemiaDetector():
    def __init__(self) -> None:
        self._detectors = {}
        self._load_models()
        self._labels = {0:"No Anemia", 1:"Anemia"}

    def _load_models(self):
        """ load pretrained model"""
        try:
            for key, mpath in { "palpebral"     : "model_palpebral_93_18",
                                "forniceal"     : "model_forniceal_90_69",
                                "forniceal_palp": "model_forniceal_palp_86_04_35",
                                "org"           : "model_org_84_09"}.items():
                self._detectors[key] = load_model(f"models/{mpath}.hd5")
        
        except Exception as e:
            print(f"[EXCEPTION] ", e)
            self._detector = None

    def _preprocess(self, image):
        img           = cv2.resize(image, (64, 64))
        img           = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kernel        = np.array([[-1,-1,-1], 
                                    [-1, 9,-1],
                                    [-1,-1,-1]])
        sharpened     = cv2.filter2D(img, -1, kernel)
        img           = cv2.GaussianBlur(sharpened, (5, 5), 0)
        img           = img.reshape(64, 64, 1)
        return img

    def detect(self, image, model_type="palpebral"):
        def result_json(lbl, conf):
            return {"result":lbl, "confidence":f"{conf}"}

        try:
            image   = self._preprocess(image)
            probs   = self._detectors[model_type].predict( np.array([image]) )
            lbl     = np.argmax(probs)
            return result_json(self._labels[lbl], "{:.2f}".format(probs[0][lbl]) ) 
        
        except Exception as e:
            print("[EXCEPTION] ", e)
            return result_json(None, None)

if __name__ == "__main__":
    detector= AnemiaDetector()
    img     = cv2.imread("test.png")
    print   ( detector.detect(img) )
