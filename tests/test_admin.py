"""Admin functionality tests."""
import pytest
from backend.models import UserRole, HardwareStatus


class TestAdminUserManagement:
    """Test admin user management."""
    
    def test_admin_create_user(self, client, admin_token):
        """Test that admin can create new users."""
        response = client.post(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "email": "newuser@test.com",
                "password": "password123",
                "role": "user"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "user"
    
    def test_regular_user_cannot_create_user(self, client, user_token):
        """Test that regular users cannot create users."""
        response = client.post(
            "/admin/users",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "email": "newuser@test.com",
                "password": "password123",
                "role": "user"
            }
        )
        
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()
    
    def test_cannot_create_duplicate_email(self, client, admin_token, regular_user):
        """Test that duplicate emails cannot be created."""
        response = client.post(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "email": regular_user.email,
                "password": "password123",
                "role": "user"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_admin_list_users(self, client, admin_token):
        """Test that admin can list all users."""
        response = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the admin


class TestAdminHardwareManagement:
    """Test admin hardware management."""
    
    def test_admin_add_hardware(self, client, admin_token):
        """Test that admin can add hardware."""
        response = client.post(
            "/admin/hardware",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "New Laptop",
                "brand": "Dell",
                "purchase_date": "15-03-2022",
                "status": "Available",
                "notes": "Brand new"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Laptop"
        assert data["brand"] == "Dell"
        assert data["status"] == "Available"
    
    def test_regular_user_cannot_add_hardware(self, client, user_token):
        """Test that regular users cannot add hardware."""
        response = client.post(
            "/admin/hardware",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "name": "New Laptop",
                "brand": "Dell",
                "purchase_date": "15-03-2022",
                "status": "Available"
            }
        )
        
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()
    
    def test_admin_delete_hardware(self, client, admin_token, sample_hardware):
        """Test that admin can delete hardware."""
        # Razer Basilisk is in Repair, should be deletable
        repair_hardware = sample_hardware[2]
        
        response = client.delete(
            f"/admin/hardware/{repair_hardware.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 204
    
    def test_cannot_delete_hardware_in_use(self, client, admin_token, sample_hardware):
        """Test that hardware in use cannot be deleted."""
        in_use_hardware = sample_hardware[1]
        
        response = client.delete(
            f"/admin/hardware/{in_use_hardware.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400
        assert "in use" in response.json()["detail"].lower()
    
    def test_admin_toggle_repair_status(self, client, admin_token, sample_hardware, db):
        """Test that admin can toggle repair status."""
        available_hardware = sample_hardware[0]
        
        response = client.patch(
            f"/admin/hardware/{available_hardware.id}/toggle-repair",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Repair"
        
        # Toggle back
        response2 = client.patch(
            f"/admin/hardware/{available_hardware.id}/toggle-repair",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["status"] == "Available"
    
    def test_regular_user_cannot_toggle_repair(self, client, user_token, sample_hardware):
        """Test that regular users cannot toggle repair status."""
        available_hardware = sample_hardware[0]
        
        response = client.patch(
            f"/admin/hardware/{available_hardware.id}/toggle-repair",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403


class TestHardwareListing:
    """Test hardware listing with filtering and sorting."""
    
    def test_list_all_hardware(self, client, user_token, sample_hardware):
        """Test listing all hardware."""
        response = client.get(
            "/dashboard/hardware",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == len(sample_hardware)
        assert len(data["items"]) == len(sample_hardware)
    
    def test_filter_by_status(self, client, user_token, sample_hardware):
        """Test filtering hardware by status."""
        response = client.get(
            "/dashboard/hardware?status_filter=Available",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1  # Only iPhone
        assert all(item["status"] == "Available" for item in data["items"])
    
    def test_sort_by_name(self, client, user_token, sample_hardware):
        """Test sorting hardware by name."""
        response = client.get(
            "/dashboard/hardware?sort_by=name",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        names = [item["name"] for item in data["items"]]
        assert names == sorted(names)
    
    def test_pagination(self, client, user_token, sample_hardware):
        """Test pagination."""
        response = client.get(
            "/dashboard/hardware?skip=1&limit=2",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["skip"] == 1
        assert data["limit"] == 2
