from typing import Optional, List, Dict, Any
import asyncpg
from ...sql.account import AccountQuery
from datetime import datetime
import uuid

class AccountService:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_account(
        self,
        number: int,
        code: str,
        name: str,
        email: str,
        username: str,
        password: str,
        salt: str,
        images: str,
        status: bool = True,
        created_by: str = None,
        is_deleted: bool = False,
    ) -> Dict[str, Any]:
        """Create a new account"""
        # Check if user with email already exists
        result = await AccountQuery.get_account_by_email(self.pool, email)
        if result and result.get('count', 0) > 0:
            raise ValueError("Account with this email already exists")
            
        # Generate UUID and current timestamp
        account_id = str(uuid.uuid4())
        current_time = datetime.now()

        # For the first account, created_by will be NULL
        # For subsequent accounts, created_by must reference an existing account
        if created_by is None:
            # Check if this is the first account
            check_first_account = """
            SELECT COUNT(*) as count FROM account
            """
            async with self.pool.acquire() as conn:
                count = await conn.fetchval(check_first_account)
                if count > 0:
                    raise ValueError("created_by is required for non-first accounts")
        
        return await AccountQuery.create_account(
            self.pool,
            id=account_id,
            number=number,
            code=code,
            name=name,
            email=email,
            username=username,
            password=password,
            salt=salt,
            created_at=current_time,
            updated_at=current_time,
            images=images,
            status=status,
            created_by=created_by,
            is_deleted=is_deleted
        )

    async def get_account_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get account by email"""
        result = await AccountQuery.get_account_by_email(self.pool, email)
        return result.get('count', 0) if result else 0

    