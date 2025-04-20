#!/bin/bash

# Ensure wsgi.py is in the correct location
if [ ! -f "wsgi.py" ]; then
    echo "Error: wsgi.py not found in root directory. Make sure it exists before deploying."
    exit 1
fi

# Create deployment zip
echo "Creating deployment zip file..."
zip -r deployment.zip app.py wsgi.py requirements.txt web.config startup.txt static/ templates/

echo "Deployment package ready: deployment.zip"
echo "Upload this file to Azure App Service through the portal or use az webapp deployment source config-zip" 