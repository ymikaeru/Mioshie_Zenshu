#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Ensinamentos Viewer..."
echo "Opening browser..."
open "http://localhost:8080/index.html"
echo "Starting server at http://localhost:8080 (Press Ctrl+C to stop)"
python3 -m http.server 8080
