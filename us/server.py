import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'server.log'))
    ]
)

logging.info("Starting server.py directly")

# Add the current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import from main module
    from main import app
    logging.info("Imported app from main module")
except ImportError as e:
    logging.error(f"Error importing from main: {e}")
    
    # Create a simple Flask app as fallback
    from flask import Flask, render_template, send_from_directory
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "URL Shortener - Simple Server"
    
    logging.info("Created fallback Flask app")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    logging.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port) 