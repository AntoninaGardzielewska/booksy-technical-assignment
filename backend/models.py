"""SQLAlchemy models for the application."""
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class HardwareStatus(str, enum.Enum):
    """Enum for hardware status."""
    AVAILABLE = "Available"
    IN_USE = "In Use"
    REPAIR = "Repair"


class UserRole(str, enum.Enum):
    """Enum for user roles."""
    ADMIN = "admin"
    USER = "user"


class Hardware(Base):
    """Hardware item model."""
    
    __tablename__ = "hardware"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    brand = Column(String(255), nullable=False)
    purchase_date = Column(String(10), nullable=False)  # DD-MM-YYYY format
    status = Column(Enum(HardwareStatus), default=HardwareStatus.AVAILABLE, nullable=False)
    notes = Column(String(500), nullable=True)
    assigned_to = Column(String(255), nullable=True)  # User email
    
    # Relationships
    rentals = relationship("Rental", back_populates="hardware", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Hardware(id={self.id}, name={self.name}, status={self.status})>"


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    rentals = relationship("Rental", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class Rental(Base):
    """Rental transaction model."""
    
    __tablename__ = "rentals"
    
    id = Column(Integer, primary_key=True, index=True)
    hardware_id = Column(Integer, ForeignKey("hardware.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    rented_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    returned_at = Column(DateTime, nullable=True)
    
    # Relationships
    hardware = relationship("Hardware", back_populates="rentals")
    user = relationship("User", back_populates="rentals")
    
    def __repr__(self):
        return f"<Rental(id={self.id}, hardware_id={self.hardware_id}, user_id={self.user_id})>"
