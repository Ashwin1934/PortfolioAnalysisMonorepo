from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import yfinance as yf
import logging
from concurrent.futures import ThreadPoolExecutor
import time
from confluent_kafka import Producer
from db_utils import PostgresDB
from event_bus import AsyncEventBus
import os
import asyncio
import queue
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)
app = FastAPI()

BATCH_SIZE = 2 # Number of tickers per batch, increase later
BATCH_TIMEOUT = 2.0 # Max seconds to wait for batch to fill

# SQL Queries
SQL_QUERIES = {
    "get_all_tickers": """
        SELECT ticker FROM stocks ORDER BY ticker
    """,
    "insert_ticker": """
        INSERT INTO stocks (ticker) VALUES ($1)
        ON CONFLICT (ticker) DO NOTHING
        RETURNING ticker
    """,
    "get_ticker_history": """
        SELECT 
            ticker,
            valuation_growth,
            valuation_sales_growth,
            eps,
            avg_price_target,
            recommendation_key,
            market_price,
            growth_rate,
            sales_growth_rate,
            bond_yield,
            created_at,
            valuation_date
        FROM stock_valuations 
        WHERE ticker = $1
        ORDER BY created_at DESC
    """,
    "insert_valuation": """
        INSERT INTO stock_valuations (
            ticker, valuation_growth, valuation_sales_growth, eps,
            avg_price_target, recommendation_key, market_price,
            growth_rate, sales_growth_rate, bond_yield
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    """,
    "create_table": """
    CREATE TABLE IF NOT EXISTS stock_valuations (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR(10) NOT NULL,
        valuation_growth NUMERIC(15, 2),
        valuation_sales_growth NUMERIC(15, 2),
        eps NUMERIC(15, 4),
        avg_price_target NUMERIC(15, 2),
        recommendation_key VARCHAR(20),
        market_price NUMERIC(15, 2),
        growth_rate NUMERIC(10, 2),
        sales_growth_rate NUMERIC(10, 2),
        bond_yield NUMERIC(10, 4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        valuation_date DATE DEFAULT CURRENT_DATE
    );
    
    CREATE INDEX IF NOT EXISTS idx_ticker ON stock_valuations(ticker);
    CREATE INDEX IF NOT EXISTS idx_created_at ON stock_valuations(created_at DESC);
    """
}

# Global variables for shared resources
producer = None
db = None
event_bus = None
under_valued_stocks = {}
tickers = []  # List to store tickers from database

async def fetch_tickers():
    """Fetch all tickers from the stocks table."""
    global tickers
    try:
        rows = await db.fetch(SQL_QUERIES["get_all_tickers"])
        tickers = [row['ticker'] for row in rows]
        logger.info(f"Loaded {len(tickers)} tickers from database")
    except Exception as e:
        logger.error(f"Error fetching tickers from database: {e}")
        tickers = []

@app.on_event("startup")
async def startup_event():
    global producer, db
    # Initialize Kafka producer
    # producer = Producer({
    #     'bootstrap.servers': 'host.docker.internal:9092',
    #     'acks': 'all',                # Wait for all replicas to acknowledge
    #     'linger.ms': 10,              # Wait up to 10ms to batch messages
    #     'batch.num.messages': 1000,   # Batch up to 1000 messages
    #     'enable.idempotence': True    # Ensure no duplicates
    # })
    # logger.info("Kafka producer initialized")

    # Initialize PostgreSQL connection pool
    db = PostgresDB(
        host="postgres",  # Update these values based on your PostgreSQL configuration
        port=5432,
        user="stock_user",
        password="stonks",  # Use environment variables in production
        database="stockdata"
    )
    await initialize_database()
    event_bus = AsyncEventBus()
    event_bus.subscribe(db_handler) # db_handler consumes from event bus and puts into queue for db insertion
    event_bus.subscribe(valuation_handler) # valuation_handler consumes from event bus and checks for under-valued stocks
    
    # Fetch tickers from database
    await fetch_tickers()
    
    logger.info("App startup complete")

async def initialize_database():
    """Background task to initialize database connection"""
    global db
    try:
        await db.create_pool(min_size=2, max_size=10, max_retries=5, retry_interval=5)

        await create_table_if_not_exists()
        logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

async def create_table_if_not_exists():
    """Create the stock_valuations table if it doesn't exist"""
    create_table_query = SQL_QUERIES["create_table"]
    
    try:
        await db.execute(create_table_query)
        logger.info("Table 'stock_valuations' verified/created successfully")
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    global producer, db
    # Clean up Kafka producer
    if producer:
        producer.flush()
        producer.close()
        logger.info("Kafka producer closed")
    
    # Clean up PostgreSQL connection pool
    if db:
        await db.close_pool()
        logger.info("PostgreSQL connection pool closed")

