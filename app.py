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
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
LAT = "43.14"   # Your Latitude (e.g., Kitchener/Waterloo)
LON = "-77.85"  # Your Longitude
UNITS = "imperial" # Use 'imperial' for Fahrenheit

# Global variables to hold the last successful weather data
last_weather_cache = None

def fetch_pollen_data():
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LAT}&longitude={LON}&current=alder_pollen,birch_pollen,grass_pollen,mugwort_pollen,olive_pollen,ragweed_pollen&timezone=auto"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json().get('current', {})
        
        # Using .get(key, 0) isn't enough because the key might exist but be None.
        # This list comprehension ensures every value is at least 0.
        pollen_fields = [
            'alder_pollen', 'birch_pollen', 'grass_pollen', 
            'mugwort_pollen', 'olive_pollen', 'ragweed_pollen'
        ]

        pollen_values = [data.get(field) if data.get(field) is not None else 0 for field in pollen_fields]

        max_pollen = max(pollen_values)
        return format_pollen_risk(max_pollen)
    except Exception as e:
        print(f"Pollen Error: {e}")
        return "N/A"

def format_pollen_risk(value):
    # Rough grains/m^3 scale for a "General" label
    if value < 10: return "Low"
    if value < 50: return "Med"
    if value < 150: return "High"
    return "Very High"

def get_weather():
    global last_weather_cache

    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&appid={OPENWEATHER_API_KEY}&units={UNITS}"

    try:
        # 1. Try to fetch fresh data
        response = requests.get(url, timeout=10) # Added timeout so it doesn't hang
        response.raise_for_status()
        weather_data = response.json()

        pollen = fetch_pollen_data()
        
        if pollen:
            weather_data['pollen'] = pollen

        #2. Success! Update the RAM cache
        last_weather_cache = weather_data
        return weather_data
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
        
        pollen_data = data['pollen']

        # 3. Pass data to the HTML template
        return render_template('index.html', w=data, pollen=pollen_data)
    except Exception as e:
        return f"Error fetching weather: {e}"

@app.route('/api/weather')
def weather_api():
    return get_weather()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
