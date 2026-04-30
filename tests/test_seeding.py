"""Database seeding and data cleaning tests."""
import pytest
from backend.seeder import validate_and_fix_date, normalize_status, clean_hardware_data
from backend.models import HardwareStatus


class TestDataCleaning:
    """Test data cleaning utilities."""
    
    def test_validate_and_fix_date_ddmmyyyy(self):
        """Test date validation with DD-MM-YYYY format."""
        valid, fixed = validate_and_fix_date("23-11-2021")
        assert valid
        assert fixed == "23-11-2021"
    
    def test_validate_and_fix_date_yyyymmdd(self):
        """Test date validation with YYYY-MM-DD format."""
        valid, fixed = validate_and_fix_date("2021-11-23")
        assert valid
        assert fixed == "23-11-2021"
    
    def test_validate_and_fix_date_ddmmyy(self):
        """Test date validation with DD-MM-YY format."""
        valid, fixed = validate_and_fix_date("23-11-21")
        assert valid
        assert fixed == "23-11-2021"
    
    def test_validate_and_fix_date_invalid(self):
        """Test invalid date."""
        valid, fixed = validate_and_fix_date("invalid")
        assert not valid
        assert fixed == ""
    
    def test_validate_and_fix_date_empty(self):
        """Test empty date."""
        valid, fixed = validate_and_fix_date("")
        assert not valid
    
    def test_normalize_status_available(self):
        """Test normalizing various available statuses."""
        for status in ["Available", "available", "Avail", "Free"]:
            valid, normalized = normalize_status(status)
            assert valid
            assert normalized == HardwareStatus.AVAILABLE
    
    def test_normalize_status_in_use(self):
        """Test normalizing various in use statuses."""
        for status in ["In Use", "inuse", "Used", "Rented"]:
            valid, normalized = normalize_status(status)
            assert valid
            assert normalized == HardwareStatus.IN_USE
    
    def test_normalize_status_repair(self):
        """Test normalizing various repair statuses."""
        for status in ["Repair", "broken", "Maintenance", "Service"]:
            valid, normalized = normalize_status(status)
            assert valid
            assert normalized == HardwareStatus.REPAIR
    
    def test_normalize_status_invalid(self):
        """Test invalid status."""
        valid, normalized = normalize_status("InvalidStatus")
        assert not valid
        assert normalized is None


class TestHardwareDataCleaning:
    """Test complete hardware data cleaning."""
    
    def test_clean_valid_data(self):
        """Test cleaning valid hardware data."""
        raw_data = [
            {
                "id": 1,
                "name": "iPhone 13",
                "brand": "Apple",
                "purchaseDate": "2021-11-23",
                "status": "Available"
            }
        ]
        
        cleaned, warnings = clean_hardware_data(raw_data)
        
        assert len(cleaned) == 1
        assert len(warnings) == 0
        assert cleaned[0]["id"] == 1
        assert cleaned[0]["purchase_date"] == "23-11-2021"
        assert cleaned[0]["status"] == HardwareStatus.AVAILABLE
    
    def test_clean_duplicate_ids(self):
        """Test handling duplicate IDs."""
        raw_data = [
            {
                "id": 1,
                "name": "Item 1",
                "brand": "Brand 1",
                "purchaseDate": "2021-11-23",
                "status": "Available"
            },
            {
                "id": 1,  # Duplicate
                "name": "Item 2",
                "brand": "Brand 2",
                "purchaseDate": "2021-11-23",
                "status": "Available"
            }
        ]
        
        cleaned, warnings = clean_hardware_data(raw_data)
        
        assert len(cleaned) == 2
        assert len(warnings) == 1
        assert "Duplicate" in warnings[0]
        assert cleaned[0]["id"] == 1
        assert cleaned[1]["id"] == 2
    
    def test_clean_invalid_dates(self):
        """Test handling invalid dates."""
        raw_data = [
            {
                "id": 1,
                "name": "Item 1",
                "brand": "Brand 1",
                "purchaseDate": "invalid-date",
                "status": "Available"
            }
        ]
        
        cleaned, warnings = clean_hardware_data(raw_data)
        
        assert len(cleaned) == 0
        assert len(warnings) == 1
        assert "Invalid date" in warnings[0]
    
    def test_clean_invalid_status(self):
        """Test handling invalid status."""
        raw_data = [
            {
                "id": 1,
                "name": "Item 1",
                "brand": "Brand 1",
                "purchaseDate": "2021-11-23",
                "status": "InvalidStatus"
            }
        ]
        
        cleaned, warnings = clean_hardware_data(raw_data)
        
        assert len(cleaned) == 0
        assert len(warnings) == 1
        assert "Invalid status" in warnings[0]
    
    def test_clean_missing_required_fields(self):
        """Test handling missing required fields."""
        raw_data = [
            {
                "id": 1,
                "name": "",  # Empty name
                "brand": "Brand 1",
                "purchaseDate": "2021-11-23",
                "status": "Available"
            }
        ]
        
        cleaned, warnings = clean_hardware_data(raw_data)
        
        assert len(cleaned) == 0
        assert len(warnings) == 1
        assert "Missing" in warnings[0]
    
    def test_clean_complex_dataset(self):
        """Test cleaning complex dataset with multiple issues."""
        raw_data = [
            {
                "id": 1,
                "name": "Valid Item",
                "brand": "Brand A",
                "purchaseDate": "2021-11-23",
                "status": "Available"
            },
            {
                "id": 1,  # Duplicate ID
                "name": "Duplicate ID Item",
                "brand": "Brand B",
                "purchaseDate": "2021-11-23",
                "status": "Available"
            },
            {
                "id": 3,
                "name": "Invalid Date Item",
                "brand": "Brand C",
                "purchaseDate": "invalid",
                "status": "Available"
            },
            {
                "id": 4,
                "name": "Invalid Status Item",
                "brand": "Brand D",
                "purchaseDate": "2021-11-23",
                "status": "Unknown"
            }
        ]
        
        cleaned, warnings = clean_hardware_data(raw_data)
        
        # Should have 2 valid items (original 1 + reassigned duplicate)
        assert len(cleaned) == 2
        # Should have 3 warnings (duplicate, invalid date, invalid status)
        assert len(warnings) == 3
