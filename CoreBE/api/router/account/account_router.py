from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Any
from api.middleware.auth import get_bearer_token
from api.service.account.account import AccountService
from api.initialize.postgres import PostgresInitializer
from api.models.account_model import CreateAccount
from api.controller.account.account_controller import AccountController

# Create router
account_router = APIRouter()

# Dependency to get AccountController instance
async def get_account_controller():
    postgres = PostgresInitializer()
    pool = await postgres.initialize()
    account_service = AccountService(pool)
    return AccountController(account_service)

@account_router.post("", status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: CreateAccount = Body(..., description="Data for creating a new account"),
    account_controller: AccountController = Depends(get_account_controller),
    auth: HTTPAuthorizationCredentials = Depends(get_bearer_token)
) -> Dict[str, Any]:
    """Create a new account"""
    return await account_controller.create_account(
        account_data=account_data
    )

