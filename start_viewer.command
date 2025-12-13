#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Ensinamentos Viewer (New Version)..."
echo "The original site is also available at index.html"
echo "Opening viewer in browser..."
open "http://localhost:8080/viewer.html"
echo "Starting server at http://localhost:8080 (Press Ctrl+C to stop)"
python3 -m http.server 8080
