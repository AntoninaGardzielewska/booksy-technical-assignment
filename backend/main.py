"""Main FastAPI application."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import logging
import os
from backend.config import settings
from backend.database import init_db, get_db, SessionLocal
from backend.seeder import seed_database
from backend.routes import auth, admin, dashboard, search

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Hardware Rental Management System",
    description="A system for managing hardware rentals with admin controls and AI-powered search",
    version="1.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Event Handlers ============
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting up application...")
    
    # Initialize database
    init_db()
    
    # Seed database if empty
    db = SessionLocal()
    try:
        from backend.models import User
        user_count = db.query(User).count()
        if user_count == 0:
            logger.info("Seeding database with initial data...")
            seed_database(db)
    finally:
        db.close()
    
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("Shutting down application...")


# ============ Include Routes ============
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(dashboard.router)
app.include_router(search.router)


# ============ Root Endpoints ============
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Hardware Rental Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# ============ Error Handlers ============
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    logger.error(f"HTTP Exception: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail
        }
    )


# ============ Serve Frontend (if built) ============
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/static", StaticFiles(directory=frontend_dist), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve SPA application."""
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        # Return index.html for all routes (SPA fallback)
        return FileResponse(os.path.join(frontend_dist, "index.html"))


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )
