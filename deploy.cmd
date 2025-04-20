@echo off
echo Deploying Flask application to Azure App Service...

:: Check if wsgi.py exists
echo Checking for wsgi.py...
if not exist wsgi.py (
    echo ERROR: wsgi.py not found in root directory. Deployment cannot proceed.
    exit /b 1
)

:: Create Python virtual environment
echo Creating Python virtual environment...
D:\home\Python39\python.exe -m venv env
call env\Scripts\activate

:: Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Copy web.config to the deployment folder if not exists
echo Checking for web.config...
if not exist %DEPLOYMENT_TARGET%\web.config (
    echo Copying web.config to deployment folder...
    copy web.config %DEPLOYMENT_TARGET%\web.config
)

:: Copy startup.txt to the deployment folder if not exists
echo Checking for startup.txt...
if not exist %DEPLOYMENT_TARGET%\startup.txt (
    echo Copying startup.txt to deployment folder...
    copy startup.txt %DEPLOYMENT_TARGET%\startup.txt
)

echo Deployment completed! 