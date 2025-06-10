from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Tuple, Dict, Any
from ...models.login import LoginInput, LoginOutput
from ...service.authentication.auth import AuthService
from ...errors.errors import ErrorNotAuth, ErrorForbidden, ErrorInternal
from api.utils.response import create_response

class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    async def login(
        self,
        login_data: LoginInput = Body(
            ...,
            description="Login credentials",
            example={
                "username": "Admin",
                "password": "thaco@1234"
            }
        )
    ) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        try:
            status_code, response, error = await self.auth_service.login(login_data)

            if error is not None:
                if isinstance(error, ErrorNotAuth):
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
                elif isinstance(error, ErrorForbidden):
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
                else:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

            return create_response(
                status_code=status.HTTP_200_OK,
                message="Login successful",
                data=response
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            ) 