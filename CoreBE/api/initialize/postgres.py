import asyncpg
import logging
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class PostgresInitializer:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        
    async def initialize(self) -> asyncpg.Pool:
        """Initialize PostgreSQL connection pool"""
        try:
            # You can modify these connection parameters based on your needs
            self.pool = await asyncpg.create_pool(
                user='admin',
                password='123',
                database='chatbot',
                host='localhost',
                port=5432,
                min_size=5,
                max_size=20
            )
            logger.info("PostgreSQL connection pool initialized successfully")
            return self.pool
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection pool: {str(e)}")
            raise
            
    async def close(self):
        """Close PostgreSQL connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed")

# Global pool instance
_pool: Optional[asyncpg.Pool] = None

async def get_pool() -> asyncpg.Pool:
    """Get or create database connection pool"""
    global _pool
    if _pool is None:
        initializer = PostgresInitializer()
        _pool = await initializer.initialize()
    return _pool

@asynccontextmanager
async def get_db_cursor():
    """Get a database cursor"""
    pool = await get_pool()
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)

async def execute_query(query: str, params: tuple = None):
    """Execute a query without returning results"""
    pool = await get_pool()
    conn = await pool.acquire()
    try:
        await conn.execute(query, *params if params else ())
    finally:
        await pool.release(conn)

async def fetch_all(query: str, params: tuple = None) -> List[Dict[str, Any]]:
    """Execute a query and return all results"""
    pool = await get_pool()
    conn = await pool.acquire()
    try:
        records = await conn.fetch(query, *params if params else ())
        return [dict(record) for record in records]
    finally:
        await pool.release(conn)

async def fetch_one(query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
    """Execute a query and return one result"""
    pool = await get_pool()
    conn = await pool.acquire()
    try:
        record = await conn.fetchrow(query, *params if params else ())
        return dict(record) if record else None
    finally:
        await pool.release(conn)
