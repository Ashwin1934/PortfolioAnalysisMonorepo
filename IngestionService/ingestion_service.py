from fastapi import FastAPI, BackgroundTasks
from concurrent.futures import ThreadPoolExecutor
import finnhub
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s"
)
logger = logging.getLogger("finnhub_service")

app = FastAPI()

# Globals initialized on startup
executor: ThreadPoolExecutor | None = None
finnhub_client: finnhub.Client | None = None

# File that contains tickers (one per line)
TICKER_FILE = Path("testTickers.txt") # TODO: pull from a central file used by both APIs

# startup event hook that initializes global resources like API client + thread pool
@app.on_event("startup")
def on_startup():
    global executor, finnhub_client
    executor = ThreadPoolExecutor(max_workers=4)
    finnhub_client = finnhub.Client(api_key="YOUR_API_KEY") #TODO add in API Key in a secure way to be used in container
    logger.info("🚀 Executor + Finnhub client initialized")

@app.on_event("shutdown")
def on_shutdown():
    global executor
    if executor:
        executor.shutdown(wait=True)
        logger.info("🛑 Executor shut down")

@app.post("/fetch-news")
def fetch_news(background_tasks: BackgroundTasks):
    """
    Endpoint to fetch news for tickers from file.
    Each request to Finnhub is rate-limited (2s delay).
    """
    global executor, finnhub_client

    if not finnhub_client or not executor:
        logger.error("Service not initialized")
        return {"error": "Service not initialized"}

    if not TICKER_FILE.exists():
        logger.error(f"Ticker file not found: {TICKER_FILE}")
        return {"error": f"Ticker file not found: {TICKER_FILE}"}

    # Load tickers from file
    tickers = [line.strip() for line in TICKER_FILE.read_text().splitlines() if line.strip()]
    logger.info(f"📂 Loaded {len(tickers)} tickers from {TICKER_FILE}")

    # Schedule the background task
    background_tasks.add_task(fetch_and_process_news, tickers)

    return {"status": "submitted", "tickers": tickers}

def fetch_and_process_news(tickers: list[str]):
    """Fetch and process news for each ticker in the background."""
    global executor, finnhub_client
    for i, ticker in enumerate(tickers):
        try:
            # Fetch news (blocking call)
            news = finnhub_client.company_news(
                ticker,
                _from="2025-08-20",
                to="2025-08-27"
            )

            # Conduct processing work in parallel with API fetching. This is by design to meet the rate limit of 60 calls/min
            executor.submit(process_news, ticker, news)
            logger.info(f"✅ Submitted {len(news)} news items for {ticker}")
        except Exception as e:
            logger.error(f"❌ Error fetching news for {ticker}: {e}")

        # Respect 2s delay between API calls, unless it’s the last ticker
        if i < len(tickers) - 1:
            logger.info("⏳ Waiting 2 seconds before next request...")
            time.sleep(2)

def process_news(ticker: str, news: list[dict]):
    """Background work (runs in thread pool)."""
    logger.info(f"Processing {len(news)} headlines for {ticker}")
    time.sleep(1)  # simulate work
    for item in news[:2]:  # just log first 2 headlines
        logger.info(f"{ticker}: {item.get('headline')}")
