#!/bin/bash
echo "Starting URL Shortener application..."
cd "$(dirname "$0")"

# Install required packages
pip install -r requirements.txt

# Start the application using the most appropriate method
if command -v gunicorn &> /dev/null
then
    echo "Starting with Gunicorn"
    gunicorn --bind=0.0.0.0:8000 azure_startup:app
else
    echo "Starting with Python"
    python azure_startup.py
fi 