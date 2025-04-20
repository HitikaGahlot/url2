import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('azure-setup.log')
    ]
)

def run_command(cmd):
    """Run a command and log output"""
    logging.info(f"Running command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        logging.info(f"Command output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with error: {e}")
        logging.error(f"Error output: {e.stderr}")
        return False

def setup_azure():
    """Setup the Python environment on Azure"""
    logging.info("Starting Azure setup script")
    
    # Log system info
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Current directory: {os.getcwd()}")
    logging.info(f"Directory contents: {os.listdir('.')}")
    
    # Check for different Python paths on Azure
    python_paths = [
        "D:\\home\\Python39\\python.exe",
        "D:\\home\\Python310\\python.exe",
        "D:\\home\\Python311\\python.exe",
        "D:\\Python39\\python.exe",
        "%HOME%\\Python39\\python.exe",
        "python3.9",
        "python3"
    ]
    
    python_path = None
    for path in python_paths:
        cmd = f"{path} --version"
        try:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            logging.info(f"Found Python at {path}: {result.stdout.strip()}")
            python_path = path
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            logging.info(f"Python not found at {path}")
    
    if not python_path:
        logging.error("Could not find Python 3.9 or later on the system")
        return False
    
    # Install dependencies
    logging.info("Installing dependencies")
    run_command(f"{python_path} -m pip install --upgrade pip")
    run_command(f"{python_path} -m pip install -r requirements.txt")
    run_command(f"{python_path} -m pip install gunicorn python-dotenv")
    
    # Create startup command
    startup_command = f"{python_path} -m gunicorn --bind=0.0.0.0 --timeout 600 main:app"
    logging.info(f"Recommended startup command: {startup_command}")
    
    # Write the startup command to a file
    with open("startup.txt", "w") as f:
        f.write(startup_command)
    
    logging.info("Azure setup completed successfully")
    return True

if __name__ == "__main__":
    setup_azure() 