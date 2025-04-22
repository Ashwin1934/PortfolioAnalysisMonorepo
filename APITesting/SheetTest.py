import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope for the Google APIs
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Path to your credentials.json file
CREDENTIALS_FILE = 'Config/portfolio-analysis-project-efa0a394cf46.json'

# Authenticate with the Google API
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
client = gspread.authorize(credentials)

# Open the Google Sheet (replace 'Your Spreadsheet Name' with your sheet's name)
SPREADSHEET_NAME = 'StockValuations'
sheet = client.open(SPREADSHEET_NAME).sheet1  # Open the first sheet

# Data to publish
data = [
    ["Name", "Age", "City"],
    ["Alice", 30, "New York"],
    ["Bob", 25, "Los Angeles"],
    ["Charlie", 35, "Chicago"]
]

# Update the sheet with data (starting from the first cell)
sheet.update('A1', data)

print("Data published successfully!")
