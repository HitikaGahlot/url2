import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('application.log')
    ]
)

# Log diagnostic information 
logging.info("Starting application.py")
logging.info(f"Python version: {sys.version}")
logging.info(f"Current directory: {os.getcwd()}")
logging.info(f"Files in current directory: os.listdir() result: {os.listdir('.')}")

try:
    # First try to import from main module
    logging.info("Attempting to import from main.py")
    from main import app
    logging.info("Successfully imported app from main.py")
except ImportError as e:
    logging.error(f"Error importing from main: {e}")
    
    try:
        # If main.py import fails, create a simple app
        logging.info("Creating a fallback Flask application")
        from flask import Flask, render_template
        app = Flask(__name__)
        
        @app.route('/')
        def index():
            return "URL Shortener is starting up. The main application couldn't be loaded."
    except Exception as flask_error:
        logging.error(f"Error creating fallback Flask app: {flask_error}")
        raise

# Define application variable for WSGI compatability
application = app

if __name__ == "__main__":
    # Use PORT environment variable or default to 8000
    port = int(os.environ.get('PORT', 8000))
    logging.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port) 