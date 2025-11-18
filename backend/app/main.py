"""
Main FastAPI application
Australian Privacy Act ADM Compliance Framework
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from .core.config import settings
from .api import auth, adm_registry, pia, fairness, transparency, requests, compliance, audit, reports

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    Australian Privacy Act Automated Decision-Making (ADM) Compliance Framework

    This platform helps organisations assess, monitor, document, and demonstrate compliance
    for systems involving automated or semi-automated decision-making affecting individuals.

    ## Key Features

    * **ADM System Registry** - Catalogue and classify ADM systems
    * **Privacy Impact Assessments** - Automated PIA workflows
    * **Fairness & Bias Assessment** - Evaluate and monitor for bias
    * **Transparency Notices** - Generate APP5-compliant notices
    * **Individual Requests** - Handle explanation and review requests
    * **Compliance Monitoring** - Continuous drift and bias detection
    * **Audit & Governance** - Comprehensive audit trails and reporting

    ## Compliance Focus

    - Australian Privacy Act 1988
    - Australian Privacy Principles (APPs)
    - OAIC guidance on ADM systems
    - AI ethics and governance principles
    """,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred. Please contact support.",
            "type": type(exc).__name__
        }
    )


# Health check
@app.get("/health", tags=["System"])
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """API root"""
    return {
        "message": "Australian Privacy Act ADM Compliance Framework API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "health": "/health"
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(adm_registry.router, prefix="/api/v1/adm", tags=["ADM Registry"])
app.include_router(pia.router, prefix="/api/v1/pia", tags=["Privacy Impact Assessment"])
app.include_router(fairness.router, prefix="/api/v1/fairness", tags=["Fairness & Bias"])
app.include_router(transparency.router, prefix="/api/v1/transparency", tags=["Transparency"])
app.include_router(requests.router, prefix="/api/v1/requests", tags=["Individual Requests"])
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["Compliance Monitoring"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit & Governance"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