# Fetch and calculate valuation
def fetch_and_calculate_valuation(ticker, bond_yield, result_queue: queue.Queue, kafka_topic=None):
    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        growth_estimates = stock.growth_estimates
        revenue_estimate = stock.revenue_estimate
        
        ttm_eps = stock_info.get('trailingEps', 'N/A')
        avg_price_target = stock_info.get('targetMeanPrice', 'N/A')
        recommendation_key = stock_info.get('recommendationKey', 'N/A')
        market_price = stock_info.get('regularMarketPrice', 'N/A')  # Add current/last market price
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

        # Send data to Kafka topic
        result = {
            "ticker": ticker,
            "valuation_growth": valuation_growth if g_rate != 'N/A' else None,
            "valuation_sales_growth": valuation_sales_growth if sales_g_rate != 'N/A' else None,
            "eps": ttm_eps,
            "avg_price_target": avg_price_target,
            "recommendation_key": recommendation_key,
            "market_price": market_price,
            "growth_rate": g_rate,
            "sales_growth_rate": sales_g_rate,
            "bond_yield": bond_yield,
        }

        # Add to queue instead of inserting directly
        context = {'queue', result_queue}
        event_bus.publish_from_thread(result, asyncio.get_event_loop(), context)
        logger.info(f"Queued valuation result for {ticker}")

        # # Send to Kafka if topic is provided
        # if kafka_topic:
        #     # Combine ticker and current date as key (e.g., "AAPL-2025-07-01")
        #     key = f"{ticker}-{datetime.date.today().isoformat()}"
        #     producer.produce(kafka_topic, key=key, value=json.dumps(result))
        #     logger.info("Data sent to Kafka topic %s for key %s", kafka_topic, key)

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        logger.error("Error fetching data for %s: %s", ticker, e)


# Function to process all tickers in the background (async/threaded)
async def process_valuations_async(bond_yield, kafka_topic=None):
    """
    Main orchestration function that:
    1. Creates a thread-safe queue
    2. Starts the async consumer task
    3. Uses ThreadPoolExecutor for valuation producers
    4. Waits for completion and cleanup
    
    Args:
        bond_yield (float): Current bond yield for valuation calculations
    """
    
    start_time = time.perf_counter()
    try:
        if not tickers:
            await fetch_tickers()  # Refresh tickers if list is empty

        # Create thread safe queue and stop event
        result_queue = queue.Queue()
        stop_event = asyncio.Event()

        # Start the async consumer task in the event loop
        consumer_task = asyncio.create_task(queue_consumer(result_queue, stop_event))
        
        max_workers = min(os.cpu_count() * 2, 20)  # Cap at 20, TODO tune this based on system

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks for each ticker to the executor
            futures = [
                loop.run_in_executor(
                    executor,
                    fetch_and_calculate_valuation,
                    ticker,
                    bond_yield,
                    result_queue,
                    kafka_topic
                )
                for ticker in tickers
            ]
            # Wait for all producers to complete
            await asyncio.gather(*futures)

        logger.info("All producers finished.")
        #producer.flush()  # Ensure all messages are sent to Kafka ; flush once at the end to ensure all messages are sent

        # Signal the consumer to finish processing remaining items
        stop_event.set()

        # Wait for consumer to finish processing remaining items
        await consumer_task

        elapsed = time.perf_counter() - start_time
        logger.info("Async processing completed in %.2f seconds.", elapsed)
    except Exception as e:
        logger.error("An error occurred: %s", e)

# Endpoint to trigger valuation computation
@app.post("/compute_valuations_async")
async def compute_valuations_async(background_tasks: BackgroundTasks):
    bond_yield = 5.54  # 20-year corporate bond yield
    kafka_topic = "valuation_results"
    
    # Schedule the background task
    background_tasks.add_task(process_valuations_async, bond_yield)
    
    # Return an immediate response
    return {"message": "Async Valuation computation triggered. Results will be printed to the console."}

@app.get("/ticker/{ticker}")
async def get_ticker(ticker: str):
    """
    Get historical valuation data for a specific ticker from PostgreSQL.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., AAPL, MSFT)
        
    Returns:
        dict: A dictionary containing the ticker's historical valuation data
    """
    logger.info(f"Fetching historical data for ticker: {ticker}")
    
    try:
        # Query all records for the given ticker, ordered by creation date
        rows = await db.fetch(SQL_QUERIES["get_ticker_history"], ticker.upper())
        
        if not rows:
            logger.info(f"No historical data found for ticker: {ticker}")
            return {"ticker": ticker, "message": "No historical data found", "valuations": []}
            
        logger.info(f"Found {len(rows)} historical records for ticker: {ticker}")
        return {
            "ticker": ticker,
            "message": f"Found {len(rows)} historical records",
            "valuations": rows
        }
            
    except Exception as e:
        logger.error(f"Error fetching data for ticker {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching data: {str(e)}"
        )
    
@app.get("/undervalued-stocks", response_model=List[Dict[str, any]])
async def get_undervalued_stocks():
    """
    Returns a list of currently undervalued stocks and their valuation details
    """
    return [{"ticker": ticker, **details} for ticker, details in under_valued_stocks.items()]

class TickerRequest(BaseModel):
    tickers: List[str]

