#!/bin/bash
# Azure App Service startup script for FastAPI
 
echo "Starting FastAPI app on port 8000..."
 
# Activate virtual environment if it exists (Oryx creates 'antenv')
if [ -d "/home/site/wwwroot/antenv" ]; then
    echo "Activating virtual environment..."
    source /home/site/wwwroot/antenv/bin/activate
    pip install -r requirements.txt
fi
 
# Start uvicorn with the app
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000