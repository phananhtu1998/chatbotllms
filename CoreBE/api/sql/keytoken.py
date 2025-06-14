import asyncpg
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import uuid
import json

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
    async def update_refresh_token(
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

    @staticmethod
    async def delete_key(
        pool: asyncpg.Pool,
        account_id: str
    ) -> bool:
        query = """
        DELETE FROM keytoken
        WHERE account_id = $1
        """
        
        try:
            async with pool.acquire() as conn:
                await conn.execute(query, account_id)
                return True
        except Exception as e:
            print(f"DEBUG: Error deleting key token: {str(e)}")
            return False

    @staticmethod
    async def count_refresh_token_by_account(
        pool: asyncpg.Pool,
        refresh_token: str
    ) -> int:
        query = """
        SELECT COUNT(*) AS total_count 
        FROM keytoken 
        WHERE refresh_token = $1
        """
        
        async with pool.acquire() as conn:
            count = await conn.fetchval(query, refresh_token)
            return count if count is not None else 0

    @staticmethod
    async def count_by_token_and_account(
        pool: asyncpg.Pool,
        account_id: str,
        refresh_token: str
    ) -> int:
        query = """
        SELECT COUNT(*) AS total_count 
        FROM keytoken 
        WHERE account_id = $1 
        AND refresh_tokens_used::jsonb @> $2::jsonb
        """
        
        try:
            async with pool.acquire() as conn:
                count = await conn.fetchval(query, account_id, json.dumps([refresh_token]))
                return count if count is not None else 0
        except Exception as e:
            print(f"DEBUG: Error counting by token and account: {str(e)}")
            return 0

    @staticmethod
    async def update_refresh_token_and_used_tokens(
        pool: asyncpg.Pool,
        account_id: str,
        refresh_token: str
    ) -> bool:
        query = """
        UPDATE keytoken
        SET refresh_token = $1,
            refresh_tokens_used = refresh_tokens_used || $2::jsonb,
            updated_at = CURRENT_TIMESTAMP
        WHERE account_id = $3
        """
        
        try:
            async with pool.acquire() as conn:
                # Get current refresh token before updating
                current_token_query = """
                SELECT refresh_token 
                FROM keytoken 
                WHERE account_id = $1
                """
                current_token = await conn.fetchval(current_token_query, account_id)
                
                if current_token:
                    # Add current token to used tokens list
                    used_tokens = json.dumps([current_token])
                    await conn.execute(query, refresh_token, used_tokens, account_id)
                else:
                    # If no current token, just update the refresh token
                    await conn.execute(query, refresh_token, json.dumps([]), account_id)
                return True
        except Exception as e:
            print(f"DEBUG: Error updating refresh token and used tokens: {str(e)}")
            return False
    