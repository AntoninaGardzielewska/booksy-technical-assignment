"""Dashboard and hardware rental routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from backend.database import get_db
from backend.models import Hardware, Rental, HardwareStatus, User
from backend.schemas import (
    HardwareResponse, HardwareListResponse, RentalResponse,
    RentalCreateRequest, RentalReturnRequest
)
from backend.dependencies import get_current_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/hardware", response_model=HardwareListResponse)
async def list_hardware(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    brand_filter: Optional[str] = Query(None),
    sort_by: str = Query("name", regex="^(name|brand|purchase_date|status)$")
):
    """List hardware with filtering and sorting.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        skip: Number of items to skip
        limit: Maximum items to return
        status_filter: Filter by status (Available, In Use, Repair)
        brand_filter: Filter by brand
        sort_by: Sort by field (name, brand, purchase_date, status)
        
    Returns:
        Paginated list of hardware items
    """
    query = db.query(Hardware)
    
    # Apply status filter
    if status_filter:
        try:
            status_enum = HardwareStatus(status_filter)
            query = query.filter(Hardware.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    if brand_filter:
        query = query.filter(Hardware.brand.ilike(f"%{brand_filter}%"))

    # Get total count
    total = query.count()
    
    # Apply sorting
    if sort_by == "name":
        query = query.order_by(Hardware.name)
    elif sort_by == "brand":
        query = query.order_by(Hardware.brand)
    elif sort_by == "purchase_date":
        query = query.order_by(Hardware.purchase_date)
    elif sort_by == "status":
        query = query.order_by(Hardware.status)
    
    # Apply pagination
    items = query.offset(skip).limit(limit).all()
    
    return HardwareListResponse(
        items=[HardwareResponse.from_orm(item) for item in items],
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/hardware/{hardware_id}/rent", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
async def rent_hardware(
    hardware_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Rent hardware item (user).
    
    Args:
        hardware_id: ID of hardware to rent
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Rental record
    """
    # Get hardware
    hardware = db.query(Hardware).filter(Hardware.id == hardware_id).first()
    
    if not hardware:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hardware not found"
        )
    
    # Check if hardware is available
    if hardware.status != HardwareStatus.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Hardware is not available (current status: {hardware.status.value})"
        )
    
    # Use atomic transaction to prevent race conditions
    # Check again inside transaction (double-check pattern)
    hardware_check = db.query(Hardware).filter(Hardware.id == hardware_id).with_for_update().first()
    
    if hardware_check.status != HardwareStatus.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hardware was just rented by another user"
        )
    
    # Get user
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    # Create rental record
    rental = Rental(
        hardware_id=hardware_id,
        user_id=current_user["user_id"],
        rented_at=datetime.utcnow()
    )
    
    # Update hardware status
    hardware_check.status = HardwareStatus.IN_USE
    hardware_check.assigned_to = current_user["email"]
    
    db.add(rental)
    db.commit()
    db.refresh(rental)
    
    logger.info(f"Hardware {hardware_id} rented by user {current_user['email']}")
    
    return RentalResponse.from_orm(rental)


@router.post("/hardware/{hardware_id}/return", response_model=RentalResponse)
async def return_hardware(
    hardware_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Return rented hardware item (user).
    
    Args:
        hardware_id: ID of hardware to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated rental record
    """
    # Get active rental for this user and hardware
    rental = db.query(Rental).filter(
        and_(
            Rental.hardware_id == hardware_id,
            Rental.user_id == current_user["user_id"],
            Rental.returned_at == None
        )
    ).first()
    
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active rental found for this hardware"
        )
    
    # Update rental
    rental.returned_at = datetime.utcnow()
    
    # Update hardware status
    hardware = db.query(Hardware).filter(Hardware.id == hardware_id).first()
    hardware.status = HardwareStatus.AVAILABLE
    hardware.assigned_to = None
    
    db.commit()
    db.refresh(rental)
    
    logger.info(f"Hardware {hardware_id} returned by user {current_user['email']}")
    
    return RentalResponse.from_orm(rental)


@router.get("/user-rentals", response_model=List[RentalResponse])
async def get_user_rentals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all rentals for current user.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of rentals for the user
    """
    rentals = db.query(Rental).filter(
        Rental.user_id == current_user["user_id"]
    ).order_by(Rental.rented_at.desc()).all()
    
    return [RentalResponse.from_orm(rental) for rental in rentals]
