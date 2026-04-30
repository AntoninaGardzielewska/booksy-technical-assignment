"""Authentication tests."""
import pytest
from backend.models import User, UserRole
from backend.security import hash_password, verify_password


class TestAuthentication:
    """Authentication tests."""
    
    def test_login_success(self, client, regular_user):
        """Test successful login."""
        response = client.post(
            "/auth/login",
            json={"email": regular_user.email, "password": "password123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == regular_user.email
    
    def test_login_invalid_email(self, client):
        """Test login with non-existent email."""
        response = client.post(
            "/auth/login",
            json={"email": "nonexistent@test.com", "password": "password123"}
        )
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, client, regular_user):
        """Test login with wrong password."""
        response = client.post(
            "/auth/login",
            json={"email": regular_user.email, "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_inactive_user(self, client, db, regular_user):
        """Test login with inactive user."""
        regular_user.is_active = False
        db.commit()
        
        response = client.post(
            "/auth/login",
            json={"email": regular_user.email, "password": "password123"}
        )
        
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()


class TestPasswordHashing:
    """Password hashing tests."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "mypassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 10
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "mypassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed)
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "mypassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        assert not verify_password(wrong_password, hashed)
