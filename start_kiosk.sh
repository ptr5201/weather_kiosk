#!/bin/bash

# 1. Move to the project directory
cd /home/ptr5201/projects/weather_kiosk

# 2. Run the app using the direct path to the VENV python
# The '&' puts it in the background so the script can continue
./venv/bin/python3 app.py &

# 3. Wait for the server to bind to the port
echo "Waiting for Flask to start..."
until $(curl -s -f http://localhost:5000 > /dev/null); do
	echo "Waiting for Flask..."
	sleep 2
done
echo "Flask is up!"

# 4. Launch Chromium in kiosk mode
chromium --kiosk --incognito --noerrdialogs --disable-infobars --password-store=basic http://localhost:5000
