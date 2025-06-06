from fastapi import HTTPException, status, Body
from typing import Optional, List, Dict, Any
from api.service.account import AccountService
from api.middleware.auth import get_api_key_or_bearer
from api.utils.response import create_response, create_paginated_response
from api.models.account_model import CreateAccount

class AccountController:
    def __init__(self, account_service: AccountService):
        self.account_service = account_service

    async def create_account(
        self,
        account_data: CreateAccount = Body(
            ...,
            description="Account data for creation",
            example={
                "number": 123,
                "code": "TK_1234",
                "name": "Admin",
                "email": "admin@gmail.com",
                "username": "admin",
                "password": "123456",
                "salt": "123456",
                "images": "/upload/images/phananhtu.jpg",
                "status": True,
                "created_by": "2b796313-1134-44b3-b527-2c27d41a1624"
            }
        )
    ) -> Dict[str, Any]:
        """Create a new account"""
        try:
            account = await self.account_service.create_account(
                number=account_data.number,
                code=account_data.code,
                name=account_data.name,
                email=account_data.email,
                username=account_data.username,
                password=account_data.password,
                salt=account_data.salt,
                images=account_data.images,
                status=account_data.status,
                created_by=account_data.created_by
            )
            return create_response(
                status_code=status.HTTP_201_CREATED,
                message="Account created successfully",
                data=account
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

