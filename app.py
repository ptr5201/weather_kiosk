import requests
import os
import time
from flask import Flask, render_template
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%H:%M'):
    return datetime.fromtimestamp(value).strftime(format)

# --- CONFIGURATION ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
LAT = "43.14"   # Your Latitude (e.g., Kitchener/Waterloo)
LON = "-77.85"  # Your Longitude
UNITS = "imperial" # Use 'imperial' for Fahrenheit

# Global variables to hold the last successful weather data
last_weather_cache = None

def fetch_aqi_data():
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LAT}&longitude={LON}&current=us_aqi&timezone=auto"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json().get('current', {})
        aqi = data.get('us_aqi')

        if aqi is None:
            return None

        return round(aqi)
    except Exception as e:
        print(f"AQI Error: {e}")
        return None

def format_aqi(value):
    if value is None:
        return "N/A"
    if value <= 50:
        return f"{value} Good"
    if value <= 100:
        return f"{value} Moderate"
    if value <= 150:
        return f"{value} Unhealthy for Sensitive Groups"
    if value <= 200:
        return f"{value} Unhealthy"
    if value <= 300:
        return f"{value} Very Unhealthy"
    return f"{value} Hazardous"

def get_weather():
    global last_weather_cache

    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&appid={OPENWEATHER_API_KEY}&units={UNITS}"

    try:
        # 1. Try to fetch fresh data
        response = requests.get(url, timeout=10) # Added timeout so it doesn't hang
        response.raise_for_status()
        weather_data = response.json()

        # Remove weather alerts that have already expired
        current_time = int(time.time())
        weather_data['alerts'] = [
                alert for alert in weather_data.get('alerts', []) if alert.get('end', 0) > current_time
                ]

        # AQI is supplemental data. If it fails, the main weather
        # request should still succeed.
        aqi = fetch_aqi_data()
        weather_data['aqi'] = format_aqi(aqi)

        #2. Success! Update the RAM cache
        last_weather_cache = weather_data
        return weather_data
    except Exception as e:
        print(f"Fetch failed: {e}")
        # 3. If it fails, check if we have a RAM backup
        if last_weather_cache:
            print("Using RAM cache...")

            # Remove expired alerts from cached weather data too.
            current_time = int(time.time())
            last_weather_cache['alerts'] = [
                    alert for alert in last_weather_cache.get('alerts', []) if alert.get('end', 0) > current_time
            ]
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
