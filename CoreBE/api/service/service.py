from typing import Optional, List
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
class AuthService:
    def get_health_status(self):
        return {"status": "ok", "message": "Service is healthy"}