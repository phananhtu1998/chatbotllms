from fastapi import APIRouter
import logging
from api.router.user.user_router import user_router

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
                tags=["users"]
            )
            
            logger.info("All routers initialized successfully")
            return self.main_router
            
        except Exception as e:
            logger.error(f"Error initializing routers: {str(e)}")
            raise