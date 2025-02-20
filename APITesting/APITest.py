import requests
import yfinance as yf
import json


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

def fetch_yahoo_finance_data():
    
    stock = yf.Ticker("FSLR")
    print(type(stock))
    print('growth estimates')
    print(stock.growth_estimates)
    print('balance sheet')
    print(stock.balance_sheet)
    print('analyst price targets')
    print(stock.analyst_price_targets)
    print(stock.get_analyst_price_targets('mean'))
    print('fast info')
    print(stock.fast_info)
    
    return stock

def fetch_updated_yahoo_finance_data():
    stock = yf.Ticker("FSLR")
    print(type(stock))
    print(stock.info)
    stock_info = stock.info
    ttm_eps = stock_info.get('trailingEps', 'N/A')
    avg_price_target = stock_info.get('targetMeanPrice', 'N/A')
    recommendation_key = stock_info.get('recommendationKey', 'N/A')
    close_price = stock_info.get('previousClose', 'N/A')
    

# Main function
def main():
    api_url = "https://api.polygon.io/v2/reference/news?ticker=AAPL&limit=10&apiKey=K_BzBMJ_P99kHEvLjB2cC8lQuEruCpUE"
    
    
    # Pull data from the API
    try:
        #data = fetch_api_data(api_url)
        #print(data)
        #print(fetch_yahoo_finance_data())
        print(fetch_updated_yahoo_finance_data())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
