from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Any
from api.middleware.auth import get_bearer_token
from api.controller.user.controller import AccountController
from api.service.user.service import UserService
from api.initialize.postgres import PostgresInitializer
from api.models.account_model import AccountCreateRequest

# Create router
account_router = APIRouter()

# Dependency to get UserController instance
async def get_account_controller():
    postgres = PostgresInitializer()
    pool = await postgres.initialize()
    account_service = UserService(pool)
    return AccountController(account_service)

@account_router.post("", status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreateRequest = Body(..., description="Data for creating a new account"),
    account_controller: AccountController = Depends(get_account_controller),
    auth: HTTPAuthorizationCredentials = Depends(get_bearer_token)
) -> Dict[str, Any]:
    """Create a new account"""
    return await account_controller.create_account(
        account_data=account_data
    )

