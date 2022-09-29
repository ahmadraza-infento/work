
import cv2
import base64
import numpy as np
from anemia_detector import AnemiaDetector
from flask import Flask, request, abort, jsonify

detector            = AnemiaDetector()
app                 = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/detect', methods=['POST'])
def detect_anemia():
    if not request.json or 'image' not in request.json: 
        abort(400)

    print       (request.json['model_type'])
    im_b64      = request.json['image']
    img_bytes   = base64.b64decode(im_b64.encode('utf-8'))
    jpg_as_np   = np.frombuffer(img_bytes, dtype=np.uint8)
    img         = cv2.imdecode(jpg_as_np, flags=1)
    resp        = detector.detect(img)
    return resp

def run_server_api():
    app.run(host='0.0.0.0', port=8080)
  
  
if __name__ == "__main__":     
    run_server_api()