from flask import Flask, jsonify, render_template
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Get API key from environment variable (set this in Render)
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_KEY")

# Function to get real-time traffic data from Google Maps API
def get_traffic_data(origin, destination):
    try:
        url = (
            "https://maps.googleapis.com/maps/api/distancematrix/json"
            f"?origins={origin}&destinations={destination}"
            f"&departure_time=now&key={GOOGLE_API_KEY}"
        )
        response = requests.get(url)
        data = response.json()

        if data.get("status") == "OK":
            element = data["rows"][0]["elements"][0]
            if element.get("status") == "OK":
                distance = element["distance"]["text"]
                duration = element["duration"]["text"]
                duration_in_traffic = element.get("duration_in_traffic", {}).get("text", duration)

                return {
                    "location": f"{origin} to {destination}",
                    "distance": distance,
                    "duration": duration,
                    "duration_in_traffic": duration_in_traffic,
                    "congestion": get_congestion_level(duration, duration_in_traffic)
                }
        return {"error": "Unable to fetch data from Google Maps API"}
    except Exception as e:
        return {"error": str(e)}

# Function to determine congestion level based on travel time difference
def get_congestion_level(normal_time, traffic_time):
    try:
        normal_minutes = int(normal_time.split()[0])
        traffic_minutes = int(traffic_time.split()[0])

        if traffic_minutes <= normal_minutes * 1.2:
            return "Low"
        elif traffic_minutes <= normal_minutes * 1.5:
            return "Moderate"
        else:
            return "High"
    except:
        return "Unknown"

# API route for frontend JS
@app.route("/get_latest_data")
def get_latest_data():
    origin = "Mumbai"
    destination = "Navi Mumbai"
    data = get_traffic_data(origin, destination)
    return jsonify(data)

# Optional home page
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
