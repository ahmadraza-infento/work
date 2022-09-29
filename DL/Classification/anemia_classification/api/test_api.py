import requests
import base64
import json    


api_url     = "http://localhost:8080/detect"

model_type  = input("please enter model type (palpebral/forniceal/forniceal_palp/org) >>>") 
image_file = f'test_imgs/test_{model_type}.png'

with open(image_file, "rb") as f:
    im_bytes = f.read()        
im_b64 = base64.b64encode(im_bytes).decode("utf8")

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
payload = json.dumps({"image": im_b64, "model_type": model_type})


response = requests.post(api_url, data=payload, headers=headers)
try:
    data = response.json()     
    print(data)                
except requests.exceptions.RequestException:
    print(response.text)
