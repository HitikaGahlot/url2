from main import app

# This is just an entry point file for Azure App Service
# It imports the app from main.py so that Azure can find it
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000) 