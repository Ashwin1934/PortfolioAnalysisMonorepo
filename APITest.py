import requests


def delivery_report(err, msg):
    """Callback for delivery reports."""
    if err is not None:
        print(f"Delivery failed for message {msg.key()}: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Function to fetch data from API
def fetch_api_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Main function
def main():
    api_url = "https://api.polygon.io/v2/reference/news?ticker=AAPL&limit=10&apiKey=K_BzBMJ_P99kHEvLjB2cC8lQuEruCpUE"
    
    
    # Pull data from the API
    try:
        data = fetch_api_data(api_url)
        print(data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
