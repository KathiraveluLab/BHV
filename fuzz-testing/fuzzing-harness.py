import random
import requests

def fuzzer(max_length=100, start=33, end=126) -> str :

    string_length=random.randrange(1,max_length+1)
    output="" 
    for i in range(0,string_length):
        output+=chr(random.randrange(start,end+1))
    return output
    
def test_inputs():
    for i in range(0,100):
        name=fuzzer()
        narrative=fuzzer()
        URL1= "http://127.0.0.1:5000/upload"
        inputs={"patient_name": name ,"narrative": narrative }
        fake_imag={
            'patient_image': ('test.jpg', b'fake-image-content', 'image/jpeg')
        }
        try:
            r = requests.post(URL1, data=inputs,files=fake_imag)
            if r.status_code == 500:
                print(f"Internal Server Error, inputs: Name:{name} || Narrative:{narrative}")
            else:
                print(f"server responded with : {r.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Server is down or a network error occurred: {e}")

test_inputs()
