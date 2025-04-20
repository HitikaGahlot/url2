@echo off
echo Creating deployment zip file...

:: Check if wsgi.py exists in the root directory
if not exist wsgi.py (
    echo Error: wsgi.py not found in root directory. Make sure it exists before deploying.
    exit /b 1
)

:: Check if 7-Zip is installed
where 7z >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Using 7-Zip to create deployment package...
    7z a -tzip deployment.zip app.py wsgi.py requirements.txt web.config startup.txt static templates
) else (
    echo 7-Zip not found. Using PowerShell to create zip...
    powershell -Command "& {Add-Type -Assembly 'System.IO.Compression.FileSystem'; [System.IO.Compression.ZipFile]::CreateFromDirectory('.', 'deployment.zip', 'Optimal', $false)}"
)

echo Deployment package ready: deployment.zip
echo Upload this file to Azure App Service through the portal or use az webapp deployment 