import asyncpg
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

async def create_account(
    pool: asyncpg.Pool,
    id: str,
    number: int,
    code: str,
    name: str,
    email: str,
    username: str,
    password: str,
    salt: str,
    created_at: datetime,
    updated_at: str,
    images: str,
    status: bool = True,
    created_by: str = "",
    is_deleted: bool = False,
) -> Dict[str, Any]:
    """Create a new user in the database"""
    query = """
    INSERT INTO users (id, number, code, name, email, username, password, salt, status, images, created_at, created_by, is_deleted, updated_at)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
    RETURNING id, number, code, name, email, username, salt, status, images, created_at, created_by, is_deleted, updated_at
    """
    async with pool.acquire() as conn:
        record = await conn.fetchrow(query, id, number, code, name, email, username, password,salt,status,images,created_at, created_by, is_deleted, updated_at)
        return dict(record) if record else None
