from fastapi import APIRouter, Depends, HTTPException, status, Body, Request, Header
from fastapi.security import HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Any
from api.middleware.auth import AuthMiddleware
from api.service.authentication.auth import AuthService
from api.initialize.postgres import PostgresInitializer
from api.models.login import LoginInput
from ...controller.auth.auth import AuthController

# Create router
auth_router = APIRouter()

# Create auth middleware instance
auth = AuthMiddleware()

async def get_auth_service():
    postgres = PostgresInitializer()
    pool = await postgres.initialize()
    return AuthService(pool)

async def get_auth_controller(auth_service: AuthService = Depends(get_auth_service)):
    return AuthController(auth_service)

@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginInput = Body(..., description="Data for user login"),
    auth_controller: AuthController = Depends(get_auth_controller),
) -> Dict[str, Any]:
    """Authenticate user and return tokens"""
    return await auth_controller.login(
        login_data=login_data
    )

@auth_router.post("/logout", dependencies=[Depends(auth.get_bearer_token)])
async def logout(
    request: Request,
    auth_controller: AuthController = Depends(get_auth_controller),
) -> Dict[str, Any]:
    """Logout user and blacklist their token"""
    return await auth_controller.logout(
        request=request
    )

@auth_router.post("/refresh", dependencies=[Depends(auth.get_bearer_token)])
async def refresh_tokens(
    request: Request,
    refresh_token: str = Header(..., alias="Refresh-Token", description="Refresh token to get new access token"),
    auth_controller: AuthController = Depends(get_auth_controller),
) -> Dict[str, Any]:
    """Refresh access and refresh tokens"""
    return await auth_controller.refresh_tokens(
        request=request,
        refresh_token=refresh_token
    )

