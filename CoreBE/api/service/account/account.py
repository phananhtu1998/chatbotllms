from typing import Optional, List, Dict, Any
import asyncpg
from ...sql.account import create_account
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
        created_by: str = "",
        is_deleted: bool = False,
    ) -> Dict[str, Any]:
        """Create a new account"""
        # Check if user with email already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError("Account with this email already exists")
            
        # Generate UUID and current timestamp
        account_id = uuid.uuid4().hex
        current_time = datetime.now()
        
        return await create_account(
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
            updated_at=current_time.isoformat(),
            images=images,
            status=status,
            created_by=created_by,
            is_deleted=is_deleted
        )

    