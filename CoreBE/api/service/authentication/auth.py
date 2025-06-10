from typing import Optional, Dict, Any, Tuple
import asyncpg
from ...sql.account import AccountQuery
from ...sql.keytoken import KeyTokenQuery
from datetime import datetime, timedelta
from ...utils.crypto.crypto import Crypto
from ...utils.utils import TokenGenerator
from ...utils.auth.jwt import create_token, create_refresh_token
import uuid
import json
from api.global_config.global_val import global_instance
from ...const.const import REFRESH_TOKEN
from ...models.login import LoginInput, LoginOutput
from ...errors.errors import ErrorNotAuth, ErrorForbidden, ErrorInternal, ErrorBadRequest, AppError
import traceback


class AuthService:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def login(self, input_data: LoginInput) -> Tuple[int, LoginOutput, Optional[Exception]]:
        try:
            # Check if user with username exists
            item_account = await AccountQuery.get_account_by_username(self.pool, input_data.username)
            if not item_account:
                return 401, None, ErrorNotAuth()

            # Verify password
            if not Crypto.matching_password(item_account["password"], input_data.password, item_account["salt"]):
                return 401, None, ErrorNotAuth()
            
            # Check if account is active
            if item_account["status"] == False:
                return 403, None, ErrorForbidden("Account is Locked")

            # Generate tokens
            subtoken = TokenGenerator(item_account["number"])
            
            # Get account info
            info_account, err = await AccountQuery.get_account_by_id(self.pool, item_account["id"])
            if err is not None:
                return 500, None, ErrorInternal("Error getting account information")

            try:
                info_account_json = json.dumps(info_account)
            except Exception as e:
                return 500, None, ErrorInternal(f"Error converting account info to JSON: {str(e)}")
                
            try:
                await global_instance.redis_client.set(
                    subtoken,
                    info_account_json,
                    ex=REFRESH_TOKEN * 3600  # Convert hours to seconds
                )
            except Exception as e:
                return 500, None, ErrorInternal(f"Error setting Redis: {str(e)}")

            # Create tokens
            access_token = create_token(subtoken)
            refresh_token = create_refresh_token(subtoken)
            
            try:
                KeyToken = await KeyTokenQuery.count_by_account(self.pool, item_account["id"])
            except Exception as e:
                return 400, None, ErrorBadRequest(f"Error count keytoken account: {str(e)}")
                
            if KeyToken > 0:
                try:
                    success = await KeyTokenQuery.update_refresh_token_and_used_tokens(self.pool, item_account["id"], refresh_token)
                    if not success:
                        return 500, None, ErrorInternal("Failed to update refresh token")
                except Exception as e:
                    return 500, None, ErrorInternal(f"Error update data: {str(e)}")
            else:
                try:
                    success = await KeyTokenQuery.insert_key(self.pool, refresh_token, item_account["id"])
                    if not success:
                        return 500, None, ErrorInternal("Failed to insert key token")
                except Exception as e:
                    return 500, None, ErrorInternal(f"Error insert data: {str(e)}")
                    
            # Prepare output
            output = LoginOutput(
                id=item_account["id"],
                username=item_account["username"],
                accesstoken=access_token,
                refresh_token=refresh_token,
                x_api_key=item_account.get("api_key", "")
            )

            return 200, output, None

        except Exception as e:
            if isinstance(e, AppError):
                return e.code, None, e
            # Capture traceback for more detailed logging
            detailed_error = traceback.format_exc()
            return 500, None, ErrorInternal(message=str(e), details={"traceback": detailed_error})
