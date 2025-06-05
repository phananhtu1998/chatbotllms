from typing import Optional, List, Dict, Any
import asyncpg
from ...sql.user import create_user, get_user_by_id, get_user_by_email, update_user, delete_user, list_users

class UserService:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        full_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new user"""
        return await create_user(
            self.pool,
            username,
            email,
            password_hash,
            full_name
        )

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return await get_user_by_id(self.pool, user_id)

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return await get_user_by_email(self.pool, email)

    async def update_user(
        self,
        user_id: int,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Update user information"""
        return await update_user(self.pool, user_id, **kwargs)

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        return await delete_user(self.pool, user_id)

    async def list_users(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List users with pagination"""
        return await list_users(self.pool, limit, offset) 