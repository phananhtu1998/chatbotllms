import asyncpg
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

class AccountQuery:
    @staticmethod
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
        """Create a new account in the database"""
        query = """
        INSERT INTO account (id, number, code, name, email, username, password, salt, status, images, created_at, created_by, is_deleted, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        RETURNING id, number, code, name, email, username, salt, status, images, created_at, created_by, is_deleted, updated_at
        """
        async with pool.acquire() as conn:
            record = await conn.fetchrow(query, id, number, code, name, email, username, password,salt,status,images,created_at, created_by, is_deleted, updated_at)
            return dict(record) if record else None

    @staticmethod
    async def get_account_by_email(
        pool: asyncpg.Pool,
        email: str
    ) -> Optional[Dict[str, Any]]:
        """Get account by email"""
        query = """
        SELECT COUNT(id) as count
        FROM account
        WHERE email = $1 AND is_deleted = false
        """
        async with pool.acquire() as conn:
            record = await conn.fetchrow(query, email)
            return dict(record) if record else None

    @staticmethod
    async def get_account_by_username(
        pool: asyncpg.Pool,
        username: str
    ) -> Optional[Dict[str, Any]]:
        """Get account by username"""
        query = """
        SELECT id, number, code, name, email, username, password, salt, status, images, created_at, created_by, is_deleted, updated_at
        FROM account
        WHERE username = $1 AND is_deleted = false
        """
        async with pool.acquire() as conn:
            record = await conn.fetchrow(query, username)
            return dict(record) if record else None

    @staticmethod
    async def get_account_by_id(
        pool: asyncpg.Pool,
        id: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Exception]]:
        """Get account by ID
        
        Returns:
            Tuple[Optional[Dict[str, Any]], Optional[Exception]]: A tuple containing:
                - First element: Account data as dictionary if found, None if not found
                - Second element: Exception if error occurred, None if successful
        """
        try:
            query = """
            SELECT id, number, code, name, email, username, salt, status, images, created_at, created_by, is_deleted, updated_at
            FROM account
            WHERE id = $1 AND is_deleted = false
            """
            async with pool.acquire() as conn:
                record = await conn.fetchrow(query, id)
                return (dict(record) if record else None, None)
        except Exception as e:
            return None, e