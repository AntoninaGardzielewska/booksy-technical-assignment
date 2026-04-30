"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.schemas import LoginRequest, LoginResponse, UserResponse
from backend.security import verify_password, create_jwt_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """User login endpoint.
    
    Args:
        request: Login credentials
        db: Database session
        
    Returns:
        JWT token and user info
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        logger.warning(f"Failed login attempt for email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    token = create_jwt_token(user.id, user.email, user.role.value)
    
    logger.info(f"Successful login for user: {user.email}")
    
    return LoginResponse(
        access_token=token,
        user=UserResponse.from_orm(user)
    )
