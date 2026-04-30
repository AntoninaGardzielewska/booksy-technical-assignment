"""Test configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import get_db
from backend.models import Base, User, Hardware, HardwareStatus, UserRole
from backend.security import hash_password
from datetime import datetime


# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override get_db for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client with overridden database."""
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    admin = User(
        email="admin@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    return admin


@pytest.fixture
def regular_user(db):
    """Create a regular user for testing."""
    user = User(
        email="user@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.USER,
        is_active=True
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def sample_hardware(db):
    """Create sample hardware items for testing."""
    items = [
        Hardware(
            name="iPhone 13 Pro Max",
            brand="Apple",
            purchase_date="23-11-2021",
            status=HardwareStatus.AVAILABLE,
            notes="Perfect condition"
        ),
        Hardware(
            name="MacBook Pro 13",
            brand="Apple",
            purchase_date="20-12-2021",
            status=HardwareStatus.IN_USE,
            assigned_to="user@test.com"
        ),
        Hardware(
            name="Razer Basilisk V2",
            brand="Razer",
            purchase_date="05-06-2021",
            status=HardwareStatus.REPAIR,
            notes="Button stuck"
        )
    ]
    for item in items:
        db.add(item)
    db.commit()
    return items


@pytest.fixture
def admin_token(client, admin_user):
    """Get JWT token for admin user."""
    response = client.post(
        "/auth/login",
        json={"email": admin_user.email, "password": "password123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def user_token(client, regular_user):
    """Get JWT token for regular user."""
    response = client.post(
        "/auth/login",
        json={"email": regular_user.email, "password": "password123"}
    )
    return response.json()["access_token"]
