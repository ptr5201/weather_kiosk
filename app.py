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

@app.route('/')
def home():
    # 1. Construct the URL
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}"
    
    try:
        # 2. Fetch the data
        response = requests.get(url)
        data = response.json()
        
        # 3. Pass data to the HTML template
        return render_template('index.html', w=data)
    except Exception as e:
        return f"Error fetching weather: {e}"

@app.route('/api/weather')
def weather_api():
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}"
    return requests.get(url).json()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
