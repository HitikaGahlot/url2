#!%HOME%\\Python39\\python.exe

import os
import sys
import logging

# Enable detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'handler.log'))
    ]
)

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))
logging.info(f"Python path: {sys.path}")
logging.info(f"Current directory: {os.path.dirname(__file__)}")
logging.info(f"Files in current directory: {os.listdir(os.path.dirname(__file__))}")

logging.info("Starting handler.fcgi")

# Import the WSGI application
try:
    logging.info("Trying to import from azure_startup")
    from azure_startup import app as application
    logging.info("Successfully imported azure_startup")
except ImportError as e:
    logging.error(f"Error importing azure_startup: {e}")
    try:
        logging.info("Trying to import from main")
        from main import app as application
        logging.info("Successfully imported main")
    except ImportError as e:
        logging.error(f"Error importing main: {e}")
        
        # Create a minimal Flask app that shows the error
        from flask import Flask, render_template_string
        application = Flask(__name__)
        
        @application.route('/')
        def index():
            error_html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>URL Shortener - Error</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    .error { background-color: #ffebee; border-left: 4px solid #f44336; padding: 15px; }
                    pre { background-color: #f5f5f5; padding: 10px; overflow: auto; }
                </style>
            </head>
            <body>
                <h1>URL Shortener - Application Error</h1>
                <div class="error">
                    <h2>Error Details:</h2>
                    <p>%s</p>
                </div>
                <h3>Debug Information:</h3>
                <pre>Python Path: %s</pre>
                <pre>Current Directory: %s</pre>
                <pre>Directory Contents: %s</pre>
            </body>
            </html>
            ''' % (
                str(e),
                str(sys.path),
                os.path.dirname(__file__),
                str(os.listdir(os.path.dirname(__file__)))
            )
            return render_template_string(error_html)

# Log the loaded application details
logging.info(f"Application loaded successfully. Routes: {list(application.url_map.iter_rules())}")

# Make various aliases for different hosting platforms
wsgi_app = application.wsgi_app
app = application

if __name__ == '__main__':
    application.run() 