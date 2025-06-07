from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class CreateAccount(BaseModel):
    number: int = Field(..., description="Account number")
    code: str = Field(..., description="Account code")
    name: str = Field(..., description="Account name")
    email: str = Field(..., description="Email address of the user")
    username: str = Field(..., description="Username of the user")
    password: str = Field(..., description="Password of the user")
    salt: str = Field(..., description="Salt of the user")
    status: bool = Field(..., description="Status of the user")
    images: Optional[str] = Field(None, description="Path to user image")
    is_deleted: bool = Field(False, description="Whether the user is deleted or not")
    created_at: datetime = Field(None, description="Creation date of the user")
    created_by: str = Field(..., description="User who created the user")
    updated_at: datetime = Field(..., description="Last update date of the user")