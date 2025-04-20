@echo off
echo Starting URL Shortener setup on Azure...

:: Set the correct Python path
set PYTHON_PATH=D:\home\Python39\python.exe
set PIP_PATH=D:\home\Python39\python.exe -m pip

echo Using Python at: %PYTHON_PATH%
%PYTHON_PATH% --version

:: Install required packages
echo Installing dependencies...
%PIP_PATH% install --upgrade pip
%PIP_PATH% install -r requirements.txt
%PIP_PATH% install gunicorn python-dotenv

:: Set environment variables
echo Setting environment variables...
set PYTHONPATH=D:\home\site\wwwroot
set FLASK_APP=main.py

:: Run the application
echo Starting the application...
%PYTHON_PATH% -m gunicorn --bind=0.0.0.0 --timeout 600 main:app 