"""Semantic search routes using Gemini API."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import Hardware
from backend.schemas import SemanticSearchRequest, SemanticSearchResponse, HardwareResponse
from backend.dependencies import get_current_user
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


def get_gemini_client():
    """Get Gemini API client."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        return genai
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        return None


def semantic_search_with_gemini(query: str, hardware_items: List[Hardware]) -> List[Hardware]:
    """Perform semantic search using Gemini.
    
    Args:
        query: User's natural language query
        hardware_items: List of all hardware items
        
    Returns:
        Filtered and ranked hardware items based on query relevance
    """
    if not hardware_items:
        return []
    
    try:
        genai = get_gemini_client()
        if not genai or not settings.gemini_api_key:
            logger.warning("Gemini API not configured, falling back to keyword search")
            return fallback_search(query, hardware_items)
        
        # Prepare hardware descriptions
        hardware_descriptions = "\n".join([
            f"- {hw.name} (Brand: {hw.brand}, Status: {hw.status.value}, Notes: {hw.notes or 'None'})"
            for hw in hardware_items
        ])
        
        # Call Gemini to find relevant hardware
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"""Given this list of hardware items:
{hardware_descriptions}

And this user query: "{query}"

Return ONLY the hardware names that match the user's needs. Return them as a comma-separated list.
If no items match, return "NONE".
Be practical and helpful in matching items based on their categories and common use cases."""
        
        response = model.generate_content(prompt)
        relevant_names = response.text.strip().split(",")
        relevant_names = [name.strip() for name in relevant_names if name.strip() and name.strip() != "NONE"]
        
        # Filter hardware items that match the Gemini response
        filtered_items = [
            hw for hw in hardware_items
            if any(name.lower() in hw.name.lower() for name in relevant_names)
        ]
        
        logger.info(f"Semantic search for '{query}' returned {len(filtered_items)} results")
        return filtered_items
        
    except Exception as e:
        logger.error(f"Error in Gemini semantic search: {e}")
        # Fall back to keyword search
        return fallback_search(query, hardware_items)


def fallback_search(query: str, hardware_items: List[Hardware]) -> List[Hardware]:
    """Fallback keyword-based search.
    
    Args:
        query: Search query
        hardware_items: List of hardware items
        
    Returns:
        Filtered hardware items
    """
    query_lower = query.lower()
    keywords = query_lower.split()
    
    filtered_items = []
    for hw in hardware_items:
        hw_text = f"{hw.name} {hw.brand} {hw.notes or ''}".lower()
        # Score based on keyword matches
        score = sum(1 for keyword in keywords if keyword in hw_text)
        if score > 0:
            filtered_items.append(hw)
    
    # Sort by relevance (name contains more keywords)
    filtered_items.sort(
        key=lambda hw: sum(1 for kw in keywords if kw in f"{hw.name} {hw.brand}".lower()),
        reverse=True
    )
    
    return filtered_items


@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Semantic search for hardware using natural language (Gemini).
    
    Args:
        request: Search query
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Semantically relevant hardware items
    """
    query = request.query.strip()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    # Get all available hardware
    all_hardware = db.query(Hardware).all()
    
    if not all_hardware:
        return SemanticSearchResponse(results=[], query=query)
    
    # Perform semantic search
    results = semantic_search_with_gemini(query, all_hardware)
    
    logger.info(f"User {current_user['email']} searched for: '{query}' - {len(results)} results")
    
    return SemanticSearchResponse(
        results=[HardwareResponse.from_orm(hw) for hw in results],
        query=query
    )
