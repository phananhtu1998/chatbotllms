from typing import Any, Dict, List, Optional, TypeVar, Generic
from fastapi import status
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=10, ge=1, le=100, description="Number of items per page")

class PaginationInfo(BaseModel):
    """Pagination information"""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model"""
    items: List[T] = Field(..., description="List of items")
    pagination: PaginationInfo = Field(..., description="Pagination information")

class ResponseModel(BaseModel, Generic[T]):
    """Standard API response model"""
    status: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Response message")
    data: Optional[T] = Field(None, description="Response data")

def create_response(
    *,
    status_code: int = status.HTTP_200_OK,
    message: str = "Success",
    data: Any = None
) -> Dict[str, Any]:
    """
    Create a standardized API response
    
    Args:
        status_code: HTTP status code
        message: Response message
        data: Response data
        
    Returns:
        Dict containing the standardized response
    """
    return {
        "status": status_code,
        "message": message,
        "data": data
    }

def create_paginated_response(
    *,
    items: List[Any],
    total: int,
    page: int,
    limit: int
) -> Dict[str, Any]:
    """
    Create a paginated response
    
    Args:
        items: List of items
        total: Total number of items
        page: Current page number
        limit: Number of items per page
        
    Returns:
        Dict containing the paginated response
    """
    total_pages = (total + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1
    
    pagination_info = {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev
    }
    
    return create_response(
        data={
            "items": items,
            "pagination": pagination_info
        }
    )

def get_pagination_params(page: int = 1, limit: int = 10) -> Dict[str, int]:
    """
    Get pagination parameters with validation
    
    Args:
        page: Page number (default: 1)
        limit: Items per page (default: 10)
        
    Returns:
        Dict containing validated pagination parameters
    """
    # Ensure page is at least 1
    page = max(1, page)
    
    # Ensure limit is between 1 and 100
    limit = max(1, min(100, limit))
    
    return {
        "page": page,
        "limit": limit
    }

def calculate_offset(page: int, limit: int) -> int:
    """
    Calculate the offset for pagination
    
    Args:
        page: Page number
        limit: Items per page
        
    Returns:
        Offset value for database query
    """
    return (page - 1) * limit 