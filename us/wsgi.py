import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('wsgi.log')
    ]
)

# Log the environment for debugging
logging.info("Starting wsgi.py")
logging.info(f"Python version: {sys.version}")
logging.info(f"Current directory: {os.getcwd()}")
logging.info(f"Directory contents: {os.listdir('.')}")

try:
    # Try direct import from application.py
    logging.info("Attempting to import from application.py")
    from application import app as application
    logging.info("Successfully imported app from application.py")
except ImportError as e:
    logging.error(f"Error importing from application.py: {e}")
    
    try:
        # Try import from main.py
        logging.info("Attempting to import from main.py")
        from main import app as application
        logging.info("Successfully imported app from main.py")
    except ImportError as main_error:
        logging.error(f"Error importing from main.py: {main_error}")
        
        # Create a fallback application
        from flask import Flask
        application = Flask(__name__)
        
        @application.route('/')
        def index():
            return "URL Shortener - WSGI Fallback Application"
        
        logging.info("Created fallback application in wsgi.py")

# Make sure app is defined for compatibility
app = application

if __name__ == "__main__":
    # Use PORT environment variable for Azure or default to 8000
    port = int(os.environ.get('PORT', 8000))
    logging.info(f"Starting application on port {port}")
    application.run(host='0.0.0.0', port=port) 