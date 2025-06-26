from fastapi import FastAPI, HTTPException, BackgroundTasks
import yfinance as yf

app = FastAPI()

# Fetch and calculate valuation
def fetch_and_calculate_valuation(ticker, bond_yield):
    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        growth_estimates = stock.growth_estimates
        
        ttm_eps = stock_info.get('trailingEps', 'N/A')
        one_year_growth_rate = growth_estimates.loc["+1y", "stockTrend"] if "+1y" in growth_estimates.index else 'N/A'

        if ttm_eps == 'N/A' or one_year_growth_rate == 'N/A':
            print(f"Insufficient data for {ticker}")
            return

        # Ben Graham's formula: Valuation = (EPS * (7 + 1.5 * g) * 4.4) / Y
        valuation = (ttm_eps * (7 + 1.5 * one_year_growth_rate) * 4.4) / bond_yield
        print(f"Ticker: {ticker}, Valuation: {valuation:.2f}")

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")

# Function to process all tickers in the background
def process_valuations(bond_yield, file_path="tickers.txt"):
    try:
        with open(file_path, 'r') as file:
            tickers = [line.strip() for line in file.readlines()]
        
        for ticker in tickers:
            fetch_and_calculate_valuation(ticker, bond_yield)
    
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Endpoint to trigger valuation computation
@app.post("/compute_valuations")
async def compute_valuations(background_tasks: BackgroundTasks):
    bond_yield = 5.54  # 20-year corporate bond yield
    ticker_path = r"C:\Users\ashud\NewProjects\PortfolioAnalysisMonorepo\portfolioTickersFull"
    
    # Schedule the background task
    background_tasks.add_task(process_valuations, bond_yield, ticker_path)
    
    # Return an immediate response
    return {"message": "Valuation computation triggered. Results will be printed to the console."}

