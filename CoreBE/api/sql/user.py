import asyncpg
from typing import Optional, List, Dict, Any, Tuple

class UserQuery:
    @staticmethod
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
            record = await conn.fetchrow(query, username, email, password_hash, full_name)
            return dict(record) if record else None

    @staticmethod
    async def get_user_by_id(
        pool: asyncpg.Pool,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        query = """
        SELECT id, username, email, password_hash, full_name, created_at
        FROM users
        WHERE id = $1
        """
        async with pool.acquire() as conn:
            record = await conn.fetchrow(query, user_id)
            return dict(record) if record else None

    @staticmethod
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
            record = await conn.fetchrow(query, email)
            return dict(record) if record else None

    @staticmethod
    async def update_user(
        pool: asyncpg.Pool,
        user_id: int,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Update user information"""
        if not kwargs:
            return None

        set_clause = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(kwargs.keys()))
        query = f"""
        UPDATE users
        SET {set_clause}
        WHERE id = $1
        RETURNING id, username, email, full_name, created_at
        """
        async with pool.acquire() as conn:
            record = await conn.fetchrow(query, user_id, *kwargs.values())
            return dict(record) if record else None

    @staticmethod
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

    @staticmethod
    async def get_total_users(pool: asyncpg.Pool) -> int:
        """Get total number of users"""
        query = """
        SELECT COUNT(*) as total
        FROM users
        """
        async with pool.acquire() as conn:
            return await conn.fetchval(query)

    @staticmethod
    async def list_users(
        pool: asyncpg.Pool,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List users with pagination"""
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get total count
        total = await UserQuery.get_total_users(pool)
        
        # Get paginated results
        query = """
        SELECT id, username, email, full_name, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT $1 OFFSET $2
        """
        async with pool.acquire() as conn:
            records = await conn.fetch(query, limit, offset)
            return [dict(record) for record in records], total 