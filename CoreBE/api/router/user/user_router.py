from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Any
from api.middleware.auth import get_api_key_or_bearer
from api.controller.user.controller import UserController
from api.service.user.service import UserService
from api.initialize.postgres import PostgresInitializer

# Create router
user_router = APIRouter()

# Dependency to get UserController instance
async def get_user_controller():
    postgres = PostgresInitializer()
    pool = await postgres.initialize()
    user_service = UserService(pool)
    return UserController(user_service)

@user_router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    username: str,
    email: str,
    password_hash: str,
    full_name: Optional[str] = None,
    user_controller: UserController = Depends(get_user_controller),
    auth: HTTPAuthorizationCredentials = Depends(get_api_key_or_bearer)
) -> Dict[str, Any]:
    """Create a new user"""
    return await user_controller.create_user(
        username=username,
        email=email,
        password_hash=password_hash,
        full_name=full_name
    )

@user_router.get("/{user_id}")
async def get_user(
    user_id: int,
    user_controller: UserController = Depends(get_user_controller),
    auth: HTTPAuthorizationCredentials = Depends(get_api_key_or_bearer)
) -> Dict[str, Any]:
    """Get user by ID"""
    return await user_controller.get_user(user_id)

@user_router.get("/email/{email}")
async def get_user_by_email(
    email: str,
    user_controller: UserController = Depends(get_user_controller),
    auth: HTTPAuthorizationCredentials = Depends(get_api_key_or_bearer)
) -> Dict[str, Any]:
    """Get user by email"""
    return await user_controller.get_user_by_email(email)

@user_router.patch("/{user_id}")
async def update_user(
    user_id: int,
    username: Optional[str] = None,
    email: Optional[str] = None,
    password_hash: Optional[str] = None,
    full_name: Optional[str] = None,
    user_controller: UserController = Depends(get_user_controller),
    auth: HTTPAuthorizationCredentials = Depends(get_api_key_or_bearer)
) -> Dict[str, Any]:
    """Update user information"""
    update_data = {}
    if username is not None:
        update_data['username'] = username
    if email is not None:
        update_data['email'] = email
    if password_hash is not None:
        update_data['password_hash'] = password_hash
    if full_name is not None:
        update_data['full_name'] = full_name
    
    return await user_controller.update_user(user_id, **update_data)

@user_router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    user_controller: UserController = Depends(get_user_controller),
    auth: HTTPAuthorizationCredentials = Depends(get_api_key_or_bearer)
) -> Dict[str, bool]:
    """Delete a user"""
    success = await user_controller.delete_user(user_id)
    return {"success": success}

@user_router.get("")
async def list_users(
    page: int = 1,
    limit: int = 10,
    user_controller: UserController = Depends(get_user_controller),
    auth: HTTPAuthorizationCredentials = Depends(get_api_key_or_bearer)
) -> Dict[str, Any]:
    """List users with pagination"""
    return await user_controller.list_users(page, limit) 