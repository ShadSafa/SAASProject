from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import auth, profile, instagram, scans
from app.tasks.token_refresh import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle management."""
    # Startup: start background scheduler
    start_scheduler()
    yield
    # Shutdown: stop scheduler gracefully
    stop_scheduler()


# Create FastAPI application with lifespan
app = FastAPI(
    title="Instagram Viral Content Analyzer",
    description="API for analyzing viral Instagram content",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Include routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(instagram.router)
app.include_router(scans.router)
