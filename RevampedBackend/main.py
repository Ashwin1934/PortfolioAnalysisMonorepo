from fastapi import FastAPI, HTTPException, BackgroundTasks
import yfinance as yf
import logging
from concurrent.futures import ThreadPoolExecutor
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)
app = FastAPI()

# Fetch and calculate valuation
def fetch_and_calculate_valuation(ticker, bond_yield):
    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        growth_estimates = stock.growth_estimates
        revenue_estimate = stock.revenue_estimate
        
        ttm_eps = stock_info.get('trailingEps', 'N/A')
        one_year_growth_rate = growth_estimates.loc["+1y", "stockTrend"] if "+1y" in growth_estimates.index else 'N/A'
        one_year_sales_growth_rate = revenue_estimate.loc["+1y", "growth"] if "+1y" in revenue_estimate.index else 'N/A' # use sales growth as an alternate growth rate

        if ttm_eps == 'N/A' or one_year_growth_rate == 'N/A':
            logger.info("Insufficient data for %s", ticker)
            return


        # Multiply growth rates by 100 if they are not 'N/A'
        g_rate = one_year_growth_rate * 100 if one_year_growth_rate != 'N/A' else 'N/A'
        sales_g_rate = one_year_sales_growth_rate * 100 if one_year_sales_growth_rate != 'N/A' else 'N/A'

        # Log all information used in the valuation
        logger.info(
            "Valuation inputs for %s - EPS: %s, 1Y Growth Rate: %s, 1Y Sales Growth Rate: %s, Bond Yield: %s",
            ticker, ttm_eps, g_rate, sales_g_rate, bond_yield
        )

        # Ben Graham's formula: Valuation = (EPS * (7 + 1.5 * g) * 4.4) / Y
        if g_rate != 'N/A':
            valuation_growth = (ttm_eps * (7 + 1.5 * g_rate) * 4.4) / bond_yield
            logger.info("Ticker: %s, Valuation (Growth Rate): %.2f", ticker, valuation_growth)
        else:
            logger.info("Ticker: %s, Valuation (Growth Rate): N/A", ticker)

        if sales_g_rate != 'N/A':
            valuation_sales_growth = (ttm_eps * (7 + 1.5 * sales_g_rate) * 4.4) / bond_yield
            logger.info("Ticker: %s, Valuation (Sales Growth Rate): %.2f", ticker, valuation_sales_growth)
        else:
            logger.info("Ticker: %s, Valuation (Sales Growth Rate): N/A", ticker)

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        logger.error("Error fetching data for %s: %s", ticker, e)

# Function to process all tickers in the background (sequential)
def process_valuations(bond_yield, file_path="tickers.txt"):
    start_time = time.perf_counter()
    try:
        with open(file_path, 'r') as file:
            tickers = [line.strip() for line in file.readlines()]
        
        for ticker in tickers:
            fetch_and_calculate_valuation(ticker, bond_yield)
        elapsed = time.perf_counter() - start_time
        logger.info("Sequential processing completed in %.2f seconds.", elapsed)
    
    except FileNotFoundError:
        logger.error("File not found: %s", file_path)
    except Exception as e:
        logger.error("An error occurred: %s", e)

# Endpoint to trigger valuation computation
@app.post("/compute_valuations")
async def compute_valuations(background_tasks: BackgroundTasks):
    bond_yield = 5.54  # 20-year corporate bond yield
    ticker_path = r"C:\Users\ashud\NewProjects\PortfolioAnalysisMonorepo\portfolioTickersFull"
    path = "testTickers.txt"
    
    # Schedule the background task
    background_tasks.add_task(process_valuations, bond_yield, path)
    
    # Return an immediate response
    return {"message": "Valuation computation triggered. Results will be printed to the console."}

# Function to process all tickers in the background (async/threaded)
def process_valuations_async(bond_yield, file_path="tickers.txt"):
    start_time = time.perf_counter()
    try:
        with open(file_path, 'r') as file:
            tickers = [line.strip() for line in file.readlines()]
        
        with ThreadPoolExecutor() as executor:
            # Submit tasks for each ticker to the executor
            futures = [executor.submit(fetch_and_calculate_valuation, ticker, bond_yield) for ticker in tickers]
            
            # Wait for all futures to complete
            for future in futures:
                future.result()
        elapsed = time.perf_counter() - start_time
        logger.info("Async processing completed in %.2f seconds.", elapsed)
    
    except FileNotFoundError:
        logger.error("File not found: %s", file_path)
    except Exception as e:
        logger.error("An error occurred: %s", e)

# Endpoint to trigger valuation computation
@app.post("/compute_valuations_async")
async def compute_valuations_async(background_tasks: BackgroundTasks):
    bond_yield = 5.54  # 20-year corporate bond yield
    ticker_path = r"C:\Users\ashud\NewProjects\PortfolioAnalysisMonorepo\portfolioTickersFull"
    path = "testTickers.txt"
    
    # Schedule the background task
    background_tasks.add_task(process_valuations_async, bond_yield, path)
    
    # Return an immediate response
    return {"message": "Async Valuation computation triggered. Results will be printed to the console."}

