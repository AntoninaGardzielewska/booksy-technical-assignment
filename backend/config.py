"""Configuration management using Pydantic Settings."""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import json

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
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v
    # Environment
    environment: str = "development"

    admin_initial_email: str = ""
    admin_initial_password: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False

    

settings = Settings()
