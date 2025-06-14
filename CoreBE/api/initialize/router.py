from fastapi import APIRouter
import logging
from api.router.user.user_router import user_router
from api.router.account.account_router import account_router
from api.router.auth.auth_router import auth_router

logger = logging.getLogger(__name__)

class RouterInitializer:
    def __init__(self):
        self.main_router = APIRouter()
    
    def initialize(self):
        """Initialize all API routers"""
        try: 
            self.main_router.include_router(
                user_router,
                prefix="/users",
                tags=["Users"]
            )
            self.main_router.include_router(
                account_router,
                prefix="/accounts",
                tags=["Accounts"]
            )
            self.main_router.include_router(
                auth_router,
                prefix="/auth",
                tags=["Authenticate"]
            )
            
            
            logger.info("All routers initialized successfully")
            return self.main_router
            
        except Exception as e:
            logger.error(f"Error initializing routers: {str(e)}")
            raise