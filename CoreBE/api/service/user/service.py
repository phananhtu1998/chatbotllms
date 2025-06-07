from typing import Optional, List, Dict, Any, Tuple
import asyncpg
from ...sql.user import UserQuery

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
        # Check if user with email already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
            
        return await UserQuery.create_user(
            self.pool,
            username,
            email,
            password_hash,
            full_name
        )

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return await UserQuery.get_user_by_id(self.pool, user_id)

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return await UserQuery.get_user_by_email(self.pool, email)

    async def update_user(
        self,
        user_id: int,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Update user information"""
        return await UserQuery.update_user(self.pool, user_id, **kwargs)

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        return await UserQuery.delete_user(self.pool, user_id)

    async def list_users(
        self,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List users with pagination"""
        return await UserQuery.list_users(self.pool, page, limit) 