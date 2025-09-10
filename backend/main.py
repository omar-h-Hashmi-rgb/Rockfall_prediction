from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from datetime import datetime

from .routers import health, predictions, sensors, alerts
from .config import settings
from .db import cleanup_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title='AI-Based Rockfall Prediction API',
    description='RESTful API for rockfall risk prediction using machine learning',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc'
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Exception",
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Include routers
app.include_router(health.router)
app.include_router(predictions.router)
app.include_router(sensors.router)
app.include_router(alerts.router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI-Based Rockfall Prediction API",
        "version": "1.0.0",
        "description": "Machine learning powered rockfall risk assessment",
        "endpoints": {
            "health": "/api/health",
            "predictions": "/api/predict",
            "sensors": "/api/sensors",
            "alerts": "/api/alerts",
            "documentation": "/docs"
        },
        "timestamp": datetime.utcnow(),
        "status": "operational"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup tasks."""
    logger.info("🚀 Starting AI-Based Rockfall Prediction API")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize services
    try:
        # Test database connection
        from .db import check_db_health
        db_health = check_db_health()
        if db_health['status'] == 'healthy':
            logger.info("✅ Database connection successful")
        else:
            logger.warning("⚠️ Database connection issues")
        
        # Test model loading
        from .services.predict import health_check as model_health
        model_health_result = model_health()
        if model_health_result['status'] == 'healthy':
            logger.info("✅ ML model loaded successfully")
        else:
            logger.warning("⚠️ ML model loading issues")
        
        # Test external services
        from .services.alerts import health_check as alerts_health
        alerts_health_result = alerts_health()
        logger.info(f"Alert services status: {alerts_health_result['status']}")
        
        from .services.mapmyindia import health_check as map_health
        map_health_result = map_health()
        logger.info(f"MapMyIndia service status: {map_health_result['status']}")
        
    except Exception as e:
        logger.error(f"Startup initialization error: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks."""
    logger.info("🛑 Shutting down AI-Based Rockfall Prediction API")
    
    try:
        cleanup_db()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"Shutdown cleanup error: {e}")

# Development server command
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )