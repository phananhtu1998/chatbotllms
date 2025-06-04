# auth_router.py
from fastapi import APIRouter, Depends
from api.controller.controller import auth_controller

auth_router = APIRouter()

@auth_router.get("/health")
async def check_health():
    """
    Endpoint to check if the service is healthy.
    """
    return auth_controller.check_health()
