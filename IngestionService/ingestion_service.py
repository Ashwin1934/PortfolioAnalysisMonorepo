from fastapi import FastAPI, BackgroundTasks
from concurrent.futures import ThreadPoolExecutor
import finnhub
import time
import logging
import os
import grpc
from datetime import datetime

# Import gRPC generated stubs
# Note: These files should be copied from InferenceService/ to IngestionService/ or shared via volume
try:
    import inference_pb2
    import inference_pb2_grpc
except ImportError as e:
    logger = logging.getLogger("finnhub_service")
    logger.warning(f"Could not import gRPC stubs: {e}. Make sure inference_pb2.py and inference_pb2_grpc.py are available.")

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
inference_stub = None  # gRPC stub for inference service

# Hardcoded tickers for now - TODO: pull from database later
DEFAULT_TICKERS = ["FSLR", "GOOG"]

# startup event hook that initializes global resources like API client + thread pool
@app.on_event("startup")
def on_startup():
    global executor, finnhub_client, inference_stub
    executor = ThreadPoolExecutor(max_workers=4)
    
    # Read API key from env
    API_KEY = os.getenv("FINNHUB_API_KEY")
    if not API_KEY:
        raise RuntimeError("Missing FINNHUB_API_KEY environment variable!")
    finnhub_client = finnhub.Client(api_key=API_KEY)
    logger.info("🚀 Executor + Finnhub client initialized")
    
    # Initialize gRPC client for inference service
    try:
        INFERENCE_SERVICE_HOST = os.getenv("INFERENCE_SERVICE_HOST", "localhost")
        INFERENCE_SERVICE_PORT = os.getenv("INFERENCE_SERVICE_PORT", "50051")
        channel = grpc.insecure_channel(f"{INFERENCE_SERVICE_HOST}:{INFERENCE_SERVICE_PORT}")
        inference_stub = inference_pb2_grpc.InferenceServiceStub(channel)
        logger.info(f"🚀 gRPC client initialized for InferenceService at {INFERENCE_SERVICE_HOST}:{INFERENCE_SERVICE_PORT}")
    except Exception as e:
        logger.warning(f"⚠️ Could not initialize gRPC client: {e}. Inference calls will be skipped.")

@app.on_event("shutdown")
def on_shutdown():
    global executor
    if executor:
        executor.shutdown(wait=True)
        logger.info("🛑 Executor shut down")

@app.post("/fetch-news")
def fetch_news(background_tasks: BackgroundTasks):
    """
    Endpoint to fetch news for tickers.
    Each request to Finnhub is rate-limited (2s delay).
    """
    global executor, finnhub_client

    if not finnhub_client or not executor:
        logger.error("Service not initialized")
        return {"error": "Service not initialized"}

    # Load tickers from hardcoded list (TODO: pull from database)
    tickers = DEFAULT_TICKERS
    logger.info(f"📂 Loaded {len(tickers)} tickers: {tickers}")

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
    """Background work (runs in thread pool). Processes headlines and calls inference service."""
    global inference_stub
    logger.info(f"Processing {len(news)} headlines for {ticker}")
    
    if not inference_stub:
        logger.warning(f"⚠️ Inference stub not available. Skipping inference for {ticker}")
        return
    
    for item in news[:5]:  # Process first 5 headlines
        try:
            headline = item.get('headline', '')
            source = item.get('source', 'unknown')
            timestamp = item.get('datetime', '')
            
            # Create gRPC request
            request = inference_pb2.InferenceRequest(
                headline=headline,
                ticker=ticker,
                source=source,
                timestamp=str(timestamp)
            )
            
            # Make gRPC call to inference service
            response = inference_stub.RunInference(request)
            
            logger.info(
                f"✅ Inference result for {ticker}: "
                f"headline='{headline[:50]}...', "
                f"score={response.score}, "
                f"label={response.label}"
            )
        except grpc.RpcError as e:
            logger.error(f"❌ gRPC error for {ticker}: {e.code()} - {e.details()}")
        except Exception as e:
            logger.error(f"❌ Error processing headline for {ticker}: {e}")
