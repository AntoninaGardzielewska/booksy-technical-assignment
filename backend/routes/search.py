"""Semantic search routes using Gemini API."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import Hardware, HardwareStatus
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


def keyword_search(query: str, hardware_items: List[Hardware]) -> List[Hardware]:
    """Keyword-based search for hardware items.
    
    Args:
        query: Search query
        hardware_items: List of hardware items to search within
        
    Returns:
        Filtered and ranked hardware items based on keyword matching
    """
    if not hardware_items:
        return []
    
    query_lower = query.lower()
    keywords = query_lower.split()
    
    scored_items = []
    for hw in hardware_items:
        hw_text = f"{hw.name} {hw.brand} {hw.notes or ''}".lower()
        # Score based on keyword matches
        score = sum(1 for keyword in keywords if keyword in hw_text)
        if score > 0:
            scored_items.append((hw, score))
    
    # Sort by relevance (more keyword matches = higher score)
    scored_items.sort(key=lambda x: x[1], reverse=True)
    return [hw for hw, _ in scored_items]


def semantic_search_with_gemini(query: str, hardware_items: List[Hardware]) -> List[Hardware]:
    """Perform semantic search using Gemini on filtered hardware items.
    
    Args:
        query: User's natural language query
        hardware_items: List of filtered hardware items to search within
        
    Returns:
        Hardware items based on semantic relevance from Gemini
    """
    if not hardware_items:
        return []
    
    try:
        genai = get_gemini_client()
        if not genai or not settings.gemini_api_key:
            logger.warning("Gemini API not configured, falling back to keyword search")
            return keyword_search(query, hardware_items)
        
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
        
        logger.info(f"Semantic search for '{query}' returned {len(filtered_items)} results from {len(hardware_items)} filtered items")
        return filtered_items
        
    except Exception as e:
        logger.error(f"Error in Gemini semantic search: {e}")
        # Fall back to keyword search
        return keyword_search(query, hardware_items)





@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Semantic search for hardware with filtering.
    
    Search strategy (applied in order):
    1. First, apply any status filters to narrow down hardware
    2. Then, perform keyword matching on filtered results
    3. If keyword matches found, return them
    4. If no keyword matches, use AI (Gemini) to find relevant items from filtered subset
    
    Args:
        request: Search query with optional status_filter
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Filtered and semantically relevant hardware items
    """
    query = request.query.strip()
    status_filter = request.status_filter
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    # Step 1: Apply status filter (AND logic with all other filters)
    filtered_query = db.query(Hardware)
    filters_applied = {}
    
    if status_filter:
        try:
            status_enum = HardwareStatus(status_filter)
            filtered_query = filtered_query.filter(Hardware.status == status_enum)
            filters_applied["status"] = status_filter
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter: {status_filter}. Must be one of: Available, In Use, Repair"
            )
    
    filtered_hardware = filtered_query.all()
    
    if not filtered_hardware:
        logger.info(f"User {current_user['email']} searched for '{query}' with filters {filters_applied} - no hardware matched filters")
        return SemanticSearchResponse(
            results=[],
            query=query,
            filters_applied=filters_applied
        )
    
    # Step 2: Try keyword search first on filtered results
    keyword_results = keyword_search(query, filtered_hardware)
    
    if keyword_results:
        logger.info(f"User {current_user['email']} searched for '{query}' with filters {filters_applied} - {len(keyword_results)} keyword matches found")
        return SemanticSearchResponse(
            results=[HardwareResponse.from_orm(hw) for hw in keyword_results],
            query=query,
            filters_applied=filters_applied
        )
    
    # Step 3: If no keyword matches, use AI on filtered subset
    ai_results = semantic_search_with_gemini(query, filtered_hardware)
    
    logger.info(f"User {current_user['email']} searched for '{query}' with filters {filters_applied} - {len(ai_results)} AI matches found")
    
    return SemanticSearchResponse(
        results=[HardwareResponse.from_orm(hw) for hw in ai_results],
        query=query,
        filters_applied=filters_applied
    )
