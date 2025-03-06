import socket
import yfinance as yf
import json

UDP_IP = "127.0.0.1"  # Server address
UDP_PORT = 5005       # Must match the server's port
MESSAGE = b"Hello, UDP server!"  # Note: UDP transmits bytes
ticker_path = r"C:\Users\ashud\NewProjects\PortfolioAnalysisMonorepo\portfolioTickers"


def process_tickers(path, socket):
    tickers = []
    try:
        with open(path, "r") as file:
            for line in file:
                tickers.append(line.strip())
                ticker = line.strip()
                ticker_info = fetch_raw_data_for_ticker(ticker)
                send_data_to_server(socket=socket, byte_data=ticker_info)

    except FileNotFoundError:
        print("File not found")
    except Exception as e:
        print(f"Error: {e}")


def instantiate_udp_socket():
    # create a UDP socket, as specified by SOCK_DGRAM
    try: 
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return sock
    except:
        print("Error instantiating UDP socket.")


def send_data_to_server(socket, byte_data):
    try:
        socket.sendto(byte_data, (UDP_IP, UDP_PORT))
        print("Sending data to socket.")
    except Exception as e:
        print("Error sending data to socket.")
        print(f"Error: {e}")

def fetch_yahoo_finance_data_for_ticker(ticker):
    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        growth_estimates = stock.growth_estimates
        ttm_eps = stock_info.get('trailingEps', 'N/A')
        avg_price_target = stock_info.get('targetMeanPrice', 'N/A')
        recommendation_key = stock_info.get('recommendationKey', 'N/A')
        close_price = stock_info.get('previousClose', 'N/A')
        one_year_growth_rate = growth_estimates.loc["+1y", "stockTrend"]
        long_term_growth_rate = growth_estimates.loc["LTG", "stockTrend"]

        return {
            "ticker": ticker,
            "ttm_eps": ttm_eps,
            "price_tgt": avg_price_target,
            "price": close_price,
            "1yg": one_year_growth_rate,
            "LTG": long_term_growth_rate
        }
    except Exception as e:
        print(f"Error: {e}")

def fetch_raw_data_for_ticker(ticker):
    try:
        data = fetch_yahoo_finance_data_for_ticker(ticker)
        json_data = json.dumps(data, indent=4)
        byte_data = json_data.encode('utf-8')
        print("Size of " + ticker + " data:", len(byte_data), "bytes")
        return byte_data
    except Exception as e:
        print(f"Error: {e}")

def main():
    
    try:
        socket = instantiate_udp_socket()
        process_tickers(path=ticker_path, socket=socket)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
