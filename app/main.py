import os
import logging
import asyncio
import uvicorn
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
# Import our middleware
from fastapi.middleware.cors import CORSMiddleware
from .infrastructure.multipart_limit_middleware import MultipartLimitMiddleware
from .infrastructure.logging import setup_logging, RequestLoggingMiddleware
from .infrastructure.metrics import PrometheusMiddleware, metrics_endpoint
from .config import settings
# Import adapter classes
from .adapters.token_service.tiktoken_service import TikTokenService
from .adapters.document_processor.simple_spacy_layout import SimpleSpacyLayoutProcessor
from .adapters.auth_service.simple_auth_service import SimpleAuthService
# Imports for routers
from .api.routes.documents import router as documents_router

app = FastAPI(
    title="BrainDrive Document Processing AI",
    description="Standalone document processing service for BrainDrive",
    version="0.1.0",
    debug=settings.DEBUG
)

# Setup logging early
setup_logging()
logger = logging.getLogger(__name__)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)

# CORS (if frontend served separately)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint for Cloud Run
@app.get("/health")
async def health_check():
    """Health check endpoint for Google Cloud Run"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "BrainDrive Document AI",
            "version": "0.1.0"
        }
    )

# Include metrics endpoint
@app.get("/metrics")
async def metrics():
    return await metrics_endpoint()

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "BrainDrive Document Processing AI",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
            "upload": "/documents/upload"
        }
    }

# On startup, instantiate and store singleton adapter instances in app.state
@app.on_event("startup")
async def on_startup():
    logger.info("Application startup: instantiating adapters...")
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    
    try:
        # Auth service
        app.state.auth_service = SimpleAuthService(
            api_key=settings.auth_api_key.get_secret_value(),
            jwt_secret=settings.jwt_secret.get_secret_value(),
        )
        # Token service
        token_service = TikTokenService()
        
        # Document processor - this will fail fast if spaCy model is not available
        app.state.document_processor = SimpleSpacyLayoutProcessor(
            spacy_model=settings.spacy_model,
            token_service=token_service,
        )
        
        logger.info("Startup complete: adapters instantiated successfully")
    except Exception as e:
        logger.error(f"Failed to initialize adapters: {e}")
        raise  # This will prevent the application from starting

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Application shutdown: closing resources...")
    logger.info("Shutdown complete.")

app.include_router(
    documents_router,
    prefix="/documents",
    tags=["documents"]
)
