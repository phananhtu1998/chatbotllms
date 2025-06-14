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
from ...models.login import LoginInput, LoginOutput, RefreshTokenInput, ChangePasswordInput
from ...response.errors import ErrorNotAuth, ErrorForbidden, ErrorInternal, ErrorBadRequest, AppError
import traceback
from fastapi import Request


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
            subtoken = TokenGenerator.generate_cli_token_uuid(item_account["number"])
            
            # Get account info
            result_tuple = await AccountQuery.get_account_by_id(self.pool, item_account["id"])
            if result_tuple is None:
                return 500, None, ErrorInternal("Failed to retrieve account information (unexpected None from DB query)")

            info_account, err = result_tuple
            if err is not None:
                return 500, None, ErrorInternal("Error getting account information")

            try:
                # Convert UUID and datetime objects to strings for JSON serialization
                for key, value in info_account.items():
                    if isinstance(value, uuid.UUID):
                        info_account[key] = str(value)
                    elif isinstance(value, datetime):
                        info_account[key] = value.isoformat()
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
                    success = await KeyTokenQuery.update_refresh_token(self.pool, item_account["id"], refresh_token)
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
                id=str(item_account["id"]),
                username=item_account["username"],
                email = item_account["email"],
                image = item_account["images"],
                accesstoken=access_token.token,
                refreshToken=refresh_token,
            )

            return 200, output, None

        except Exception as e:
            if isinstance(e, AppError):
                return e.code, None, e
            # Capture traceback for more detailed logging
            detailed_error = traceback.format_exc()
            return 500, None, ErrorInternal(message=str(e), details={"traceback": detailed_error})
        
    async def logout(self, request: Request) -> Tuple[int, Optional[Dict[str, Any]], Optional[Exception]]:
        try:
            # Get subject_uuid from context
            subject_uuid = request.state.subject_uuid
            if not subject_uuid:
                return 401, None, ErrorNotAuth("Subject UUID not found in context")

            # Get user info from Redis cache
            try:
                user_info = await global_instance.redis_client.get(subject_uuid)
                if not user_info:
                    return 500, None, ErrorInternal("User info not found in cache")
                
                user_data = json.loads(user_info)
            except Exception as e:
                return 500, None, ErrorInternal(f"Error getting user info from cache: {str(e)}")

            # Add token to blacklist in Redis
            if not global_instance.redis_client:
                return 500, None, ErrorInternal("Redis client not initialized")
            
            # Create Redis key for blacklist
            redis_key = f"TOKEN_BLACK_LIST_{subject_uuid}"
            
            # Set token in blacklist with expiration
            await global_instance.redis_client.set(redis_key, "1", ex=REFRESH_TOKEN * 3600)  # Convert hours to seconds
            
            # Delete user's refresh token from database
            try:
                success = await KeyTokenQuery.delete_key(self.pool, user_data["id"])
                if not success:
                    return 500, None, ErrorInternal("Failed to delete refresh token")
            except Exception as e:
                return 500, None, ErrorInternal(f"Error deleting refresh token: {str(e)}")
            
            return 200, {"message": "Successfully logged out"}, None
            
        except Exception as e:
            return 500, None, ErrorInternal(f"Error during logout: {str(e)}")
        
    async def refresh_tokens(self, request: Request, refresh_token: str) -> Tuple[int, Optional[LoginOutput], Optional[Exception]]:
        try:
            # Get refresh token from input
            if not refresh_token:
                return 401, None, ErrorNotAuth("Refresh token not provided")

            # Check if refresh token exists in database
            count_refresh_token = await KeyTokenQuery.count_refresh_token_by_account(self.pool, refresh_token)
            if count_refresh_token == 0:
                return 401, None, ErrorNotAuth("Account not registered or logged in elsewhere. Please login again.")

            # Get subject UUID from context
            subject_uuid = request.state.subject_uuid
            if not subject_uuid:
                return 401, None, ErrorNotAuth("Subject UUID not found in context")

            # Get user info from Redis cache
            try:
                user_info = await global_instance.redis_client.get(subject_uuid)
                if not user_info:
                    return 500, None, ErrorInternal("User info not found in cache")
                
                user_data = json.loads(user_info)
            except Exception as e:
                return 500, None, ErrorInternal(f"Error getting user info from cache: {str(e)}")

            # Check if refresh token has been used
            used_token_count = await KeyTokenQuery.count_by_token_and_account(
                self.pool,
                user_data["id"],
                refresh_token
            )
            if used_token_count > 0:
                # Delete key if token has been used
                await KeyTokenQuery.delete_key(self.pool, user_data["id"])
                return 401, None, ErrorNotAuth("Refresh token has been used")

            # Get account info
            account_info = await AccountQuery.get_account_by_username(self.pool, user_data["username"])
            if not account_info:
                return 404, None, ErrorInternal("Account not found")

            # Generate new subtoken
            subtoken = TokenGenerator.generate_cli_token_uuid(account_info["number"])

            # Get full account info
            result_tuple = await AccountQuery.get_account_by_id(self.pool, account_info["id"])
            if result_tuple is None:
                return 500, None, ErrorInternal("Failed to retrieve account information")

            info_account, err = result_tuple
            if err is not None:
                return 500, None, ErrorInternal("Error getting account information")

            try:
                # Convert UUID and datetime objects to strings for JSON serialization
                for key, value in info_account.items():
                    if isinstance(value, uuid.UUID):
                        info_account[key] = str(value)
                    elif isinstance(value, datetime):
                        info_account[key] = value.isoformat()
                info_account_json = json.dumps(info_account)
            except Exception as e:
                return 500, None, ErrorInternal(f"Error converting account info to JSON: {str(e)}")

            # Update Redis cache
            try:
                await global_instance.redis_client.set(
                    subtoken,
                    info_account_json,
                    ex=REFRESH_TOKEN * 3600  # Convert hours to seconds
                )
            except Exception as e:
                return 500, None, ErrorInternal(f"Error setting Redis: {str(e)}")

            # Create new tokens
            access_token = create_token(subtoken)
            new_refresh_token = create_refresh_token(subtoken)

            # Update refresh token in database
            try:
                success = await KeyTokenQuery.update_refresh_token_and_used_tokens(
                    self.pool,
                    account_info["id"],
                    new_refresh_token
                )
                if not success:
                    return 500, None, ErrorInternal("Failed to update refresh token")
            except Exception as e:
                return 500, None, ErrorInternal(f"Error updating refresh token: {str(e)}")

            # Prepare output
            output = LoginOutput(
                id=str(account_info["id"]),
                username=account_info["username"],
                email=account_info["email"],
                image=account_info["images"],
                accesstoken=access_token.token,
                refreshToken=new_refresh_token,
            )

            return 200, output, None

        except Exception as e:
            if isinstance(e, AppError):
                return e.code, None, e
            # Capture traceback for more detailed logging
            detailed_error = traceback.format_exc()
            return 500, None, ErrorInternal(message=str(e), details={"traceback": detailed_error})
        
    async def change_password(self, request: Request, input_data: ChangePasswordInput) -> Tuple[int, LoginOutput, Optional[Exception]]:
        try:
            subject_uuid = request.state.subject_uuid
            if not subject_uuid:
                return 401, None, ErrorNotAuth("Subject UUID not found in context")

            # Get user info from Redis cache (assuming it stores enough info for password change)
            try:
                user_info_str = await global_instance.redis_client.get(subject_uuid)
                if not user_info_str:
                    return 500, None, ErrorInternal("User info not found in cache")
                user_info = json.loads(user_info_str)
            except Exception as e:
                return 500, None, ErrorInternal(f"Error getting user info from cache: {str(e)}")

            # Get account details from DB
            account_tuple = await AccountQuery.get_account_by_id(self.pool, user_info["id"])
            if account_tuple is None or account_tuple[0] is None:
                return 500, None, ErrorInternal("Failed to retrieve account information from DB")
            account_data, err = account_tuple
            if err:
                return 500, None, ErrorInternal(f"Error getting account information from DB: {str(err)}")

            # Verify old password
            if not Crypto.matching_password(account_data["password"], input_data.old_password, account_data["salt"]):
                return 401, None, ErrorNotAuth("Old password is incorrect")

            # Generate new hashed password and salt
            new_salt = Crypto.generate_salt()
            new_hashed_password = Crypto.hash_password(input_data.new_password, new_salt)

            # Update password in DB
            success = await AccountQuery.change_password_by_id(self.pool, new_hashed_password, user_info["id"], new_salt)
            if not success:
                return 500, None, ErrorInternal("Failed to update password in database")

            # Invalidate old tokens by setting a timestamp in Redis (TOKEN_IAT_AVAILABLE_ACCOUNT_ID)
            invalidation_key = f"TOKEN_IAT_AVAILABLE_{user_info['id']}"
            await global_instance.redis_client.set(invalidation_key, int(datetime.utcnow().timestamp()), ex=REFRESH_TOKEN * 3600)

            # Generate new subtoken and update cache
            subtoken = TokenGenerator.generate_cli_token_uuid(account_data["number"])
            try:
                # Convert UUID and datetime objects to strings for JSON serialization for new cache entry
                for key, value in account_data.items():
                    if isinstance(value, uuid.UUID):
                        account_data[key] = str(value)
                    elif isinstance(value, datetime):
                        account_data[key] = value.isoformat()
                account_info_json = json.dumps(account_data)
            except Exception as e:
                return 500, None, ErrorInternal(f"Error converting account info to JSON for cache: {str(e)}")

            try:
                await global_instance.redis_client.set(
                    subtoken,
                    account_info_json,
                    ex=REFRESH_TOKEN * 3600  # Convert hours to seconds
                )
            except Exception as e:
                return 500, None, ErrorInternal(f"Error setting Redis for new subtoken: {str(e)}")

            # Create new tokens
            access_token = create_token(subtoken)
            new_refresh_token = create_refresh_token(subtoken)

            # Update refresh token in database
            success = await KeyTokenQuery.update_refresh_token(self.pool, user_info["id"], new_refresh_token)
            if not success:
                return 500, None, ErrorInternal("Failed to update refresh token in database")

            # Prepare output
            output = LoginOutput(
                id=str(account_data["id"]),
                username=account_data["username"],
                email=account_data["email"],
                image=account_data["images"],
                accesstoken=access_token.token,
                refreshToken=new_refresh_token,
            )

            return 200, output, None

        except Exception as e:
            if isinstance(e, AppError):
                return e.code, None, e
            detailed_error = traceback.format_exc()
            return 500, None, ErrorInternal(message=str(e), details={"traceback": detailed_error})
        
        
