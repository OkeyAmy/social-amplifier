"""
Social Amplifier Backend - Main Application Entry Point
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

from app.core.config import settings
from app.api.routes import auth, generate, publish, drafts

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Social Amplifier API",
    description="AI-powered social media content generation and publishing platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - Must be before route includes
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(generate.router, prefix="/api/v1/generate", tags=["Content Generation"])
app.include_router(publish.router, prefix="/api/v1/publish", tags=["Publishing"])
app.include_router(drafts.router, prefix="/api/v1/drafts", tags=["Drafts"])


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Social Amplifier API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "social-amplifier-api",
        "cors_origins": settings.CORS_ORIGINS
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
