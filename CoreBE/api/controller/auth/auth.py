from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Tuple, Dict, Any
from ...models.login import LoginInput, LoginOutput
from ...service.authentication.auth import AuthService
from ...errors.errors import ErrorNotAuth, ErrorForbidden, ErrorInternal, AppError
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
                    # For any other AppError, or generic Exception, expose details if available
                    detail_message = str(error)
                    if hasattr(error, 'details') and error.details:
                        detail_message = {"message": str(error), "details": error.details}
                    raise HTTPException(status_code=error.code if isinstance(error, AppError) else status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail_message)

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