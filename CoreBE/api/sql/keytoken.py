import asyncpg
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import uuid

class KeyTokenQuery:
    @staticmethod
    async def count_by_account(
        pool: asyncpg.Pool,
        account_id: str,
    ) -> int:
        query = """
        SELECT COUNT(*) AS total_count 
        FROM keytoken 
        WHERE account_id = $1
        """
        
        async with pool.acquire() as conn:
            count = await conn.fetchval(query, account_id)
            return count if count is not None else 0
        
    @staticmethod
    async def update_refresh_token_and_used_tokens(
        pool: asyncpg.Pool,
        account_id: str,
        refresh_token: str
    ) -> bool:
        query = """
        UPDATE keytoken
        SET refresh_token = $1,
            updated_at = CURRENT_TIMESTAMP
        WHERE account_id = $2
        """
        
        try:
            async with pool.acquire() as conn:
                await conn.execute(query, refresh_token, account_id)
                return True
        except Exception as e:
            print(f"DEBUG: Error updating refresh token: {str(e)}")
            return False

    @staticmethod
    async def insert_key(
        pool: asyncpg.Pool,
        refresh_token: str,
        account_id: str
    ) -> bool:
        query = """
        INSERT INTO keytoken (
            id,
            account_id,
            refresh_token,
            refresh_tokens_used,
            created_at,
            updated_at
        ) VALUES (
            $1,
            $2,
            $3,
            '[]'::jsonb,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        """
        
        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    query,
                    str(uuid.uuid4()),  # Generate new UUID for id
                    account_id,
                    refresh_token
                )
                return True
        except Exception as e:
            print(f"DEBUG: Error inserting key token: {str(e)}")
            return False
    