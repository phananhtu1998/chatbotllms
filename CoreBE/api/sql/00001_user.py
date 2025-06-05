import asyncpg
from typing import Optional, List, Dict, Any

async def create_user(
    pool: asyncpg.Pool,
    username: str,
    email: str,
    password_hash: str,
    full_name: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new user in the database"""
    query = """
    INSERT INTO users (username, email, password_hash, full_name)
    VALUES ($1, $2, $3, $4)
    RETURNING id, username, email, full_name, created_at
    """
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, username, email, password_hash, full_name)

async def get_user_by_id(
    pool: asyncpg.Pool,
    user_id: int
) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    query = """
    SELECT id, username, email, full_name, created_at
    FROM users
    WHERE id = $1
    """
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, user_id)

async def get_user_by_email(
    pool: asyncpg.Pool,
    email: str
) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    query = """
    SELECT id, username, email, password_hash, full_name, created_at
    FROM users
    WHERE email = $1
    """
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, email)

async def update_user(
    pool: asyncpg.Pool,
    user_id: int,
    **kwargs
) -> Optional[Dict[str, Any]]:
    """Update user information"""
    allowed_fields = {'username', 'email', 'password_hash', 'full_name'}
    update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not update_fields:
        return None
        
    set_clause = ', '.join(f"{k} = ${i+2}" for i, k in enumerate(update_fields.keys()))
    query = f"""
    UPDATE users
    SET {set_clause}
    WHERE id = $1
    RETURNING id, username, email, full_name, created_at
    """
    
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, user_id, *update_fields.values())

async def delete_user(
    pool: asyncpg.Pool,
    user_id: int
) -> bool:
    """Delete a user"""
    query = """
    DELETE FROM users
    WHERE id = $1
    """
    async with pool.acquire() as conn:
        result = await conn.execute(query, user_id)
        return result == "DELETE 1"

async def list_users(
    pool: asyncpg.Pool,
    limit: int = 10,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """List users with pagination"""
    query = """
    SELECT id, username, email, full_name, created_at
    FROM users
    ORDER BY created_at DESC
    LIMIT $1 OFFSET $2
    """
    async with pool.acquire() as conn:
        return await conn.fetch(query, limit, offset)
