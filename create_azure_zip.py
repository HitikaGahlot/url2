#!/usr/bin/env python3
"""
Azure Deployment Zip Creator

This script creates a proper Azure deployment zip with wsgi.py at the root level.
"""

import os
import sys
import zipfile
import tempfile
import shutil
import argparse

def create_wsgi_file(path):
    """Create a robust wsgi.py file at the specified path"""
    wsgi_content = """import os
import logging
import sys

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

try:
    # Try to import app from app.py
    from app import app
    logging.info("Successfully imported app from app.py")
except ImportError as e:
    logging.error(f"Error importing from app: {e}")
    
    # Try to look for app.py in subdirectories
    for subdir in [d for d in os.listdir('.') if os.path.isdir(d)]:
        sys.path.insert(0, os.path.abspath(subdir))
        try:
            from app import app
            logging.info(f"Found app in subdirectory: {subdir}")
            break
        except ImportError:
            sys.path.pop(0)
            continue
    else:
        # If we still can't find it, create a simple fallback app
        try:
            from flask import Flask
            app = Flask(__name__)
            
            @app.route('/')
            def index():
                return "URL Shortener - wsgi.py fallback route"
            
            logging.info("Created fallback Flask app in wsgi.py")
        except Exception as flask_error:
            logging.error(f"Error creating fallback Flask app: {flask_error}")
            raise

# Main application variable for WSGI compatibility
application = app

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    logging.info(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port)
"""
    with open(path, 'w') as f:
        f.write(wsgi_content)
    return path

def create_app_py_file(path):
    """Create a simple app.py file at the specified path"""
    app_content = """from flask import Flask, redirect, render_template
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# For WSGI compatibility
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
"""
    with open(path, 'w') as f:
        f.write(app_content)
    return path

def create_azure_zip(source_dir, output_zip=None):
    """
    Create a proper Azure deployment zip with wsgi.py at the root
    
    Args:
        source_dir: Source directory containing application files
        output_zip: Output zip file path (if None, will use source_dir name + .zip)
    
    Returns:
        Path to the created zip file
    """
    if not os.path.isdir(source_dir):
        raise ValueError(f"Source directory {source_dir} does not exist")
    
    # Create temporary directory for zip creation
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create wsgi.py file in temp directory
        wsgi_path = create_wsgi_file(os.path.join(temp_dir, "wsgi.py"))
        
        # Check if app.py exists in source_dir
        if not os.path.exists(os.path.join(source_dir, "app.py")):
            # Create app.py in temp directory
            app_path = create_app_py_file(os.path.join(temp_dir, "app.py"))
        else:
            app_path = None
        
        # Determine output zip path
        if output_zip is None:
            output_zip = os.path.join(os.path.dirname(source_dir), 
                                     os.path.basename(source_dir) + ".zip")
        
        # Create the zip file
        with zipfile.ZipFile(output_zip, 'w') as zipf:
            # Add wsgi.py to the root of the zip
            zipf.write(wsgi_path, "wsgi.py")
            
            # Add app.py to the root if created
            if app_path:
                zipf.write(app_path, "app.py")
            
            # Add all files from source_dir
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Add files with correct relative paths
                    rel_path = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, rel_path)
        
        print(f"Created Azure deployment zip: {output_zip}")
        return output_zip
    
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

def main():
    """Main function to run from command line"""
    parser = argparse.ArgumentParser(description="Create an Azure deployment zip with wsgi.py at the root")
    parser.add_argument("source_dir", help="Source directory containing application files")
    parser.add_argument("-o", "--output", help="Output zip file path")
    
    args = parser.parse_args()
    
    try:
        zip_path = create_azure_zip(args.source_dir, args.output)
        print(f"Successfully created Azure deployment zip: {zip_path}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 