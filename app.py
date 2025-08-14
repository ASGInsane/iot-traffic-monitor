from flask import Flask, render_template, jsonify
import requests
import os
import time

app = Flask(__name__)

# Load Google API Key (You can also set it as an env variable)
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"

# Store latest data
latest_data = {
    "location": "Mumbai to Navi Mumbai",
    "vehicle_count": "N/A",  # Google doesn't give count, we can estimate later
    "average_speed": 0,
    "congestion": "Low"
}

def fetch_google_traffic():
    origin = "Mumbai"
    destination = "Navi Mumbai"
    url = (
        "https://maps.googleapis.com/maps/api/distancematrix/json"
        f"?origins={origin}&destinations={destination}"
        f"&departure_time=now&traffic_model=best_guess&key={GOOGLE_API_KEY}"
    )

    try:
        response = requests.get(url)
        data = response.json()

        if "rows" in data and data["rows"][0]["elements"][0]["status"] == "OK":
            element = data["rows"][0]["elements"][0]
            normal_time = element["duration"]["value"]  # in seconds
            traffic_time = element["duration_in_traffic"]["value"]  # in seconds

            # Estimate speed in km/h (assuming route distance in meters)
            distance_m = element["distance"]["value"]
            speed_kmh = (distance_m / 1000) / (traffic_time / 3600)

            latest_data["average_speed"] = round(speed_kmh, 2)

            # Simple congestion logic based on delay percentage
            delay_ratio = (traffic_time - normal_time) / normal_time
            if delay_ratio > 0.5:
                latest_data["congestion"] = "High"
            elif delay_ratio > 0.2:
                latest_data["congestion"] = "Medium"
            else:
                latest_data["congestion"] = "Low"
        else:
            latest_data["congestion"] = "Error fetching data"
    except Exception as e:
        latest_data["congestion"] = "API Error"
        print(e)

# Background loop to refresh data every 1 minute
def background_update():
    while True:
        fetch_google_traffic()
        time.sleep(60)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_latest_data")
def get_latest_data():
    return jsonify(latest_data)

if __name__ == "__main__":
    import threading
    threading.Thread(target=background_update, daemon=True).start()
    app.run(debug=True)

