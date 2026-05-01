"""Pydantic models for request/response validation."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from backend.models import HardwareStatus, UserRole


# ============ User Schemas ============
class UserCreate(BaseModel):
    """User creation model."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER


class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: str
    role: UserRole
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Hardware Schemas ============
class HardwareCreate(BaseModel):
    """Hardware creation model."""
    name: str = Field(..., min_length=1, max_length=255)
    brand: str = Field(..., min_length=1, max_length=255)
    purchase_date: str = Field(..., pattern=r"^\d{2}-\d{2}-\d{4}$")  # DD-MM-YYYY
    status: HardwareStatus = HardwareStatus.AVAILABLE
    notes: Optional[str] = Field(None, max_length=500)


class HardwareUpdate(BaseModel):
    """Hardware update model."""
    name: Optional[str] = None
    brand: Optional[str] = None
    purchase_date: Optional[str] = None
    status: Optional[HardwareStatus] = None
    notes: Optional[str] = None


class HardwareResponse(BaseModel):
    """Hardware response model."""
    id: int
    name: str
    brand: str
    purchase_date: str
    status: HardwareStatus
    notes: Optional[str]
    assigned_to: Optional[str]
    
    class Config:
        from_attributes = True


class HardwareListResponse(BaseModel):
    """Hardware list response with pagination/filtering."""
    items: List[HardwareResponse]
    total: int
    skip: int
    limit: int

# ============ Auth Schemas ============
class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


# ============ Rental Schemas ============
class RentalResponse(BaseModel):
    """Rental response model."""
    id: int
    hardware_id: int
    user_id: int
    rented_at: datetime
    returned_at: Optional[datetime]
    hardware: HardwareResponse
    user: UserResponse
    
    class Config:
        from_attributes = True


class RentalCreateRequest(BaseModel):
    """Rental creation request."""
    hardware_id: int


class RentalReturnRequest(BaseModel):
    """Rental return request."""
    hardware_id: int


# ============ Search Schemas ============
class SemanticSearchRequest(BaseModel):
    """Semantic search request model."""
    query: str = Field(..., min_length=1)
    status_filter: Optional[str] = Field(None, description="Filter by status: Available, In Use, or Repair")


class SemanticSearchResponse(BaseModel):
    """Semantic search response model."""
    results: List[HardwareResponse]
    query: str
    filters_applied: Optional[dict] = Field(None, description="Information about applied filters")


# ============ Error Schemas ============
class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
    error_code: str
