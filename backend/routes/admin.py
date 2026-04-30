"""Admin routes for managing users and hardware."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User, Hardware, UserRole
from backend.schemas import UserCreate, UserResponse, HardwareCreate, HardwareResponse, HardwareListResponse
from backend.security import hash_password
from backend.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new user (admin only).
    
    Args:
        user_data: User creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created user
    """
    # Check if current user is admin
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create users"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user created: {user_data.email} with role {user_data.role.value}")
    
    return UserResponse.from_orm(new_user)


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all users (admin only).
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of users
    """
    # Check if current user is admin
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can list users"
        )
    
    users = db.query(User).all()
    return [UserResponse.from_orm(user) for user in users]


@router.post("/hardware", response_model=HardwareResponse, status_code=status.HTTP_201_CREATED)
async def add_hardware(
    hardware_data: HardwareCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add new hardware item (admin only).
    
    Args:
        hardware_data: Hardware creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created hardware item
    """
    # Check if current user is admin
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can add hardware"
        )
    
    # Create new hardware
    new_hardware = Hardware(**hardware_data.dict())
    
    db.add(new_hardware)
    db.commit()
    db.refresh(new_hardware)
    
    logger.info(f"New hardware added: {hardware_data.name} (Brand: {hardware_data.brand})")
    
    return HardwareResponse.from_orm(new_hardware)


@router.delete("/hardware/{hardware_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hardware(
    hardware_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete hardware item (admin only).
    
    Args:
        hardware_id: ID of hardware to delete
        db: Database session
        current_user: Current authenticated user
    """
    # Check if current user is admin
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete hardware"
        )
    
    hardware = db.query(Hardware).filter(Hardware.id == hardware_id).first()
    
    if not hardware:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hardware not found"
        )
    
    # Check if hardware is currently in use
    if hardware.status.value == "In Use":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete hardware that is currently in use"
        )
    
    db.delete(hardware)
    db.commit()
    
    logger.info(f"Hardware deleted: ID {hardware_id}")


@router.patch("/hardware/{hardware_id}/toggle-repair", response_model=HardwareResponse)
async def toggle_repair_status(
    hardware_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Toggle repair status of hardware (admin only).
    
    Args:
        hardware_id: ID of hardware
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated hardware item
    """
    # Check if current user is admin
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can toggle repair status"
        )
    
    hardware = db.query(Hardware).filter(Hardware.id == hardware_id).first()
    
    if not hardware:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hardware not found"
        )
    
    # Toggle between Available and Repair
    if hardware.status == "Repair":
        hardware.status = "Available"
        hardware.assigned_to = None
    else:
        hardware.status = "Repair"
    
    db.commit()
    db.refresh(hardware)
    
    logger.info(f"Hardware {hardware_id} repair status toggled to {hardware.status.value}")
    
    return HardwareResponse.from_orm(hardware)
