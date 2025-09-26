"""
Database utilities for PostgreSQL connection management and query execution.

Connection Pool Overview:
-----------------------
A connection pool is a cache of database connections that are maintained so that the 
connections can be reused when needed. This provides several benefits:

1. Performance: Creating new database connections is expensive as it requires:
   - TCP three-way handshake (SYN, SYN-ACK, ACK)
   - Authentication with the database
   - Session setup and initialization
   By reusing existing connections, we avoid this overhead.

2. Resource Management:
   - Limits maximum number of concurrent database connections
   - Prevents database server overload
   - Manages connection lifecycle automatically

TCP Connection Details:
---------------------
Each database connection in the pool represents a full TCP connection to PostgreSQL:
- Default PostgreSQL port: 5432
- Connection establishment requires full TCP handshake
- Connections are kept alive rather than being closed/reopened
- Visible using 'netstat -an | findstr 5432' on Windows

Pool Configuration:
-----------------
min_size: Minimum number of TCP connections kept alive
max_size: Maximum number of TCP connections allowed
Each connection is a persistent TCP socket to PostgreSQL

Architecture:
-----------
This implementation uses asyncpg which leverages async/await for non-blocking I/O
operations. Instead of using multiple threads, it uses an event loop to handle
multiple connections efficiently.
"""

import asyncpg
from typing import List, Dict, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

class PostgresDB:
    def __init__(self, dsn: str = None, **kwargs):
        """Initialize the PostgresDB class.
        
        Args:
            dsn (str, optional): Database connection string. If not provided, kwargs will be used.
            **kwargs: Connection parameters (host, port, user, password, database)
        """
        self.dsn = dsn
        self.conn_params = kwargs if not dsn else None
        self._pool = None

    async def create_pool(self, min_size: int = 2, max_size: int = 10):
        """Create a connection pool.
        
        Args:
            min_size (int): Minimum number of connections in the pool
            max_size (int): Maximum number of connections in the pool
        """
        try:
            if self.dsn:
                self._pool = await asyncpg.create_pool(
                    dsn=self.dsn,
                    min_size=min_size,
                    max_size=max_size
                )
            else:
                self._pool = await asyncpg.create_pool(
                    **self.conn_params,
                    min_size=min_size,
                    max_size=max_size
                )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Error creating connection pool: {e}")
            raise

    async def close_pool(self):
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("Database connection pool closed")

    async def execute(self, query: str, *args) -> str:
        """Execute a single query.
        
        Args:
            query (str): SQL query to execute
            *args: Query parameters
            
        Returns:
            str: Status of the execution
        """
        if not self._pool:
            raise RuntimeError("Connection pool not initialized. Call create_pool() first.")
        
        try:
            async with self._pool.acquire() as conn:
                result = await conn.execute(query, *args)
                logger.info(f"Query executed successfully: {query}")
                return result
        except Exception as e:
            logger.error(f"Error executing query {query}: {e}")
            raise

    async def executemany(self, query: str, args_list: List[tuple]) -> str:
        """Execute a query with multiple sets of parameters.
        
        Args:
            query (str): SQL query to execute
            args_list (List[tuple]): List of parameter tuples
            
        Returns:
            str: Status of the execution
        """
        if not self._pool:
            raise RuntimeError("Connection pool not initialized. Call create_pool() first.")
        
        try:
            async with self._pool.acquire() as conn:
                # Start a transaction
                async with conn.transaction():
                    result = await conn.executemany(query, args_list)
                    logger.info(f"Batch query executed successfully with {len(args_list)} items")
                    return result
        except Exception as e:
            logger.error(f"Error executing batch query {query}: {e}")
            raise

    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        """Fetch rows from the database.
        
        Args:
            query (str): SQL query to execute
            *args: Query parameters
            
        Returns:
            List[Dict[str, Any]]: List of rows as dictionaries
        """
        if not self._pool:
            raise RuntimeError("Connection pool not initialized. Call create_pool() first.")
        
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching data with query {query}: {e}")
            raise