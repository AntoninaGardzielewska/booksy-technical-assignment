"""Database connection and session management."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.config import settings
from backend.models import Base
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database and create all tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")


def reset_db():
    """Reset database - drops all tables and recreates them."""
    Base.metadata.drop_all(bind=engine)
    init_db()
    logger.info("Database reset")


# Enable foreign keys for SQLite
if "sqlite" in settings.database_url:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
