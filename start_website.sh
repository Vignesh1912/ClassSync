#!/bin/bash

echo "Starting ClassSync App..."

# Check if Linux venv exists, if not create it
if [ ! -f "venv/bin/activate" ]; then
    echo "First time running on Linux! Setting up environment..."
    # If a Windows venv was copied, remove it
    rm -rf venv
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start the Flask app in the background
python run.py &
FLASK_PID=$!

# Give Flask a second to start
sleep 2

echo "Starting Tunnel..."
# Start LocalTunnel for public access
npx localtunnel --port 5000 --subdomain classsync-vigne &
TUNNEL_PID=$!

echo ""
echo "========================================================"
echo "Your persistent public website link is:"
echo "https://classsync-vigne.loca.lt"
echo "========================================================"
echo ""
echo "Note: Keep this terminal window open to keep the website online!"
echo "Press Ctrl+C to stop both the application and the public link."

# Wait for both processes so Ctrl+C stops everything cleanly
trap "echo 'Stopping all services...'; kill $FLASK_PID $TUNNEL_PID; exit" EXIT INT TERM
wait
