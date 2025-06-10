from typing import Optional, Dict, Any

class AppError(Exception):
    def __init__(self, message: str, code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class ErrorNotAuth(AppError):
    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(message=message, code=401)

class ErrorForbidden(AppError):
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message=message, code=403)

class ErrorNotFound(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, code=404)

class ErrorInternal(AppError):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message=message, code=500)

class ErrorBadRequest(AppError):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, code=400) 