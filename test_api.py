import requests
import json

payload = {
 "HR": 125,
 "O2Sat": 90,
 "Temp": 39.0,
 "SBP": 85,
 "MAP": 60,
 "Resp": 28,
 "Lactate": 4.0,
 "WBC": 18000,
 "Platelets": 90000,
 "Creatinine": 2.5
}

try:
    response = requests.post("http://localhost:8000/predict", json=payload)
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
