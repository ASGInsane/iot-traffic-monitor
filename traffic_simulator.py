import time
import random
import requests

SERVER_URL = "http://localhost:5000/data"

while True:
    data = {
        "location": "Highway_1",
        "vehicle_count": random.randint(5, 50),
        "avg_speed": random.randint(5, 80)  # km/h
    }
    requests.post(SERVER_URL, json=data)
    print("Sent:", data)
    time.sleep(2)  # every 2 seconds
