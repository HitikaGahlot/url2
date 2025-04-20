import os
import shutil
import zipfile
import tempfile
import secrets
from PIL import Image
from io import BytesIO
from flask import Flask, render_template, request, send_file, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import re
import sys
import uuid
import requests
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Log startup information
logging.info("Starting app.py")
logging.info(f"Python version: {sys.version}")
logging.info(f"Current directory: {os.getcwd()}")

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key

# Constants
URL_SHORTENER_SRC = os.path.join(os.path.dirname(__file__), 'us')  # Path to the URL shortener source code
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Configure app
app.config['STARTUP_COMPLETE'] = False
app.config['STARTUP_DELAY_TASKS'] = []

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(file, output_format='PNG'):
    """Process uploaded image and convert it to the desired format"""
    try:
        img = Image.open(file)
        img_io = BytesIO()
        img.save(img_io, format=output_format)
        img_io.seek(0)
        return img_io
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def replace_name_in_files(directory, new_name, accent_color=None):
    """Replace 'URL Shortener' with the provided name and update accent color in all text-based files"""
    for root, _, files in os.walk(directory):
        for file in files:
            # Only process text-based files
            if file.endswith(('.html', '.js', '.css', '.py', '.md', '.txt')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Replace various forms of "URL Shortener"
                    content = content.replace('URL Shortener', new_name)
                    content = content.replace('URL shortener', new_name.lower())
                    content = content.replace('Url Shortener', new_name)
                    content = content.replace('url shortener', new_name.lower())
                    
                    # Update accent color if provided
                    if accent_color:
                        # Create color variations for different states and opacities
                        rgb_color = hex_to_rgb(accent_color)
                        darker_accent = adjust_color(accent_color, -50)
                        hover_color = adjust_color(accent_color, -15)
                        light_bg = color_with_opacity(accent_color, 0.12)
                        lighter_bg = color_with_opacity(accent_color, 0.18)
                        
                        # Handle HTML file color replacements for inline styles
                        if file.endswith('.html'):
                            # Handle CSS variables in stats_view.html
                            if "stats_view.html" in file_path or "stats-view.html" in file_path:
                                # Replace primary-color CSS variable
                                content = re.sub(
                                    r'--primary-color:\s*#[0-9a-fA-F]{6}',
                                    f'--primary-color: {accent_color}',
                                    content
                                )
                                # Replace primary-light CSS variable
                                content = re.sub(
                                    r'--primary-light:\s*rgba\([^)]+\)',
                                    f'--primary-light: rgba({rgb_color}, 0.2)',
                                    content
                                )
                                # Replace primary-dark CSS variable
                                content = re.sub(
                                    r'--primary-dark:\s*#[0-9a-fA-F]{6}',
                                    f'--primary-dark: {hover_color}',
                                    content
                                )
                                # Replace secondary-color CSS variable
                                content = re.sub(
                                    r'--secondary-color:\s*#[0-9a-fA-F]{6}',
                                    f'--secondary-color: {adjust_color(accent_color, -30)}',
                                    content
                                )
                                # Replace secondary-light CSS variable
                                content = re.sub(
                                    r'--secondary-light:\s*rgba\([^)]+\)',
                                    f'--secondary-light: rgba({hex_to_rgb(adjust_color(accent_color, -30))}, 0.2)',
                                    content
                                )
                                
                                # Replace chart series colors
                                content = re.sub(
                                    r'chart\.line\(\)\s*\.\s*stroke\(.*?\)',
                                    f'chart.line().stroke("{accent_color}", 2)',
                                    content
                                )
                                
                                # Replace series color assignments
                                content = re.sub(
                                    r'series\.stroke\(.*?\)',
                                    f'series.stroke("{accent_color}", 2)',
                                    content
                                )
                                
                                # Replace any chart color
                                content = re.sub(
                                    r'\.color\(".*?"\)',
                                    f'.color("{accent_color}")',
                                    content
                                )
                                
                                # Replace chart background
                                content = re.sub(
                                    r'chart\.background\(\)\.fill\(".*?"\)',
                                    f'chart.background().fill("{light_bg}")',
                                    content
                                )
                                
                                # Replace plot background
                                content = re.sub(
                                    r'chart\.plot\(\)\.background\(\)\.fill\(".*?"\)',
                                    f'chart.plot().background().fill("{light_bg}")',
                                    content
                                )
                                
                                # Replace anychart theme
                                content = re.sub(
                                    r'anychart\.theme\(anychart\.themes\.[\w]+\)',
                                    f'anychart.theme(anychart.themes.lightBlue)',
                                    content
                                )
                                
                                # Replace palette settings
                                content = re.sub(
                                    r'\.palette\(\[.*?\]\)',
                                    f'.palette(["{accent_color}", "{adjust_color(accent_color, -20)}", "{adjust_color(accent_color, -40)}"])',
                                    content
                                )
                            
                            # Replace inline styles in self-promo divs
                            content = re.sub(
                                r'style="background-color:\s*(?:rgb\([^)]+\)|#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})"',
                                f'style="background-color: {darker_accent}"',
                                content
                            )
                            
                            # Replace any other inline color styles that might be using the blue color
                            content = re.sub(
                                r'color:\s*#4285f4',
                                f'color: {accent_color}',
                                content
                            )
                            
                            # Replace inline style background colors that might be using the blue color
                            content = re.sub(
                                r'background-color:\s*#4285f4',
                                f'background-color: {accent_color}',
                                content
                            )
                            
                            # Stats view specific inline replacements - replace all references to the dark purple
                            content = re.sub(
                                r'rgb\(70,\s*17,\s*120\)',
                                f'{darker_accent}',
                                content
                            )
                            content = re.sub(
                                r'#250096',
                                f'{darker_accent}',
                                content
                            )
                            
                            # Replace common chart colors in JavaScript code blocks within HTML
                            common_chart_colors = ['#4285f4', '#1a73e8', '#0f9d58', '#f4b400', '#db4437', '#3366CC', '#DC3912']
                            for color in common_chart_colors:
                                # Regular color references
                                content = content.replace(f'"{color}"', f'"{accent_color}"')
                                content = content.replace(f"'{color}'", f"'{accent_color}'")
                                
                                # Method calls with color - fill, stroke, etc.
                                color_method_patterns = [
                                    f'.fill("{color}"',
                                    f".fill('{color}'",
                                    f'.stroke("{color}"',
                                    f".stroke('{color}'",
                                    f'.color("{color}"',
                                    f".color('{color}'"
                                ]
                                
                                for pattern in color_method_patterns:
                                    content = content.replace(pattern, pattern.replace(color, accent_color))
                            
                            # Direct replacement of the specific backgroundColor/borderColor pattern in stats_view.html
                            content = content.replace(
                                "backgroundColor: 'rgba(25, 118, 210, 0.2)'",
                                f"backgroundColor: 'rgba({rgb_color}, 0.2)'"
                            )
                            content = content.replace(
                                "borderColor: 'rgba(25, 118, 210, 1)'",
                                f"borderColor: 'rgba({rgb_color}, 1)'"
                            )
                            
                            # Handle chart data series colors
                            if "stats_view.html" in file_path or "stats.html" in file_path:
                                # Replace chart styles using backgroundColor and borderColor properties
                                # Handle backgroundColor with rgba
                                content = re.sub(
                                    r'backgroundColor:\s*\'rgba\([^)]+\)\'',
                                    f"backgroundColor: 'rgba({rgb_color}, 0.2)'",
                                    content
                                )
                                
                                # Handle borderColor with rgba
                                content = re.sub(
                                    r'borderColor:\s*\'rgba\([^)]+\)\'',
                                    f"borderColor: 'rgba({rgb_color}, 1)'",
                                    content
                                )
                                
                                # Also handle double-quoted versions
                                content = re.sub(
                                    r'backgroundColor:\s*"rgba\([^)]+\)"',
                                    f'backgroundColor: "rgba({rgb_color}, 0.2)"',
                                    content
                                )
                                content = re.sub(
                                    r'borderColor:\s*"rgba\([^)]+\)"',
                                    f'borderColor: "rgba({rgb_color}, 1)"',
                                    content
                                )
                                
                                # Handle specific RGB value patterns (like rgba(25, 118, 210, x))
                                blue_rgb_patterns = [
                                    r'rgba\(25,\s*118,\s*210,\s*([0-9.]+)\)',
                                    r'rgba\(66,\s*133,\s*244,\s*([0-9.]+)\)',
                                    r'rgba\(26,\s*115,\s*232,\s*([0-9.]+)\)',
                                    r'rgba\(33,\s*150,\s*243,\s*([0-9.]+)\)',
                                    r'rgba\(3,\s*169,\s*244,\s*([0-9.]+)\)',
                                    r'rgba\(0,\s*188,\s*212,\s*([0-9.]+)\)',
                                ]
                                
                                for pattern in blue_rgb_patterns:
                                    content = re.sub(
                                        pattern,
                                        lambda match: f"rgba({rgb_color}, {match.group(1)})",
                                        content
                                    )
                                
                                # Also handle hex color versions
                                content = re.sub(
                                    r'backgroundColor:\s*[\'"]#[0-9a-fA-F]{6}[\'"]',
                                    f"backgroundColor: '{light_bg}'",
                                    content
                                )
                                content = re.sub(
                                    r'borderColor:\s*[\'"]#[0-9a-fA-F]{6}[\'"]',
                                    f"borderColor: '{accent_color}'",
                                    content
                                )
                                
                                # Look for chart configuration patterns with colors
                                chart_color_patterns = [
                                    r'palette\(\["#[0-9a-fA-F]{6}"\]',
                                    r'fill\("#[0-9a-fA-F]{6}"\)',
                                    r'stroke\("#[0-9a-fA-F]{6}"\)',
                                    r'color:\s*"#[0-9a-fA-F]{6}"',
                                    r'background:\s*"#[0-9a-fA-F]{6}"',
                                    r'\.background\(\)\.fill\("#[0-9a-fA-F]{6}"\)',
                                    r'\.fill\(\["#[0-9a-fA-F]{6}"\]\)',
                                    r'\.markers\(\)\.type\("[^"]+"\)\.fill\("#[0-9a-fA-F]{6}"\)',
                                    r'\.markers\(\)\.stroke\("#[0-9a-fA-F]{6}"\)',
                                ]
                                
                                for pattern in chart_color_patterns:
                                    content = re.sub(
                                        pattern,
                                        lambda match: match.group(0).replace('#' + match.group(0).split('#')[1].split('"')[0], accent_color),
                                        content
                                    )
                                
                                # Replace chart area background color
                                content = re.sub(
                                    r'\.fill\("rgba\((\d+),\s*(\d+),\s*(\d+),\s*([0-9.]+)\)"\)',
                                    f'.fill("rgba({rgb_color}, 0.1)")',
                                    content
                                )
                                
                                # Handle datasets array with backgroundColor and borderColor properties
                                # This pattern looks for dataset definition blocks
                                dataset_pattern = r'datasets:\s*\[\s*\{[^}]*\}\s*\]'
                                for dataset_match in re.finditer(dataset_pattern, content):
                                    dataset_text = dataset_match.group(0)
                                    
                                    # Replace backgroundColor in the dataset
                                    modified_dataset = re.sub(
                                        r'backgroundColor:\s*[\'"](?:rgba\([^)]+\)|#[0-9a-fA-F]{6})[\'"]',
                                        f"backgroundColor: 'rgba({rgb_color}, 0.2)'",
                                        dataset_text
                                    )
                                    
                                    # Replace borderColor in the dataset
                                    modified_dataset = re.sub(
                                        r'borderColor:\s*[\'"](?:rgba\([^)]+\)|#[0-9a-fA-F]{6})[\'"]',
                                        f"borderColor: 'rgba({rgb_color}, 1)'",
                                        modified_dataset
                                    )
                                    
                                    # Update content with the modified dataset
                                    content = content.replace(dataset_text, modified_dataset)
                                
                                # Also handle arrays of colors for multiple datasets
                                content = re.sub(
                                    r'backgroundColor:\s*\[\s*[\'"](?:rgba\([^)]+\)|#[0-9a-fA-F]{6})[\'"](?:\s*,\s*[\'"](?:rgba\([^)]+\)|#[0-9a-fA-F]{6})[\'"])*\s*\]',
                                    f"backgroundColor: ['rgba({rgb_color}, 0.2)']",
                                    content
                                )
                                content = re.sub(
                                    r'borderColor:\s*\[\s*[\'"](?:rgba\([^)]+\)|#[0-9a-fA-F]{6})[\'"](?:\s*,\s*[\'"](?:rgba\([^)]+\)|#[0-9a-fA-F]{6})[\'"])*\s*\]',
                                    f"borderColor: ['rgba({rgb_color}, 1)']",
                                    content
                                )
                        
                        # Handle CSS file color replacements
                        elif file.endswith('.css'):
                            # Main background color in stats view
                            if any(x in file_path for x in ["stats-view.css", "stats.css"]):
                                # Replace the stats view background color - look for all instances of #250096
                                content = content.replace('#250096', darker_accent)
                                
                                # Also check for the dark purple in rgb format
                                content = content.replace('rgb(70, 17, 120)', darker_accent)
                            
                            # Standard color replacements for all CSS files
                            color_replacements = {
                                # Primary blue color variations
                                '#4285f4': accent_color,
                                '#1a73e8': hover_color,
                                '#4285F4': accent_color.upper(),
                                '#1557b0': adjust_color(accent_color, -30),
                                '#0d47a1': adjust_color(accent_color, -40),
                                'rgba(66, 133, 244, 0.15)': f'rgba({rgb_color}, 0.15)',
                                'rgba(66, 133, 244, 0.3)': f'rgba({rgb_color}, 0.3)',
                                'rgba(66, 133, 244, 0.4)': f'rgba({rgb_color}, 0.4)',
                                'rgba(66, 133, 244, 0.5)': f'rgba({rgb_color}, 0.5)',
                                'rgba(66, 133, 244, 0.7)': f'rgba({rgb_color}, 0.7)',
                                'rgba(26, 115, 232, 0.2)': f'rgba({rgb_color}, 0.2)',
                                'rgba(13, 71, 161, 0.2)': f'rgba({hex_to_rgb(adjust_color(accent_color, -30))}, 0.2)',
                                
                                # Hover/active color variations
                                '#e8f0fe': light_bg,
                                '#d2e3fc': lighter_bg,
                            }
                            
                            for old_color, new_color in color_replacements.items():
                                content = content.replace(old_color, new_color)
                            
                            # Replace the color in the gradient header of the form
                            if 'linear-gradient(to right, #4285f4, #4285f4, #34a853, #fbbc04, #ea4335)' in content:
                                gradient = f'linear-gradient(to right, {accent_color}, {accent_color}, {accent_color}, {hover_color}, {adjust_color(accent_color, -30)})'
                                content = content.replace('linear-gradient(to right, #4285f4, #4285f4, #34a853, #fbbc04, #ea4335)', gradient)
                            
                            # Update border and focus states
                            if '#password:focus' in content:
                                content = re.sub(
                                    r'border-color:\s*#4285f4',
                                    f'border-color: {accent_color}',
                                    content
                                )
                                content = re.sub(
                                    r'border-color:\s*#1a73e8',
                                    f'border-color: {accent_color}',
                                    content
                                )
                            
                            # Update navbar links and active states
                            if '.navbar a {' in content:
                                # Handle navbar link colors
                                content = re.sub(
                                    r'\.navbar a:hover\s*{[^}]*color:\s*#4285f4',
                                    f'.navbar a:hover {{color: {accent_color}',
                                    content
                                )
                                content = re.sub(
                                    r'\.navbar a\.active\s*{[^}]*color:\s*#4285f4',
                                    f'.navbar a.active {{color: {accent_color}',
                                    content
                                )
                            
                            # Update submit button colors
                            if 'button[type="submit"]' in content:
                                content = re.sub(
                                    r'background-color:\s*#4285f4',
                                    f'background-color: {accent_color}',
                                    content
                                )
                                content = re.sub(
                                    r'background-color:\s*#1a73e8',
                                    f'background-color: {accent_color}',
                                    content
                                )
                                
                                # Special case for hover states with specific values
                                if 'button[type="submit"]:hover' in content:
                                    content = re.sub(
                                        r'button\[type="submit"\]:hover\s*{[^}]*background-color:\s*#1a73e8',
                                        f'button[type="submit"]:hover {{background-color: {hover_color}',
                                        content
                                    )
                            
                            # Update feature headings
                            if '.features h2' in content:
                                content = re.sub(
                                    r'\.features h2\s*{[^}]*color:\s*var\(--primary-color\)',
                                    f'.features h2 {{color: {accent_color}',
                                    content
                                )
                            
                            # Update scrollbar colors
                            if 'scrollbar-thumb' in content:
                                content = content.replace('rgba(66, 133, 244,', f'rgba({rgb_color},')
                            
                            # Update header text color if it exists
                            if 'header h1' in content:
                                content = re.sub(
                                    r'header h1\s*{[^}]*color:\s*var\(--primary-color\)',
                                    f'header h1 {{color: {accent_color}',
                                    content
                                )
                        
                        # Handle JavaScript files that might have color definitions
                        elif file.endswith('.js'):
                            # Replace colors in chart configurations and data points
                            common_chart_colors = ['#4285f4', '#1a73e8', '#0f9d58', '#f4b400', '#db4437', '#3366CC', '#DC3912']
                            for color in common_chart_colors:
                                # Regular color references
                                content = content.replace(f'"{color}"', f'"{accent_color}"')
                                content = content.replace(f"'{color}'", f"'{accent_color}'")
                                
                                # Method calls with color - fill, stroke, etc.
                                color_method_patterns = [
                                    f'.fill("{color}"',
                                    f".fill('{color}'",
                                    f'.stroke("{color}"',
                                    f".stroke('{color}'",
                                    f'.color("{color}"',
                                    f".color('{color}'"
                                ]
                                
                                for pattern in color_method_patterns:
                                    content = content.replace(pattern, pattern.replace(color, accent_color))
                            
                            # Replace chart area colors
                            content = re.sub(
                                r'\.area\(\)\s*\.\s*fill\([^)]+\)',
                                f'.area().fill("{light_bg}", 0.6)',
                                content
                            )
                            
                            # Replace dark purple colors in stats view scripts
                            if "stats-view-script.js" in file_path or "stats-script.js" in file_path:
                                content = content.replace('#250096', darker_accent)
                                content = content.replace('rgb(70, 17, 120)', darker_accent)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                except Exception as e:
                    print(f"Error replacing content in {file_path}: {e}")

def hex_to_rgb(hex_color):
    """Convert hex color to RGB format"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"{r}, {g}, {b}"

def color_with_opacity(hex_color, opacity):
    """Create a color with opacity"""
    rgb = hex_to_rgb(hex_color)
    return f"rgba({rgb}, {opacity})"

def adjust_color(color, amount):
    """Adjust the brightness of a hex color"""
    color = color.lstrip('#')
    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    rgb = tuple(max(0, min(255, x + amount)) for x in rgb)
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def create_customized_shortener(name, logo_file, favicon_file, deployment_option, accent_color=None, advanced_options=None, mongodb_uri=None):
    """
    Create a customized URL shortener based on the provided parameters
    """
    try:
        # Create a temporary directory to hold the modified shortener
        temp_dir = tempfile.mkdtemp()
        
        # Copy the URL shortener source code
        shortener_dir = os.path.join(temp_dir, name.lower().replace(" ", "_"))
        shutil.copytree(URL_SHORTENER_SRC, shortener_dir)
        
        # Create README file
        create_readme_file(shortener_dir, name)
        
        # Create deployment instructions file
        create_deployment_instructions(shortener_dir, deployment_option, name)
        
        # Create .env file with MongoDB connection string
        env_content = f"MONGODB_URI={mongodb_uri or 'mongodb://localhost:27017/urlshortener'}"
        with open(os.path.join(shortener_dir, '.env'), 'w') as f:
            f.write(env_content)
        
        # Special configuration for Azure deployment
        if deployment_option == 'azure':
            # Update the web.config to point to the correct entry point
            web_config_path = os.path.join(shortener_dir, 'web.config')
            if os.path.exists(web_config_path):
                # On Linux, we don't need web.config, so remove it
                os.remove(web_config_path)
            
            # Create a startup.txt file for Azure App Service (Linux)
            startup_txt = "python -m gunicorn --bind=0.0.0.0 --timeout 600 wsgi:app"
            with open(os.path.join(shortener_dir, 'startup.txt'), 'w') as f:
                f.write(startup_txt)

            print(f"Creating app.py in {shortener_dir}")
            # Make sure app.py exists at the root (as we saw it was looking for this)
            if not os.path.exists(os.path.join(shortener_dir, 'app.py')):
                app_py = """import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Log the environment for debugging
logging.info("Starting app.py")
logging.info(f"Python version: {sys.version}")
logging.info(f"Current directory: {os.getcwd()}")
try:
    logging.info(f"Directory contents: {os.listdir('.')}")
except Exception as e:
    logging.error(f"Error listing directory: {e}")

try:
    # Try to import from main.py
    logging.info("Attempting to import from main.py")
    from main import app
    logging.info("Successfully imported app from main.py")
except ImportError as e:
    logging.error(f"Error importing from main: {e}")
    
    # Create a simple fallback app
    try:
        from flask import Flask
        app = Flask(__name__)
    
        @app.route('/')
        def index():
            return "URL Shortener - app.py fallback route"
    
        logging.info("Created fallback Flask app")
    except Exception as flask_error:
        logging.error(f"Error creating fallback Flask app: {flask_error}")
        raise

# Create an application variable for WSGI compatibility
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logging.info(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port)
"""
                with open(os.path.join(shortener_dir, 'app.py'), 'w') as f:
                    f.write(app_py)
                
                # Make it executable
                os.chmod(os.path.join(shortener_dir, 'app.py'), 0o755)
                
            # Create a Linux deployment script
            run_sh = """#!/bin/bash
echo "Starting URL Shortener setup on Azure Linux..."

# Install required packages
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn python-dotenv

# Set environment variables
export PYTHONPATH=/home/site/wwwroot
export FLASK_APP=main.py

echo "Setup completed successfully!"
"""
            with open(os.path.join(shortener_dir, 'run.sh'), 'w') as f:
                f.write(run_sh)
            
            # Make the script executable
            os.chmod(os.path.join(shortener_dir, 'run.sh'), 0o755)
            
            # Create a health check page
            health_check = """<!DOCTYPE html>
<html>
<head>
    <title>URL Shortener Health Check</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>URL Shortener Health Check</h1>
    <p class="success">The application is running!</p>
    <p>If you're seeing this page directly, navigate to the <a href="/index">main application</a>.</p>
</body>
</html>
"""
            with open(os.path.join(shortener_dir, 'health.html'), 'w') as f:
                f.write(health_check)
            
            # Update requirements to ensure gunicorn is included
            req_path = os.path.join(shortener_dir, 'requirements.txt')
            if os.path.exists(req_path):
                with open(req_path, 'r') as f:
                    req_content = f.read()
                
                # Add necessary Azure packages
                required_packages = [
                    "gunicorn==21.2.0",
                    "python-dotenv==1.0.0"
                ]
                
                for package in required_packages:
                    if package.split('==')[0] not in req_content:
                        with open(req_path, 'a') as f:
                            f.write(f"\n{package}")
                            
            # Create a wsgi.py file specifically for Azure Linux App Service
            wsgi_py = """import os
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
logging.info(f"Directory contents: {os.listdir('.')}")

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
            with open(os.path.join(shortener_dir, 'wsgi.py'), 'w') as f:
                f.write(wsgi_py)
        
        # Ensure static directories exist
        static_dir = os.path.join(shortener_dir, 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir, exist_ok=True)
            
        img_dir = os.path.join(static_dir, 'img')
        if not os.path.exists(img_dir):
            # Check if 'images' directory exists instead
            images_dir = os.path.join(static_dir, 'images')
            if os.path.exists(images_dir):
                img_dir = images_dir
            else:
                # Create the img directory
                os.makedirs(img_dir, exist_ok=True)
        
        # Generate default text logo if no logo provided
        if logo_file is None:
            try:
                # Try to find the original logo
                original_logo_path = find_static_asset_path(URL_SHORTENER_SRC, 'text.png', ['png', 'jpg', 'jpeg', 'gif'])
                
                if original_logo_path and os.path.exists(original_logo_path):
                    # Copy the original logo to the new location
                    with open(original_logo_path, 'rb') as original:
                        logo_data = original.read()
                        
                    with open(os.path.join(img_dir, 'text.png'), 'wb') as f:
                        f.write(logo_data)
                else:
                    # Create a basic placeholder logo with the name
                    from PIL import Image, ImageDraw, ImageFont
                    img = Image.new('RGB', (300, 150), color='white')
                    d = ImageDraw.Draw(img)
                    
                    # Try to use a system font or fall back to default
                    try:
                        # Try several common fonts
                        common_fonts = ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "Verdana.ttf", "Tahoma.ttf"]
                        font = None
                        
                        for font_name in common_fonts:
                            try:
                                font = ImageFont.truetype(font_name, 36)
                                break
                            except:
                                continue
                                
                        if font is None:
                            font = ImageFont.load_default()
                    except:
                        font = ImageFont.load_default()
                    
                    # Draw text centered on image
                    text_width = d.textlength(name, font=font)
                    text_position = ((300 - text_width) // 2, 60)
                    d.text(text_position, name, fill='black', font=font)
                    
                    # Save the image
                    logo_path = os.path.join(img_dir, 'text.png')
                    img.save(logo_path, format='PNG')
                    print(f"Created placeholder logo at {logo_path}")
            except Exception as e:
                print(f"Error creating logo: {e}")
                # Create an empty PNG file as fallback
                with open(os.path.join(img_dir, 'text.png'), 'wb') as f:
                    # Create a 1x1 transparent PNG
                    img = Image.new('RGBA', (1, 1), (255, 255, 255, 0))
                    img_io = BytesIO()
                    img.save(img_io, format='PNG')
                    f.write(img_io.getvalue())
        else:
            # Process the uploaded logo
            logo_io = process_image(logo_file)
            if logo_io:
                # Save the processed logo
                with open(os.path.join(img_dir, 'text.png'), 'wb') as f:
                    f.write(logo_io.read())
        
        # Handle favicon if provided
        if favicon_file:
            try:
                # Process the uploaded favicon
                favicon_io = process_image(favicon_file, output_format='ICO')
                if favicon_io:
                    # Save the processed favicon
                    with open(os.path.join(img_dir, 'favicon.png'), 'wb') as f:
                        f.write(favicon_io.read())
            except Exception as favicon_error:
                print(f"Error processing favicon: {favicon_error}")
                # Try to use a default favicon instead
                try:
                    # Create a simple colored square as favicon
                    from PIL import Image
                    img = Image.new('RGB', (32, 32), color=accent_color or '#4285f4')
                    img_io = BytesIO()
                    img.save(img_io, format='PNG')
                    img_io.seek(0)
                    
                    with open(os.path.join(img_dir, 'favicon.png'), 'wb') as f:
                        f.write(img_io.getvalue())
                except Exception as e:
                    print(f"Error creating default favicon: {e}")
        else:
            try:
                # Try to copy the original favicon if it exists
                original_favicon_path = find_static_asset_path(URL_SHORTENER_SRC, 'favicon.png', ['png', 'ico', 'jpg'])
                if original_favicon_path and os.path.exists(original_favicon_path):
                    with open(original_favicon_path, 'rb') as original:
                        favicon_data = original.read()
                        
                    with open(os.path.join(img_dir, 'favicon.png'), 'wb') as f:
                        f.write(favicon_data)
                else:
                    # Create a simple colored square as favicon
                    from PIL import Image
                    img = Image.new('RGB', (32, 32), color=accent_color or '#4285f4')
                    img_io = BytesIO()
                    img.save(img_io, format='PNG')
                    img_io.seek(0)
                    
                    with open(os.path.join(img_dir, 'favicon.png'), 'wb') as f:
                        f.write(img_io.getvalue())
            except Exception as favicon_error:
                print(f"Error handling favicon: {favicon_error}")
                # Don't let favicon error stop the process
        
        # Replace name in files
        replace_name_in_files(shortener_dir, name, accent_color)
        
        # Handle advanced options
        if advanced_options is not None:
            handle_advanced_options(shortener_dir, advanced_options)
        
        # Create ZIP file
        zip_path = os.path.join(temp_dir, f"{name.lower().replace(' ', '_')}_url_shortener.zip")
        
        # Special handling for Azure deployment - FIXED: Create the zip with wsgi.py at the root
        if deployment_option == 'azure':
            # Use the helper function to create a proper Azure deployment zip
            zip_path = create_azure_deployment_zip(zip_path, shortener_dir, temp_dir)
        else:
            # Standard zip creation for non-Azure deployments
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(shortener_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
        
        return zip_path
    except Exception as e:
        print(f"Error creating customized shortener: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_readme_file(shortener_dir, name):
    """Create a README.md file for the URL shortener"""
    readme_content = f"""# {name}

A URL shortening service that allows users to create shortened links and track their performance.

## Features

- URL shortening - converting long URLs into compact, shareable links
- Statistics tracking - collecting data on clicks, browsers, and platforms
- Visualization - displaying click data through interactive charts and graphs
- Export functionality - allowing users to download stats in various formats (JSON, CSV, XLSX)
- API access - enabling programmatic interaction with the service

## Deployment

Please see the DEPLOYMENT.md file for detailed deployment instructions.
"""
    
    with open(os.path.join(shortener_dir, 'README.md'), 'w') as f:
        f.write(readme_content)

def create_deployment_instructions(shortener_dir, deployment_option, name):
    """
    Creates deployment instructions based on the selected option
    """
    instructions = f"# {name} Deployment Instructions\n\n"
    
    if deployment_option == 'docker':
        instructions += f"""## Docker Deployment

1. Make sure you have Docker and Docker Compose installed on your system.
2. Navigate to the {name.lower().replace(" ", "_")} directory.
3. Create a `.env` file with your MongoDB connection string:
   ```
   MONGODB_URI=mongodb://mongo:27017/urlshortener
   ```
4. Run the following command to start the application:
   ```
   docker-compose up -d
   ```
5. The {name} will be available at http://localhost:8000

To stop the application, run:
```
docker-compose down
```

## Customization Options

- To change the port, edit the `docker-compose.yml` file and update the port mapping.
- To use an external MongoDB database, update the MONGODB_URI in the `.env` file.
"""
    elif deployment_option == 'azure':
        instructions += f"""## Azure Deployment

Your {name} has been deployed to Azure App Service!

### Accessing Your Deployed Application
- The URL to access your URL shortener will be shown once the deployment is complete.
- Your application is running on a Free/Basic Azure App Service plan.

### Managing Your Application
1. Log in to the [Azure Portal](https://portal.azure.com)
2. Navigate to "App Services" to find your application
3. From there you can:
   - View application logs
   - Monitor performance
   - Configure settings
   - Scale up if needed

### MongoDB Database
- Your application is using Azure Cosmos DB with MongoDB API
- Connection details are automatically configured in your app's Application Settings

### Custom Domain (Optional)
To use a custom domain with your URL shortener:
1. Go to your App Service in the Azure Portal
2. Select "Custom domains" from the left navigation
3. Follow the instructions to add and verify your domain

### SSL Certificate (Optional)
To secure your URL shortener with HTTPS:
1. In your App Service, select "TLS/SSL settings"
2. You can use a free Azure-managed certificate or upload your own
"""
    else:  # standalone
        instructions += f"""## Standalone Python Deployment

1. Make sure you have Python 3.8+ installed on your system.
2. Navigate to the {name.lower().replace(" ", "_")} directory.
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Install and start MongoDB on your system, or use a cloud MongoDB service.
5. Create a `.env` file with your MongoDB connection string:
   ```
   MONGODB_URI=mongodb://localhost:27017/urlshortener
   ```
   Or if using a cloud service:
   ```
   MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/urlshortener
   ```
6. Run the application:
   ```
   python main.py
   ```
7. The {name} will be available at http://localhost:8000

## Customization Options

- To change the port, edit the `main.py` file and update the port number in the `app.run()` function.
- To configure the application for production, consider using a WSGI server like Gunicorn.
"""
    
    # Write the instructions to a file
    with open(os.path.join(shortener_dir, 'DEPLOYMENT.md'), 'w') as f:
        f.write(instructions)

def handle_advanced_options(directory, advanced_options):
    """
    Modifies the index.html file to comment out features not selected in advanced options
    """
    # Find the index.html file
    index_file = os.path.join(directory, 'templates', 'index.html')
    
    if not os.path.exists(index_file):
        print(f"Index file not found at {index_file}")
        return
    
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Comment out custom alias option if not selected
        if 'custom_alias' not in advanced_options:
            # Find and comment out alias input container
            alias_pattern = r'<div class="child">\s*<label for="alias">Custom Alias</label>.*?<p id="non-imp">Leave blank for a random short URL</p>\s*</div>'
            content = comment_out_pattern(content, alias_pattern, re.DOTALL)
        
        # Track what options are disabled to adjust layout
        disabled_options = []
        
        # Comment out password protection option if not selected
        if 'password_protection' not in advanced_options:
            # Find and comment out password div
            password_pattern = r'<div id="password-div">.*?</div>'
            content = comment_out_pattern(content, password_pattern, re.DOTALL)
            
            # Also comment out password error div
            error_pattern = r'<div id="password-error" class="error-message hidden"></div>'
            content = comment_out_pattern(content, error_pattern)
            
            disabled_options.append('password_protection')
        
        # Comment out maximum clicks option if not selected
        if 'max_clicks' not in advanced_options:
            # Find and comment out max clicks div
            max_clicks_pattern = r'<div id="clicks-div">.*?</div>'
            content = comment_out_pattern(content, max_clicks_pattern, re.DOTALL)
            
            disabled_options.append('max_clicks')
        
        # If only one option remains enabled, add a class to make it full-width
        if len(disabled_options) == 1:
            # If max_clicks is disabled but password is enabled
            if 'max_clicks' in disabled_options and 'password_protection' not in disabled_options:
                # Add full-width class to password div
                content = re.sub(
                    r'<div id="password-div">', 
                    '<div id="password-div" class="full-width">', 
                    content
                )
            
            # If password is disabled but max_clicks is enabled
            elif 'password_protection' in disabled_options and 'max_clicks' not in disabled_options:
                # Add full-width class to max clicks div
                content = re.sub(
                    r'<div id="clicks-div">', 
                    '<div id="clicks-div" class="full-width">', 
                    content
                )
                
        # If both options are disabled, comment out the entire options container
        if 'max_clicks' in disabled_options and 'password_protection' in disabled_options:
            options_container_pattern = r'<div class="options-container">.*?</div>'
            content = comment_out_pattern(content, options_container_pattern, re.DOTALL)
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Now let's also add CSS to ensure proper styling
        add_fullwidth_css(directory)
            
    except Exception as e:
        print(f"Error handling advanced options: {e}")

def add_fullwidth_css(directory):
    """
    Add CSS to handle full-width styling for remaining elements
    """
    # Find the CSS file
    css_file = os.path.join(directory, 'static', 'css', 'index.css')
    
    if not os.path.exists(css_file):
        print(f"CSS file not found at {css_file}")
        return
    
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add styles for full-width elements if not already present
        if '.full-width' not in content:
            full_width_css = """
/* Styles for full-width form elements */
.full-width {
    width: 100% !important;
    max-width: 100% !important;
}

.options-container > div.full-width {
    width: 100% !important;
}

.full-width input {
    width: 100% !important;
    max-width: 100% !important;
}

/* When only one option is visible, its input should take full width */
.options-container > div:only-child {
    width: 100% !important;
}

.options-container > div:only-child input {
    width: 100% !important;
}

/* Ensure proper spacing when only one input is shown */
#advanced-options:not(:has(.options-container)) {
    margin-bottom: 20px;
}

/* Adjust password input when it's the only one */
#password-div.full-width #password {
    width: 100% !important;
    max-width: none !important;
}

/* Adjust max-clicks input when it's the only one */
#clicks-div.full-width #max-clicks {
    width: 100% !important;
    max-width: none !important;
}
"""
            content += full_width_css
            
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        # Also specifically update the password input styling
        password_css_pattern = r'#password\s*\{[^}]*\}'
        if re.search(password_css_pattern, content):
            updated_password_css = """
#password {
    display: block;
    width: 100%;
    padding: 14px 18px;
    border-radius: 16px;
    font-size: 1rem;
    color: #3c4043;
    background: #f5f5f5;
    border: 1px solid rgba(0, 0, 0, 0.06);
    transition: all 0.25s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    margin-top: 20px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}
"""
            content = re.sub(password_css_pattern, updated_password_css, content, flags=re.DOTALL)
            
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
    except Exception as e:
        print(f"Error adding full-width CSS: {e}")

def comment_out_pattern(content, pattern, flags=0):
    """
    Find a pattern and comment it out
    """
    def replace_with_comment(match):
        return f'<!-- {match.group(0)} -->'
    
    return re.sub(pattern, replace_with_comment, content, flags=flags)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return "OK", 200

# Global initialization flag
initialization_complete = False

# Function to run heavy initialization tasks in the background
def run_delayed_startup():
    global initialization_complete
    if initialization_complete:
        return
    
    try:
        # Import heavy modules here to defer loading
        import time
        logging.info("Starting delayed initialization...")
        
        # Perform any heavy initialization here
        # Example: database connections, loading large models, etc.
        # But avoid anything that would take more than a few seconds
        
        # Mark initialization as complete
        initialization_complete = True
        app.config['STARTUP_COMPLETE'] = True
        logging.info("Delayed initialization complete")
    except Exception as e:
        logging.error(f"Error during delayed initialization: {e}")

# Replace the deprecated before_first_request with before_request
@app.before_request
def before_request_func():
    global initialization_complete
    if not initialization_complete:
        # Trigger the delayed startup in a way that doesn't block the first request
        from threading import Thread
        thread = Thread(target=run_delayed_startup)
        thread.daemon = True
        thread.start()

@app.route('/generate', methods=['POST'])
def generate():
    # Get form data
    name = request.form.get('name', 'URL Shortener')
    deployment_option = request.form.get('deployment_option', 'standalone')
    accent_color = request.form.get('accent_color', '#3f51b5')
    mongodb_uri = request.form.get('mongodb_uri', 'mongodb://localhost:27017/urlshortener')
    
    # Get advanced options (returns list of selected values)
    advanced_options = request.form.getlist('advanced_options')
    
    # Check if name is provided
    if not name:
        flash('Please provide a name for your URL shortener.')
        return redirect(url_for('index'))
    
    # Get files
    logo_file = request.files.get('logo')
    favicon_file = request.files.get('favicon')
    
    # Validate files if provided
    if logo_file and logo_file.filename and not allowed_file(logo_file.filename):
        flash('Logo file must be an image (PNG, JPG, JPEG, GIF).')
        return redirect(url_for('index'))
    
    if favicon_file and favicon_file.filename and not allowed_file(favicon_file.filename):
        flash('Favicon file must be an image (PNG, JPG, JPEG, GIF).')
        return redirect(url_for('index'))
    
    # Create the customized shortener
    zip_path = create_customized_shortener(
        name, 
        logo_file if logo_file and logo_file.filename else None,
        favicon_file if favicon_file and favicon_file.filename else None,
        deployment_option,
        accent_color,
        advanced_options,
        mongodb_uri
    )
    
    if not zip_path:
        flash('An error occurred while generating your URL shortener. Please try again.')
        return redirect(url_for('index'))
    
    # Handle Azure deployment if selected
    if deployment_option == 'azure':
        # Deploy to Azure
        app_url = deploy_to_azure(zip_path, name)
        
        if app_url:
            # Create response template with deployment info
            return render_template(
                'azure_deployed.html', 
                app_name=name,
                app_url=app_url
            )
        else:
            flash('An error occurred during Azure deployment. The application package was created successfully but could not be deployed to Azure. You can download the package and deploy it manually, or try again with a different deployment option.')
            # Provide the package for download instead
            return send_file(
                zip_path, 
                as_attachment=True, 
                download_name=f'{name.lower().replace(" ", "_")}_url_shortener.zip',
                mimetype='application/zip'
            )
    else:
        # For other deployment options, send zip file as attachment
        return send_file(
            zip_path, 
            as_attachment=True, 
            download_name=f'{name.lower().replace(" ", "_")}_url_shortener.zip',
            mimetype='application/zip'
        )

def deploy_to_azure(zip_path, name):
    """
    Deploy the URL shortener to Azure App Service
    """
    try:
        # Check if the required Azure packages are installed
        try:
            from azure.identity import InteractiveBrowserCredential
            from azure.mgmt.resource import ResourceManagementClient
            from azure.mgmt.web import WebSiteManagementClient
            from azure.mgmt.subscription import SubscriptionClient
            import requests
            import uuid
            import time
        except ImportError as e:
            print(f"Required Azure package not found: {e}")
            flash("Azure deployment requires additional packages. Please make sure azure-identity, azure-mgmt-web, azure-mgmt-resource, azure-mgmt-subscription, and requests are installed.")
            return None
        
        # Check if the zip file exists
        if not os.path.exists(zip_path):
            print(f"Zip file not found at {zip_path}")
            return None
        
        # Verify the zip file contains wsgi.py at root level
        print("Verifying zip file contents...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                if 'wsgi.py' not in file_list:
                    print("Error: wsgi.py not found at root level in the zip file")
                    flash("Deployment failed: wsgi.py not found in the package. Please rebuild the package.")
                    return None
        except Exception as zip_error:
            print(f"Error checking zip contents: {zip_error}")
            return None
            
        # Extract the MongoDB connection string from the .env file inside the zip
        mongodb_uri = "mongodb://localhost:27017/urlshortener"  # Default value
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Find the .env file
                env_files = [f for f in zip_ref.namelist() if f.endswith('.env')]
                if env_files:
                    with zip_ref.open(env_files[0]) as env_file:
                        env_content = env_file.read().decode('utf-8')
                        # Extract MONGODB_URI from the env file
                        for line in env_content.splitlines():
                            if line.startswith('MONGODB_URI='):
                                mongodb_uri = line.split('=', 1)[1].strip()
                                break
        except Exception as env_error:
            print(f"Error reading MongoDB URI from .env file: {env_error}")
            # Continue with default URI
        
        # No need to modify the ZIP file - Azure configuration files are already included in the source code
        print("Using ZIP file with pre-configured Azure files...")
        
        # Start the Azure authentication process
        print("Starting Azure authentication...")
        try:
            credential = InteractiveBrowserCredential()
        except Exception as auth_error:
            print(f"Azure authentication error: {auth_error}")
            return None
            
        # Get subscription ID
        try:
            subscription_id = get_azure_subscription_id(credential)
            if not subscription_id:
                print("No Azure subscription found. Please make sure you have an active Azure subscription.")
                flash("No Azure subscription found. Please make sure you have an active Azure subscription.")
                return None
        except Exception as sub_error:
            print(f"Error getting Azure subscription: {sub_error}")
            return None
        
        # Generate a unique name for the resources
        unique_name = f"{name.lower().replace(' ', '')}"
        # Clean up the name to only contain alphanumeric characters
        unique_name = re.sub(r'[^a-z0-9]', '', unique_name)
        # Ensure the name starts with a letter
        if not unique_name[0].isalpha():
            unique_name = 'app' + unique_name
        # Add a unique suffix
        unique_id = str(uuid.uuid4())[:8]
        app_name = f"{unique_name}{unique_id}"
        app_name = app_name[:20]  # Make even shorter to avoid issues
        resource_group_name = f"{app_name}-rg"
        location = "canadacentral"  # Use Canada Central region
        
        print(f"Creating resource group: {resource_group_name}...")
        try:
            # Create the resource group
            resource_client = ResourceManagementClient(credential, subscription_id=subscription_id)
            resource_client.resource_groups.create_or_update(
                resource_group_name,
                {"location": location}
            )
        except Exception as rg_error:
            print(f"Error creating resource group: {rg_error}")
            return None
        
        print(f"Creating app service plan: {app_name}-plan...")
        try:
            # Create App Service Plan (Free tier)
            web_client = WebSiteManagementClient(credential, subscription_id=subscription_id)
            app_service_plan_name = f"{app_name}-plan"
            
            web_client.app_service_plans.begin_create_or_update(
                resource_group_name,
                app_service_plan_name,
                {
                    "location": location,
                    "reserved": True,  # This indicates Linux
                    "sku": {
                        "name": "F1",  # Free tier
                        "tier": "Free"
                    },
                    "kind": "linux"  # Explicitly set Linux
                }
            ).result()
        except Exception as plan_error:
            print(f"Error creating app service plan: {plan_error}")
            return None
        
        print(f"Creating web app: {app_name}...")
        try:
            # Create Web App with specific configuration for Python on Linux
            web_client.web_apps.begin_create_or_update(
                resource_group_name,
                app_name,
                {
                    "location": location,
                    "server_farm_id": f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Web/serverfarms/{app_service_plan_name}",
                    "site_config": {
                        "linux_fx_version": "PYTHON|3.9",  # For Linux, use this instead of python_version
                        "app_command_line": "gunicorn --bind=0.0.0.0 --timeout 600 wsgi:app",
                        "app_settings": [
                            {
                                "name": "MONGODB_URI",
                                "value": mongodb_uri
                            },
                            {
                                "name": "SCM_DO_BUILD_DURING_DEPLOYMENT",
                                "value": "true"
                            },
                            {
                                "name": "PYTHON_ENV",
                                "value": "production"
                            },
                            {
                                "name": "WEBSITE_HTTPLOGGING_RETENTION_DAYS",
                                "value": "7"
                            }
                        ]
                    },
                    "reserved": True  # This is required for Linux
                }
            ).result()
            
            # Configure Python version and logging
            web_client.web_apps.update_configuration(
                resource_group_name,
                app_name,
                {
                    "http_logging_enabled": True,
                    "detailed_error_logging_enabled": True,
                    "request_tracing_enabled": True,
                    "use_32_bit_worker_process": True
                }
            )
        except Exception as webapp_error:
            print(f"Error creating web app: {webapp_error}")
            return None
        
        # Wait a moment for the app to be ready
        print("Waiting for app service to be ready...")
        time.sleep(10)
        
        print("Getting publishing credentials...")
        try:
            # Get publishing credentials
            credentials = web_client.web_apps.begin_list_publishing_credentials(
                resource_group_name,
                app_name
            ).result()
            
            publishing_user = credentials.publishing_user_name
            publishing_password = credentials.publishing_password
            
            # Generate deployment URL
            deployment_url = f"https://{app_name}.scm.azurewebsites.net/api/zipdeploy"
        except Exception as cred_error:
            print(f"Error getting publishing credentials: {cred_error}")
            return None
        
        print(f"Deploying zip package to {deployment_url}...")
        try:
            # Add retry logic for DNS resolution issues
            max_retries = 5
            retry_delay = 15  # seconds
            success = False
            
            for attempt in range(1, max_retries + 1):
                try:
                    # Upload and deploy ZIP package
                    with open(zip_path, 'rb') as f:
                        response = requests.post(
                            deployment_url,
                            auth=(publishing_user, publishing_password),
                            headers={"Content-Type": "application/zip"},
                            data=f,
                            timeout=180  # Increased timeout
                        )
                        
                        if response.status_code >= 400:
                            print(f"Deployment attempt {attempt} failed with status code: {response.status_code}")
                            print(f"Response: {response.text}")
                            if attempt < max_retries:
                                print(f"Retrying in {retry_delay} seconds...")
                                time.sleep(retry_delay)
                                retry_delay *= 1.5  # Increase delay for next retry
                            continue
                        else:
                            print(f"Deployment successful on attempt {attempt}")
                            success = True
                            break
                except requests.exceptions.RequestException as e:
                    print(f"Request error on attempt {attempt}: {e}")
                    if attempt < max_retries:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 1.5  # Increase delay for next retry
            
            # Use REST API for deployment (primary method)
            if not success:
                print("Trying alternative deployment method...")
                
                # Try using Azure CLI if available
                try:
                    import subprocess
                    
                    # Check if Azure CLI is installed
                    try:
                        subprocess.run(["az", "--version"], check=True, capture_output=True)
                        has_az_cli = True
                    except (subprocess.SubprocessError, FileNotFoundError):
                        has_az_cli = False
                    
                    if has_az_cli:
                        print("Azure CLI found, attempting deployment via CLI...")
                        
                        # Login with the credential from Azure SDK
                        os.environ["AZURE_SUBSCRIPTION_ID"] = subscription_id
                        
                        # Deploy using az webapp deployment command
                        deploy_cmd = [
                            "az", "webapp", "deployment", "source", "config-zip",
                            "--resource-group", resource_group_name,
                            "--name", app_name,
                            "--src", zip_path
                        ]
                        
                        deploy_result = subprocess.run(
                            deploy_cmd,
                            check=True,
                            capture_output=True,
                            text=True
                        )
                        
                        print(f"Azure CLI deployment result: {deploy_result.stdout}")
                        success = True
                    else:
                        print("Azure CLI not found, cannot use fallback deployment method")
                except Exception as cli_error:
                    print(f"Error using CLI fallback deployment: {cli_error}")
                    
            if not success:
                print("All deployment attempts failed")
                return None
        except Exception as deploy_error:
            print(f"Error deploying zip package: {deploy_error}")
            return None
        
        # Wait for the deployment to complete
        print("Waiting for deployment to complete...")
        time.sleep(45)
        
        # Return the URL of the deployed application
        app_url = f"https://{app_name}.azurewebsites.net"
        print(f"Deployment successful! App URL: {app_url}")
        
        # Test the URL to verify it's accessible
        try:
            test_response = requests.get(app_url, timeout=30)
            print(f"Test connection to {app_url}: Status Code {test_response.status_code}")
        except Exception as test_error:
            print(f"Warning: Could not connect to {app_url}: {test_error}")
            print("The application may still be starting up, please try accessing it in a few minutes.")
        
        return app_url
    
    except Exception as e:
        print(f"Error deploying to Azure: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_azure_subscription_id(credential=None):
    """
    Get the Azure subscription ID, first trying environment variables, 
    then querying available subscriptions if credential is provided
    """
    # Try to get the subscription ID from environment variable
    import os
    subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
    
    # If not found in environment and we have a credential, query Azure for subscriptions
    if not subscription_id and credential:
        try:
            from azure.mgmt.subscription import SubscriptionClient
            
            # Create a subscription client
            sub_client = SubscriptionClient(credential)
            
            # Get the list of subscriptions
            sub_list = list(sub_client.subscriptions.list())
            
            # Use the first available subscription
            if sub_list and len(sub_list) > 0:
                subscription_id = sub_list[0].subscription_id
                print(f"Using subscription: {sub_list[0].display_name} ({subscription_id})")
        except Exception as e:
            print(f"Error getting subscription list: {e}")
    
    return subscription_id

def find_static_asset_path(base_dir, asset_name, asset_types=None):
    """
    Find a static asset in various potential directories within the URL shortener template
    
    Args:
        base_dir: The base directory of the URL shortener
        asset_name: The name of the asset to find (e.g., 'text.png')
        asset_types: List of possible file extensions if the exact asset name is not found
                    (e.g., ['png', 'jpg'] for image assets)
    
    Returns:
        The path to the asset if found, None otherwise
    """
    # List of directories to search in order of preference
    search_dirs = [
        os.path.join(base_dir, 'static', 'img'),
        os.path.join(base_dir, 'static', 'images'),
        os.path.join(base_dir, 'static', 'assets'),
        os.path.join(base_dir, 'static'),
        os.path.join(base_dir, 'assets'),
        os.path.join(base_dir, 'public', 'img'),
        os.path.join(base_dir, 'public', 'images'),
        os.path.join(base_dir, 'public')
    ]
    
    # First, try to find the exact asset name
    for directory in search_dirs:
        if os.path.exists(directory):
            asset_path = os.path.join(directory, asset_name)
            if os.path.exists(asset_path):
                return asset_path
    
    # If the exact asset name is not found, try different extensions if provided
    if asset_types:
        asset_base = os.path.splitext(asset_name)[0]
        for directory in search_dirs:
            if os.path.exists(directory):
                for ext in asset_types:
                    asset_path = os.path.join(directory, f"{asset_base}.{ext}")
                    if os.path.exists(asset_path):
                        return asset_path
    
    # If still not found, search for any file starting with the asset base name
    asset_base = os.path.splitext(asset_name)[0]
    for directory in search_dirs:
        if os.path.exists(directory):
            for file_name in os.listdir(directory):
                if file_name.startswith(asset_base):
                    return os.path.join(directory, file_name)
    
    return None

def create_azure_deployment_zip(zip_path, shortener_dir, temp_dir):
    """
    Create a zip file for Azure deployment with wsgi.py at the root level
    """
    # Create a robust wsgi.py file that will work on Azure
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
logging.info(f"Directory contents: {os.listdir('.')}")

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

    # Write the wsgi.py file to the temporary directory
    root_wsgi_path = os.path.join(temp_dir, "wsgi.py")
    with open(root_wsgi_path, 'w') as f:
        f.write(wsgi_content)
        
    # Copy app.py to the root if it exists in the shortener directory
    root_app_path = None
    shortener_app_path = os.path.join(shortener_dir, "app.py")
    if os.path.exists(shortener_app_path):
        root_app_path = os.path.join(temp_dir, "app.py")
        shutil.copy2(shortener_app_path, root_app_path)
    
    # Create a new zip file
    try:
        os.remove(zip_path)  # Remove existing file if it exists
    except OSError:
        pass
        
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # First add wsgi.py to the root
        zipf.write(root_wsgi_path, arcname="wsgi.py")
        
        # Add app.py to the root if it exists
        if root_app_path:
            zipf.write(root_app_path, arcname="app.py")
        
        # Add requirements.txt to the root if it exists
        req_path = os.path.join(shortener_dir, "requirements.txt")
        if os.path.exists(req_path):
            zipf.write(req_path, arcname="requirements.txt")
            
        # Add .env file to the root if it exists
        env_path = os.path.join(shortener_dir, ".env")
        if os.path.exists(env_path):
            zipf.write(env_path, arcname=".env")
            
        # Add startup.txt to the root if it exists
        startup_path = os.path.join(shortener_dir, "startup.txt") 
        if os.path.exists(startup_path):
            zipf.write(startup_path, arcname="startup.txt")
        
        # Add all other files, preserving the directory structure
        for root, dirs, files in os.walk(shortener_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                # Skip files we already added to the root
                if file in ["wsgi.py", "app.py", "requirements.txt", ".env", "startup.txt"]:
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, shortener_dir)
                
                # Skip hidden files
                if file.startswith('.') and file != '.env':
                    continue
                    
                # Add the file to the zip
                zipf.write(file_path, arcname=rel_path)
    
    print(f"Created Azure deployment zip at {zip_path}")
    return zip_path

# Define app variable for Azure App Service compatibility
application = app

if __name__ == '__main__':
    # Use the PORT environment variable for Azure App Service or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 