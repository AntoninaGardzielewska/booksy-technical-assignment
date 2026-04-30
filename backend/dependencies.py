"""Dependency injection for authentication and authorization."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.security import verify_token_and_get_user
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP bearer token credentials
        
    Returns:
        User information from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    user_info = verify_token_and_get_user(token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info


async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Verify current user is admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user