@app.post("/tickers")
async def add_tickers(request: TickerRequest):
    """
    Add tickers to the database.
    """
    try:
        # Convert tickers to uppercase and create tuples for insertion
        processed_tickers = [ticker.strip().upper() for ticker in request.tickers]
        ticker_tuples = [(ticker,) for ticker in processed_tickers]
        
        # Insert tickers
        await db.executemany(SQL_QUERIES["insert_ticker"], ticker_tuples)
        return {"message": f"Processed {len(request.tickers)} tickers"}
            
    except Exception as e:
        logger.error(f"Error adding tickers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding tickers: {str(e)}"
        )
    finally:
        # Add new tickers to in-memory list
        for ticker in processed_tickers:
            if ticker not in tickers:
                tickers.append(ticker)

async def queue_consumer(result_queue: queue.Queue, stop_event:asyncio.Event):
    """
    Asynchronous consumer that batches results from the queue and performs batch inserts.
    Runs until stop_event is set AND queue is empty.
    
    Args:
        result_queue (queue.Queue): Thread-safe queue containing valuation results
        stop_event (asyncio.Event): Async event signaling producers have finished
    """
    logger.info("Queue consumer started")
    batch = []
    last_insert_time = time.time()

    while True:
        try:
            # Non blocking get from queue with timeout
            # Check queue in thread safe fashion from async context
            item = await asyncio.get_event_loop().run_in_executor(
                None, 
                result_queue.get,
                True,
                0.5
            )
            batch.append(item)
            result_queue.task_done()

            # Insert batch if it reaches size limit or timeout
            current_time = time.time()
            if (len(batch) >= BATCH_SIZE or (current_time - last_insert_time) >= BATCH_TIMEOUT):
                await batch_insert_valuations(batch)
                batch.clear()
                last_insert_time = current_time
        except queue.Empty:
            # Check if we should stop (producers finished AND queue is empty)
            if stop_event.is_set() and result_queue.empty():
                # Insert remaining valuations in batch
                if batch:
                    await batch_insert_valuations(batch)
                    batch.clear()
                    logger.info(f"Inserted final batch of {len(batch)} records before stopping.")
                break
            current_time = time.time()
            if (batch and (current_time - last_insert_time) >= BATCH_TIMEOUT):
                await batch_insert_valuations(batch)
                batch.clear()
                last_insert_time = current_time
        except Exception as e:
            logger.error(f"Error in queue consumer: {e}")
    logger.info("Queue consumer finished")

async def batch_insert_valuations(batch: List[Dict[str, any]]):
    """
    Perform batch insertion to PostgreSQL using asyncpg's executemany
    
    Args:
        batch (List[Dict[str, any]]): List of valuation records to insert
    """
    if not batch:
        return
    
    try:
        # Prepare data for executemany - list of tuples
        records = [
            (
                item["ticker"],
                item["valuation_growth"],
                item["valuation_sales_growth"],
                item["eps"],
                item["avg_price_target"],
                item["recommendation_key"],
                item["market_price"],
                item["growth_rate"],
                item["sales_growth_rate"],
                item["bond_yield"]
            )
            for item in batch
        ]

        # Use executemany for batch insert
        await db.executemany(SQL_QUERIES["insert_valuation"], records)
        logger.info(f"Batch inserted {len(batch)} records into PostgreSQL")
    except Exception as e:
        logger.error(f"Error during batch insert: {e}")

def db_handler(valuation_result, context):
    """Subscriber function to handle database insertion from event bus"""
    queue = context.get('queue')
    if queue:
        queue.put(valuation_result)

def valuation_handler(valuation_result, context):
    """Subscriber function to handle under-valued checks from event bus"""
    # Example: Check if valuation is under market price
    market_price = valuation_result.get("market_price")
    valuation_growth = valuation_result.get("valuation_growth")
    valuation_sales_growth = valuation_result.get("valuation_sales_growth")
    price_target = valuation_result.get("avg_price_target")
    ticker = valuation_result.get("ticker")

    good_value = False
    great_value = False
    if valuation_growth and market_price and valuation_growth > market_price:
        good_value = True
    if valuation_sales_growth and market_price and valuation_sales_growth > market_price:
        good_value = True
    if good_value and market_price and price_target and price_target > market_price:
        great_value = True
    
    if good_value or great_value:
        under_valued_stocks[ticker] = {
            "rating": "great" if great_value else "good",
            "valuation_growth": valuation_growth,
            "valuation_sales_growth": valuation_sales_growth,
            "market_price": market_price,
            "price_target": price_target,
            "ticker": ticker
        }
        if great_value:
            logger.info(f"Great Value Stock Found: {ticker} | Market Price: {market_price}, Price Target: {price_target}, Valuation (Growth): {valuation_growth}, Valuation (Sales Growth): {valuation_sales_growth}")
        else:
            logger.info(f"Good Value Stock Found: {ticker} | Market Price: {market_price}, Price Target: {price_target}, Valuation (Growth): {valuation_growth}, Valuation (Sales Growth): {valuation_sales_growth}")
    

