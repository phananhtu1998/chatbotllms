from fastapi import APIRouter, Depends, HTTPException, status, Body
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

# Dependency to get authController instance
async def get_auth_controller():
    postgres = PostgresInitializer()
    pool = await postgres.initialize()
    auth_service = AuthService(pool)
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

