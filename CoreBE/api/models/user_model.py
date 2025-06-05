from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

class UserCreateRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    images: Optional[str] = Field(None, description="Path to user image") 
    name: str = Field(..., description="Name of the user")
    role_id: uuid.UUID = Field(..., description="Role ID of the user")
    status: bool = Field(..., description="Status of the user")
    username: str = Field(..., min_length=3, max_length=50, description="Username of the user")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@gmail.com",
                "images": "/upload/images/phananhtu.jpg",
                "name": "Admin",
                "role_id": "2b796313-1134-44b3-b527-2c27d41a1624",
                "status": True,
                "username": "admin"
            }
        }

class UserResponse(BaseModel):
    id: int = Field(..., description="Unique identifier of the user")
    username: str = Field(..., description="Username of the user")
    email: str = Field(..., description="Email address of the user")
    full_name: Optional[str] = Field(None, description="Full name of the user")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe"
            }
        } 