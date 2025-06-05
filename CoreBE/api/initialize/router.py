from fastapi import APIRouter
import logging
from api.router.auth_router import auth_router
from api.router.user_router import user_router

logger = logging.getLogger(__name__)

class RouterInitializer:
    def __init__(self):
        self.main_router = APIRouter()
    
    def initialize(self):
        """Initialize all API routers"""
        try: 
            # Include routers with prefixes and tags
            self.main_router.include_router(
                auth_router,
                prefix="/check-health",
                tags=["health"]
            )
            
            self.main_router.include_router(
                user_router,
                prefix="/users",
                tags=["users"]
            )
            
            logger.info("All routers initialized successfully")
            return self.main_router
            
        except Exception as e:
            logger.error(f"Error initializing routers: {str(e)}")
            raise