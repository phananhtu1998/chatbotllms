from typing import Optional, List, Dict, Any
import asyncpg
from ...sql.account import AccountQuery
from datetime import datetime
from ...utils.crypto.crypto import Crypto
from ...utils.utils import TokenGenerator
import uuid
import json
from api.global.global import Global
from ...utils.consts import consts


class AuthService:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def Login(self, username: str, password: str) -> Dict[str, Any]:
        """Login a account"""
        # Check if user with email exists
        item_account = self.get_account_by_username(username)
        if not item_account:
            raise ValueError("Invalid username or password") # Raise a ValueError or a custom exception
        if  not Crypto.matching_password(item_account["password"], password, item_account["salt"]):
            raise ValueError("Does not match password")
        
        if item_account["status"] == False: # Check if user is active
            raise ValueError("Account is Locked")
        subtoken = TokenGenerator(item_account["number"])
        infoAccount, err = AccountQuery.get_account_by_id(self.pool, item_account["id"])
        if err is not None:
            raise ValueError("Lỗi ở phần lấy thông tin tài khoản")
        try:
            infoAccountJson = json.dumps(infoAccount)
        except Exception as e:
            raise ValueError(f"Lỗi khi chuyển đổi thông tin tài khoản sang JSON: {str(e)}")
            
        try:
            await global_instance.redis_client.set(
                subtoken,
                infoAccountJson,
                ex=consts.REFRESH_TOKEN * 3600  # Convert hours to seconds
            )
        except Exception as e:
            raise ValueError(f"Lỗi ở phần set vào redis: {str(e)}")
