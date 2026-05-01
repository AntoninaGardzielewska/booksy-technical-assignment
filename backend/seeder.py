"""Database seeding utilities with data cleaning."""
import json
import logging
from datetime import datetime
from typing import List, Tuple
from sqlalchemy.orm import Session
from backend.models import Hardware, User, HardwareStatus, UserRole
from backend.security import hash_password
from backend.config import settings

logger = logging.getLogger(__name__)


def validate_and_fix_date(date_str: str) -> Tuple[bool, str]:
    """Validate and fix date format to DD-MM-YYYY.
    
    Args:
        date_str: Date string in any format
        
    Returns:
        Tuple of (is_valid, fixed_date_string)
    """
    if not date_str:
        return False, ""
    
    # Try various date formats
    formats = [
        "%d-%m-%Y",      # DD-MM-YYYY (target format)
        "%Y-%m-%d",      # YYYY-MM-DD
        "%d/%m/%Y",      # DD/MM/YYYY
        "%m/%d/%Y",      # MM/DD/YYYY
        "%d.%m.%Y",      # DD.MM.YYYY
        "%Y/%m/%d",      # YYYY/MM/DD
        "%d-%m-%y",      # DD-MM-YY
    ]
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(str(date_str).strip(), fmt)
            return True, parsed_date.strftime("%d-%m-%Y")
        except (ValueError, TypeError):
            continue
    
    return False, ""


def normalize_status(status: str) -> Tuple[bool, HardwareStatus]:
    """Normalize status to one of the valid options.
    
    Args:
        status: Status string to normalize
        
    Returns:
        Tuple of (is_valid, normalized_status)
    """
    if not status:
        return False, None
    
    status_lower = str(status).strip().lower()
    
    # Map variations to standard statuses
    if status_lower in ["available", "avail", "free"]:
        return True, HardwareStatus.AVAILABLE
    elif status_lower in ["in use", "inuse", "used", "rented"]:
        return True, HardwareStatus.IN_USE
    elif status_lower in ["repair", "broken", "maintenance", "service"]:
        return True, HardwareStatus.REPAIR
    
    return False, None


def clean_hardware_data(raw_data: List[dict]) -> Tuple[List[dict], List[str]]:
    """Clean and validate hardware data from JSON.
    
    Args:
        raw_data: Raw hardware data from JSON
        
    Returns:
        Tuple of (cleaned_data, warnings)
    """
    cleaned_data = []
    warnings = []
    used_ids = set()
    next_free_id = 1
    
    for idx, item in enumerate(raw_data):
        item_id = item.get("id")
        
        # Check for duplicate IDs
        if item_id in used_ids:
            # Find next free ID
            while next_free_id in used_ids:
                next_free_id += 1
            warnings.append(f"Duplicate ID {item_id} at index {idx}, reassigning to {next_free_id}")
            item_id = next_free_id
            next_free_id += 1
        
        used_ids.add(item_id)
        
        # Validate and fix date
        purchase_date = item.get("purchaseDate")
        date_valid, fixed_date = validate_and_fix_date(purchase_date)
        
        if not date_valid:
            warnings.append(f"Invalid date '{purchase_date}' for hardware at index {idx}, dropping row")
            continue
        
        # Normalize status
        status = item.get("status")
        status_valid, normalized_status = normalize_status(status)
        
        if not status_valid:
            warnings.append(f"Invalid status '{status}' for hardware at index {idx}, dropping row")
            continue
        
        # Validate required fields
        name = item.get("name", "").strip()
        brand = item.get("brand", "").strip()
        
        if not name or not brand:
            warnings.append(f"Missing name or brand for hardware at index {idx}, dropping row")
            continue
        
        cleaned_item = {
            "id": item_id,
            "name": name,
            "brand": brand,
            "purchase_date": fixed_date,
            "status": normalized_status,
            "notes": item.get("notes", "").strip() or None,
            "assigned_to": item.get("assignedTo") or item.get("assigned_to")
        }
        
        cleaned_data.append(cleaned_item)
    
    return cleaned_data, warnings


def seed_database(db: Session, initial_data_path: str = "data/initial_data.json"):
    """Seed database with initial data from JSON file.
    
    Args:
        db: Database session
        initial_data_path: Path to initial data JSON file
    """
    try:
        # Load JSON data
        with open(initial_data_path, "r") as f:
            raw_data = json.load(f)
        
        # Clean hardware data
        cleaned_data, warnings = clean_hardware_data(raw_data)
        
        # Log warnings
        for warning in warnings:
            logger.warning(f"Data cleaning: {warning}")
        
        # Add cleaned hardware items
        for item in cleaned_data:
            existing = db.query(Hardware).filter(Hardware.id == item["id"]).first()
            if not existing:
                hardware = Hardware(**item)
                db.add(hardware)
                logger.info(f"Added hardware: {item['name']} (ID: {item['id']})")
        
        # Add initial admin user
        admin_email = settings.admin_initial_email
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin = User(
                email=admin_email,
                password_hash=hash_password(settings.admin_initial_password),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            logger.info(f"Added admin user: {admin_email}")
        
        db.commit()
        logger.info(f"Database seeded successfully with {len(cleaned_data)} hardware items")
        
    except FileNotFoundError:
        logger.error(f"Initial data file not found: {initial_data_path}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in data file: {e}")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
