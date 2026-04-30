"""Rental business logic tests."""
import pytest
from backend.models import HardwareStatus, Rental
from datetime import datetime


class TestRentalBusinessLogic:
    """Test rental business logic and guards."""
    
    def test_cannot_rent_unavailable_hardware(self, client, user_token, sample_hardware, db):
        """Test that users cannot rent hardware that is not available."""
        # MacBook Pro 13 is in IN_USE status
        in_use_hardware = sample_hardware[1]
        
        response = client.post(
            f"/dashboard/hardware/{in_use_hardware.id}/rent",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 400
        assert "not available" in response.json()["detail"].lower()
    
    def test_cannot_rent_hardware_in_repair(self, client, user_token, sample_hardware):
        """Test that users cannot rent hardware in repair status."""
        # Razer Basilisk V2 is in REPAIR status
        repair_hardware = sample_hardware[2]
        
        response = client.post(
            f"/dashboard/hardware/{repair_hardware.id}/rent",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 400
        assert "not available" in response.json()["detail"].lower()
    
    def test_successful_rent_hardware(self, client, user_token, sample_hardware, db):
        """Test successful hardware rental."""
        # iPhone 13 Pro Max is available
        available_hardware = sample_hardware[0]
        
        response = client.post(
            f"/dashboard/hardware/{available_hardware.id}/rent",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["hardware_id"] == available_hardware.id
        assert data["user_id"] is not None
        assert data["returned_at"] is None
        
        # Verify hardware status changed
        db.refresh(available_hardware)
        assert available_hardware.status == HardwareStatus.IN_USE
        assert available_hardware.assigned_to is not None
    
    def test_cannot_return_hardware_not_rented_by_user(self, client, regular_user, user_token, sample_hardware):
        """Test that user cannot return hardware they didn't rent."""
        # Try to return MacBook Pro which is rented by someone else
        in_use_hardware = sample_hardware[1]
        
        response = client.post(
            f"/dashboard/hardware/{in_use_hardware.id}/return",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 404
        assert "No active rental found" in response.json()["detail"]
    
    def test_successful_return_hardware(self, client, user_token, sample_hardware, db, regular_user):
        """Test successful hardware return."""
        # First rent a hardware
        available_hardware = sample_hardware[0]
        rent_response = client.post(
            f"/dashboard/hardware/{available_hardware.id}/rent",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert rent_response.status_code == 201
        
        # Then return it
        return_response = client.post(
            f"/dashboard/hardware/{available_hardware.id}/return",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert return_response.status_code == 200
        data = return_response.json()
        assert data["returned_at"] is not None
        
        # Verify hardware status changed back
        db.refresh(available_hardware)
        assert available_hardware.status == HardwareStatus.AVAILABLE
        assert available_hardware.assigned_to is None
    
    def test_concurrent_rental_prevention(self, client, db, sample_hardware, admin_user, regular_user):
        """Test that only first user can rent hardware (first wins)."""
        available_hardware = sample_hardware[0]
        
        # Simulate two concurrent rental attempts
        # Note: In real concurrency testing, use proper async/threading
        from backend.security import create_jwt_token
        from backend.models import User
        
        # Create second user
        second_user = User(
            email="user2@test.com",
            password_hash="hashed",
            role="user"
        )
        db.add(second_user)
        db.commit()
        
        token1 = create_jwt_token(regular_user.id, regular_user.email, "user")
        token2 = create_jwt_token(second_user.id, second_user.email, "user")
        
        # First rental should succeed
        response1 = client.post(
            f"/dashboard/hardware/{available_hardware.id}/rent",
            headers={"Authorization": f"Bearer {token1}"}
        )
        assert response1.status_code == 201
        
        # Second rental attempt should fail
        response2 = client.post(
            f"/dashboard/hardware/{available_hardware.id}/rent",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert response2.status_code == 400
        assert "not available" in response2.json()["detail"].lower()


class TestRentalTracking:
    """Test rental history tracking."""
    
    def test_user_rentals_list(self, client, user_token, sample_hardware, regular_user):
        """Test that users can see their rental history."""
        # Rent a hardware
        available_hardware = sample_hardware[0]
        client.post(
            f"/dashboard/hardware/{available_hardware.id}/rent",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # Get user rentals
        response = client.get(
            "/dashboard/user-rentals",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["hardware_id"] == available_hardware.id
    
    def test_rental_history_shows_returned(self, client, user_token, sample_hardware, regular_user):
        """Test that rental history shows returned items."""
        available_hardware = sample_hardware[0]
        
        # Rent
        client.post(
            f"/dashboard/hardware/{available_hardware.id}/rent",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # Return
        client.post(
            f"/dashboard/hardware/{available_hardware.id}/return",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # Get history
        response = client.get(
            "/dashboard/user-rentals",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["returned_at"] is not None
