# URL Shortener Generator

A web application that generates customized URL shortener code based on user inputs.

## Features

- Customize the name of the URL shortener
- Replace the default logo and favicon with your own images
- Choose between Docker or standalone Python deployment
- Download the customized code as a ZIP file
- Includes detailed deployment instructions

## Requirements

- Python 3.8 or higher
- Flask web framework

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd generator
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Fill out the form with your desired customizations:
   - Enter a name for your URL shortener
   - Upload your custom logo (optional)
   - Upload your custom favicon (optional)
   - Select your preferred deployment option

4. Click "Generate URL Shortener" to download your customized code

5. Follow the deployment instructions included in the downloaded ZIP file

## About the URL Shortener

The generated URL shortener includes the following features:

- URL shortening - converting long URLs into compact, shareable links
- Statistics tracking - collecting data on clicks, browsers, and platforms
- Visualization - displaying click data through interactive charts and graphs
- Export functionality - allowing users to download stats in various formats (JSON, CSV, XLSX)
- API access - enabling programmatic interaction with the service 