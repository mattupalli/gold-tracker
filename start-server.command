#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Gold Price Tracker..."
echo "Open http://localhost:8888 in your browser"
echo "Press Ctrl+C to stop"
python3 -m http.server 8888
