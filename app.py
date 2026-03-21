import requests
import os
from flask import Flask, render_template
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%H:%M'):
    return datetime.fromtimestamp(value).strftime(format)

# --- CONFIGURATION ---
API_KEY = os.getenv("OPENWEATHER_API_KEY")
LAT = "43.14"   # Your Latitude (e.g., Kitchener/Waterloo)
LON = "-77.85"  # Your Longitude
UNITS = "imperial" # Use 'imperial' for Fahrenheit

# Global variable to hold the last successful weather data
last_weather_cache = None

def get_weather():
    global last_weather_cache

    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}"

    try:
        # 1. Try to fetch fresh data
        response = requests.get(url, timeout=10) # Added timeout so it doesn't hang
        response.raise_for_status()
        data = response.json()

        #2. Success! Update the RAM cache
        last_weather_cache = data
        return data
    except Exception as e:
        print(f"Fetch failed: {e}")
        # 3. If it fails, check if we have a RAM backup
        if last_weather_cache:
            print("Using RAM cache...")
            return last_weather_cache
        else:
            # Only shows error if we've NEVER had a successful fetch since boot
            return {"error": "Weather unavailable."}

@app.route('/')
def home():
    try:
        # 2. Fetch the data
        data = get_weather()

        # 3. Pass data to the HTML template
        return render_template('index.html', w=data)
    except Exception as e:
        return f"Error fetching weather: {e}"

@app.route('/api/weather')
def weather_api():
    return get_weather()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
