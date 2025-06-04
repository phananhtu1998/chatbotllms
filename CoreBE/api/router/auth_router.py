# auth_router.py
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from api.security.auth import get_bearer_token
from api.controller.controller import auth_controller

auth_router = APIRouter()

@auth_router.get("/health")
async def check_health(token: HTTPAuthorizationCredentials = Depends(get_bearer_token)):
    """
    Endpoint to check if the service is healthy.
    Requires Bearer token authentication.
    """
    return auth_controller.check_health()
