import os
import logging
import sys
from threading import Thread
from flask import Flask

# Configure logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('wsgi.log')]
)

logging.info("Starting wsgi.py")
logging.info(f"Python version: {sys.version}")
logging.info(f"Current directory: {os.getcwd()}")
try:
    logging.info(f"Directory contents: {os.listdir('.')}")
except Exception as e:
    logging.error(f"Error listing directory: {e}")

# Create a minimal Flask app that responds immediately
temp_app = Flask(__name__)

@temp_app.route('/health')
def health():
    return "OK", 200

@temp_app.route('/')
def index():
    return "URL Shortener - Starting up...", 200

# Global variable to store the main app
main_app = None

def load_main_app():
    global main_app
    try:
        # Try to import app from app.py
        from app import app as imported_app
        main_app = imported_app
        logging.info("Successfully imported main app from app.py")
    except ImportError as e:
        logging.error(f"Error importing main app: {e}")
        # If import fails, use the temporary app
        main_app = temp_app

# Start loading the main app in a background thread
Thread(target=load_main_app, daemon=True).start()

# Use the temporary app initially
app = temp_app

# Create the WSGI application variable
application = app

# Allow the app to be run directly
if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    logging.info(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port) 