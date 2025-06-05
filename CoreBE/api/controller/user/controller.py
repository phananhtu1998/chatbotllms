from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any
from api.service.user.service import UserService
from api.middleware.auth import get_api_key_or_bearer
from api.utils.response import create_response, create_paginated_response

class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        full_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new user"""
        try:
            # Check if user with email already exists
            existing_user = await self.user_service.get_user_by_email(email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
            
            user = await self.user_service.create_user(
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=full_name
            )
            return create_response(
                status_code=status.HTTP_201_CREATED,
                message="User created successfully",
                data=user
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID"""
        try:
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return create_response(
                message="User retrieved successfully",
                data=user
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get user by email"""
        try:
            user = await self.user_service.get_user_by_email(email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return create_response(
                message="User retrieved successfully",
                data=user
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def update_user(
        self,
        user_id: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Update user information"""
        try:
            # Check if user exists
            existing_user = await self.user_service.get_user_by_id(user_id)
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            # If email is being updated, check if new email is already taken
            if 'email' in kwargs:
                email_user = await self.user_service.get_user_by_email(kwargs['email'])
                if email_user and email_user['id'] != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already taken"
                    )

            updated_user = await self.user_service.update_user(user_id, **kwargs)
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No valid fields to update"
                )
            return create_response(
                message="User updated successfully",
                data=updated_user
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Delete a user"""
        try:
            # Check if user exists
            existing_user = await self.user_service.get_user_by_id(user_id)
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            success = await self.user_service.delete_user(user_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete user"
                )
            return create_response(
                message="User deleted successfully",
                data={"success": success}
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def list_users(
        self,
        page: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """List users with pagination"""
        try:
            if limit < 1 or limit > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Limit must be between 1 and 100"
                )
            if page < 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Page must be greater than 0"
                )
            
            users, total = await self.user_service.list_users(page, limit)
            return create_paginated_response(
                items=users,
                total=total,
                page=page,
                limit=limit
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            ) 