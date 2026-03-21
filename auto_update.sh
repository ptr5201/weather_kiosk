#!/bin/bash
cd ~/projects/weather_kiosk

# Fetch the latest from the repo
git fetch origin master

# Check if the local branch is behind the remote
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u})

if [ $LOCAL != $REMOTE ]; then
    echo "Update found! Pulling changes..."
    git pull origin master
    
    # Use your aliases (ensure they are accessible or use the full commands)
    # If aliases don't work in scripts, use the systemd/process commands:
    kiosk-stop
    kiosk-start
    echo "Kiosk restarted with new version."
else
    echo "No updates found."
fi
