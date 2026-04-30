"""Configuration management using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Database
    database_url: str = "sqlite:///./app.db"
    
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 1
    
    # Gemini API
    gemini_api_key: str = ""
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
