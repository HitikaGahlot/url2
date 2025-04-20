@echo off
echo Creating a fixed Azure deployment package...

:: Check if a zip file is provided
if "%~1"=="" (
    echo Please provide a path to your existing zip file
    echo Usage: fix_azure_deploy.bat path_to_zip_file.zip
    exit /b 1
)

:: Check if the file exists
if not exist "%~1" (
    echo File %~1 does not exist
    exit /b 1
)

:: Create a temp directory
echo Creating temporary directory...
set TEMP_DIR=%TEMP%\azure_fix_%RANDOM%
mkdir "%TEMP_DIR%"

:: Extract the zip
echo Extracting zip to temporary directory...
powershell -Command "Expand-Archive -Path '%~1' -DestinationPath '%TEMP_DIR%' -Force"

:: Create proper wsgi.py at the root
echo Creating wsgi.py at the root...
echo import os > "%TEMP_DIR%\wsgi.py"
echo import logging >> "%TEMP_DIR%\wsgi.py"
echo import sys >> "%TEMP_DIR%\wsgi.py"
echo. >> "%TEMP_DIR%\wsgi.py"
echo # Configure logging for debugging >> "%TEMP_DIR%\wsgi.py"
echo logging.basicConfig( >> "%TEMP_DIR%\wsgi.py"
echo     level=logging.INFO, >> "%TEMP_DIR%\wsgi.py"
echo     format='%%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s', >> "%TEMP_DIR%\wsgi.py"
echo     handlers=[logging.StreamHandler(), logging.FileHandler('wsgi.log')] >> "%TEMP_DIR%\wsgi.py"
echo ) >> "%TEMP_DIR%\wsgi.py"
echo. >> "%TEMP_DIR%\wsgi.py"
echo logging.info("Starting wsgi.py") >> "%TEMP_DIR%\wsgi.py"
echo logging.info(f"Python version: {sys.version}") >> "%TEMP_DIR%\wsgi.py"
echo logging.info(f"Current directory: {os.getcwd()}") >> "%TEMP_DIR%\wsgi.py"
echo try: >> "%TEMP_DIR%\wsgi.py"
echo     logging.info(f"Directory contents: {os.listdir('.')}") >> "%TEMP_DIR%\wsgi.py"
echo except Exception as e: >> "%TEMP_DIR%\wsgi.py"
echo     logging.error(f"Error listing directory: {e}") >> "%TEMP_DIR%\wsgi.py"
echo. >> "%TEMP_DIR%\wsgi.py"
echo try: >> "%TEMP_DIR%\wsgi.py"
echo     # Try to import app from app.py >> "%TEMP_DIR%\wsgi.py"
echo     from app import app >> "%TEMP_DIR%\wsgi.py"
echo     logging.info("Successfully imported app from app.py") >> "%TEMP_DIR%\wsgi.py"
echo except ImportError as e: >> "%TEMP_DIR%\wsgi.py"
echo     logging.error(f"Error importing from app: {e}") >> "%TEMP_DIR%\wsgi.py"
echo     >> "%TEMP_DIR%\wsgi.py"
echo     # Try to look for app.py in subdirectories >> "%TEMP_DIR%\wsgi.py"
echo     for subdir in [d for d in os.listdir('.') if os.path.isdir(d)]: >> "%TEMP_DIR%\wsgi.py"
echo         sys.path.insert(0, os.path.abspath(subdir)) >> "%TEMP_DIR%\wsgi.py"
echo         try: >> "%TEMP_DIR%\wsgi.py"
echo             from app import app >> "%TEMP_DIR%\wsgi.py"
echo             logging.info(f"Found app in subdirectory: {subdir}") >> "%TEMP_DIR%\wsgi.py"
echo             break >> "%TEMP_DIR%\wsgi.py"
echo         except ImportError: >> "%TEMP_DIR%\wsgi.py"
echo             sys.path.pop(0) >> "%TEMP_DIR%\wsgi.py"
echo             continue >> "%TEMP_DIR%\wsgi.py"
echo     else: >> "%TEMP_DIR%\wsgi.py"
echo         # If we still can't find it, create a simple fallback app >> "%TEMP_DIR%\wsgi.py"
echo         try: >> "%TEMP_DIR%\wsgi.py"
echo             from flask import Flask >> "%TEMP_DIR%\wsgi.py"
echo             app = Flask(__name__) >> "%TEMP_DIR%\wsgi.py"
echo             >> "%TEMP_DIR%\wsgi.py"
echo             @app.route('/') >> "%TEMP_DIR%\wsgi.py"
echo             def index(): >> "%TEMP_DIR%\wsgi.py"
echo                 return "URL Shortener - wsgi.py fallback route" >> "%TEMP_DIR%\wsgi.py"
echo             >> "%TEMP_DIR%\wsgi.py"
echo             logging.info("Created fallback Flask app in wsgi.py") >> "%TEMP_DIR%\wsgi.py"
echo         except Exception as flask_error: >> "%TEMP_DIR%\wsgi.py"
echo             logging.error(f"Error creating fallback Flask app: {flask_error}") >> "%TEMP_DIR%\wsgi.py"
echo             raise >> "%TEMP_DIR%\wsgi.py"
echo. >> "%TEMP_DIR%\wsgi.py"
echo # Main application variable for WSGI compatibility >> "%TEMP_DIR%\wsgi.py"
echo application = app >> "%TEMP_DIR%\wsgi.py"
echo. >> "%TEMP_DIR%\wsgi.py"
echo if __name__ == "__main__": >> "%TEMP_DIR%\wsgi.py"
echo     # Get port from environment or default to 8000 >> "%TEMP_DIR%\wsgi.py"
echo     port = int(os.environ.get("PORT", 8000)) >> "%TEMP_DIR%\wsgi.py"
echo     logging.info(f"Starting Flask app on port {port}") >> "%TEMP_DIR%\wsgi.py"
echo     app.run(host="0.0.0.0", port=port) >> "%TEMP_DIR%\wsgi.py"

:: Create fixed zip file (use original name with _fixed suffix)
set FIXED_ZIP=%~dp1%~n1_fixed.zip
echo Creating fixed zip file: %FIXED_ZIP%

:: Check if 7-Zip is installed
where 7z >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Using 7-Zip to create fixed package...
    7z a -tzip "%FIXED_ZIP%" "%TEMP_DIR%\*"
) else (
    echo Using PowerShell to create fixed package...
    powershell -Command "& {Add-Type -Assembly 'System.IO.Compression.FileSystem'; [System.IO.Compression.ZipFile]::CreateFromDirectory('%TEMP_DIR%', '%FIXED_ZIP%', 'Optimal', $false)}"
)

:: Clean up
echo Cleaning up temporary files...
rmdir /s /q "%TEMP_DIR%"

echo Fixed Azure deployment package created: %FIXED_ZIP%
echo Use this file to deploy to Azure instead of the original package.
echo. 