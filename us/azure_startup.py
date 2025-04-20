import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'azure_startup.log'))
    ]
)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
logging.info(f"Python path: {sys.path}")
logging.info(f"Current directory: {os.getcwd()}")
logging.info(f"Files in current directory: {os.listdir(os.getcwd())}")

# Create a basic Flask app first as a fallback
from flask import Flask, render_template, send_from_directory, redirect, abort

# Create a basic app that works even if main app fails
app = Flask(__name__)

@app.route('/')
def root():
    return redirect('/index')
    
@app.route('/index')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error rendering index template: {e}")
        return f"URL Shortener is starting up. If you continue to see this message, check the logs for errors."
    
@app.route('/static/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('static', path)
    except Exception as e:
        logging.error(f"Error serving static file {path}: {e}")
        abort(404)

# Try to import the actual application
try:
    logging.info("Starting URL Shortener application on Azure")
    from main import app as main_app
    
    # Replace our app with the main app
    app = main_app
    logging.info("Successfully imported main application")
    
    # Log the registered routes
    logging.info("Registered routes:")
    for rule in app.url_map.iter_rules():
        logging.info(f"{rule.endpoint}: {rule.rule}")
except Exception as e:
    logging.error(f"Error importing main application: {e}")
    logging.error("Continuing with basic Flask app")
    import traceback
    traceback.print_exc()

# Create application variable for WSGI
application = app
wsgi_app = app.wsgi_app

if __name__ == "__main__":
    # Running directly, not through WSGI
    port = int(os.environ.get('PORT', 8000))
    logging.info(f"Starting development server on port {port}")
    app.run(host='0.0.0.0', port=port) 