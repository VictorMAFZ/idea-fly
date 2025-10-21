"""
Health check and monitoring endpoints for IdeaFly Backend.

Provides comprehensive health checks, metrics, and monitoring
endpoints for production deployment and observability.
"""

import os
import sys
import time
import psutil
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..core.logging import StructuredLogger, default_logger, LogCategory
from ..core.config import get_settings


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class HealthStatus(BaseModel):
    """Health status response model."""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment name")
    uptime_seconds: float = Field(..., description="Application uptime in seconds")
    checks: Dict[str, Any] = Field(..., description="Individual health checks")


class DatabaseHealthCheck(BaseModel):
    """Database health check model."""
    status: str = Field(..., description="Database status")
    response_time_ms: float = Field(..., description="Database response time in ms")
    connection_pool: Dict[str, Any] = Field(..., description="Connection pool stats")


class SystemMetrics(BaseModel):
    """System metrics model."""
    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_percent: float = Field(..., description="Memory usage percentage")
    memory_used_mb: float = Field(..., description="Memory used in MB")
    memory_total_mb: float = Field(..., description="Total memory in MB")
    disk_usage_percent: float = Field(..., description="Disk usage percentage")
    disk_free_gb: float = Field(..., description="Free disk space in GB")
    load_average: List[float] = Field(..., description="System load average")


class ApplicationMetrics(BaseModel):
    """Application metrics model."""
    process_id: int = Field(..., description="Process ID")
    threads_count: int = Field(..., description="Number of threads")
    open_files: int = Field(..., description="Number of open files")
    memory_rss_mb: float = Field(..., description="Resident memory in MB")
    memory_vms_mb: float = Field(..., description="Virtual memory in MB")
    cpu_percent: float = Field(..., description="Process CPU percentage")
    start_time: datetime = Field(..., description="Process start time")


class MetricsResponse(BaseModel):
    """Complete metrics response."""
    timestamp: datetime = Field(..., description="Metrics collection timestamp")
    system: SystemMetrics = Field(..., description="System metrics")
    application: ApplicationMetrics = Field(..., description="Application metrics")


# ============================================================================
# GLOBAL STATE
# ============================================================================

# Track application start time
_app_start_time = time.time()
_process = psutil.Process()

# Settings
settings = get_settings()


# ============================================================================
# HEALTH CHECK FUNCTIONS
# ============================================================================

async def check_database_health(db: AsyncSession) -> DatabaseHealthCheck:
    """
    Check database connectivity and performance.
    
    Args:
        db: Database session
        
    Returns:
        Database health check result
    """
    try:
        start_time = time.time()
        
        # Execute simple query
        result = await db.execute(text("SELECT 1"))
        await result.fetchone()
        
        response_time_ms = (time.time() - start_time) * 1000
        
        # Get connection pool stats (if available)
        pool_stats = {}
        if hasattr(db.bind, 'pool'):
            pool = db.bind.pool
            pool_stats = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid()
            }
        
        return DatabaseHealthCheck(
            status="healthy",
            response_time_ms=response_time_ms,
            connection_pool=pool_stats
        )
        
    except Exception as e:
        default_logger.error(
            f"Database health check failed: {str(e)}",
            category=LogCategory.ERROR,
            error=e
        )
        return DatabaseHealthCheck(
            status="unhealthy",
            response_time_ms=0,
            connection_pool={}
        )


def check_disk_space() -> Dict[str, Any]:
    """Check disk space availability."""
    try:
        disk_usage = psutil.disk_usage('/')
        return {
            "status": "healthy" if disk_usage.percent < 90 else "warning",
            "used_percent": disk_usage.percent,
            "free_gb": disk_usage.free / (1024 ** 3),
            "total_gb": disk_usage.total / (1024 ** 3)
        }
    except Exception as e:
        default_logger.error(f"Disk space check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def check_memory() -> Dict[str, Any]:
    """Check memory usage."""
    try:
        memory = psutil.virtual_memory()
        return {
            "status": "healthy" if memory.percent < 85 else "warning",
            "used_percent": memory.percent,
            "available_gb": memory.available / (1024 ** 3),
            "total_gb": memory.total / (1024 ** 3)
        }
    except Exception as e:
        default_logger.error(f"Memory check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def check_cpu() -> Dict[str, Any]:
    """Check CPU usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        
        return {
            "status": "healthy" if cpu_percent < 80 else "warning",
            "usage_percent": cpu_percent,
            "core_count": cpu_count,
            "load_average": load_avg
        }
    except Exception as e:
        default_logger.error(f"CPU check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def check_application_health() -> Dict[str, Any]:
    """Check application-specific health indicators."""
    try:
        # Check if critical environment variables are set
        required_env_vars = ["JWT_SECRET_KEY", "DATABASE_URL"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        # Check file system permissions
        temp_dir = Path("/tmp") if os.name != "nt" else Path.cwd()
        can_write = os.access(temp_dir, os.W_OK)
        
        status = "healthy"
        issues = []
        
        if missing_vars:
            status = "unhealthy"
            issues.append(f"Missing environment variables: {', '.join(missing_vars)}")
        
        if not can_write:
            status = "warning"
            issues.append("Cannot write to temporary directory")
        
        return {
            "status": status,
            "issues": issues,
            "environment_ok": len(missing_vars) == 0,
            "filesystem_ok": can_write
        }
        
    except Exception as e:
        default_logger.error(f"Application health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# ============================================================================
# METRICS COLLECTION
# ============================================================================

def get_system_metrics() -> SystemMetrics:
    """Collect system-level metrics."""
    # CPU metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    # Memory metrics
    memory = psutil.virtual_memory()
    
    # Disk metrics
    disk = psutil.disk_usage('/')
    
    # Load average (Unix-like systems only)
    try:
        load_avg = list(os.getloadavg()) if hasattr(os, 'getloadavg') else [0.0, 0.0, 0.0]
    except (OSError, AttributeError):
        load_avg = [0.0, 0.0, 0.0]
    
    return SystemMetrics(
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        memory_used_mb=memory.used / (1024 ** 2),
        memory_total_mb=memory.total / (1024 ** 2),
        disk_usage_percent=disk.percent,
        disk_free_gb=disk.free / (1024 ** 3),
        load_average=load_avg
    )


def get_application_metrics() -> ApplicationMetrics:
    """Collect application-level metrics."""
    # Process memory info
    memory_info = _process.memory_info()
    
    # Process CPU usage
    cpu_percent = _process.cpu_percent()
    
    # Process creation time
    create_time = datetime.fromtimestamp(_process.create_time(), tz=timezone.utc)
    
    # Thread count
    try:
        num_threads = _process.num_threads()
    except (psutil.AccessDenied, AttributeError):
        num_threads = 0
    
    # Open files count
    try:
        num_fds = _process.num_fds() if hasattr(_process, 'num_fds') else len(_process.open_files())
    except (psutil.AccessDenied, AttributeError):
        num_fds = 0
    
    return ApplicationMetrics(
        process_id=_process.pid,
        threads_count=num_threads,
        open_files=num_fds,
        memory_rss_mb=memory_info.rss / (1024 ** 2),
        memory_vms_mb=memory_info.vms / (1024 ** 2),
        cpu_percent=cpu_percent,
        start_time=create_time
    )


# ============================================================================
# ROUTER SETUP
# ============================================================================

# Create router for health and monitoring endpoints
health_router = APIRouter(
    prefix="/health",
    tags=["Health & Monitoring"],
    responses={
        503: {"description": "Service Unavailable"},
        500: {"description": "Internal Server Error"}
    }
)

metrics_router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
    responses={
        500: {"description": "Internal Server Error"}
    }
)


# ============================================================================
# HEALTH ENDPOINTS
# ============================================================================

@health_router.get(
    "/",
    response_model=HealthStatus,
    summary="Basic Health Check",
    description="Returns basic application health status"
)
async def health_check():
    """Basic health check endpoint."""
    current_time = datetime.now(timezone.utc)
    uptime = time.time() - _app_start_time
    
    return HealthStatus(
        status="healthy",
        timestamp=current_time,
        version=getattr(settings, 'version', '1.0.0'),
        environment=getattr(settings, 'environment', 'development'),
        uptime_seconds=uptime,
        checks={}
    )


@health_router.get(
    "/ready",
    response_model=HealthStatus,
    summary="Readiness Check",
    description="Returns readiness status including database connectivity"
)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check with database connectivity."""
    current_time = datetime.now(timezone.utc)
    uptime = time.time() - _app_start_time
    
    # Perform health checks
    db_health = await check_database_health(db)
    app_health = check_application_health()
    
    # Determine overall status
    checks = {
        "database": db_health.dict(),
        "application": app_health
    }
    
    # Overall status is unhealthy if any critical check fails
    overall_status = "healthy"
    if (db_health.status == "unhealthy" or 
        app_health["status"] == "unhealthy"):
        overall_status = "unhealthy"
    
    status_code = status.HTTP_200_OK if overall_status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    health_status = HealthStatus(
        status=overall_status,
        timestamp=current_time,
        version=getattr(settings, 'version', '1.0.0'),
        environment=getattr(settings, 'environment', 'development'),
        uptime_seconds=uptime,
        checks=checks
    )
    
    # Log health check results
    default_logger.info(
        f"Readiness check completed: {overall_status}",
        category=LogCategory.MONITORING,
        status=overall_status,
        checks=checks
    )
    
    return JSONResponse(
        status_code=status_code,
        content=health_status.dict()
    )


@health_router.get(
    "/live",
    summary="Liveness Check",
    description="Simple liveness check for Kubernetes probes"
)
async def liveness_check():
    """Simple liveness check."""
    return {"status": "alive", "timestamp": datetime.now(timezone.utc)}


@health_router.get(
    "/detailed",
    response_model=HealthStatus,
    summary="Detailed Health Check",
    description="Comprehensive health check including system resources"
)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check including system resources."""
    current_time = datetime.now(timezone.utc)
    uptime = time.time() - _app_start_time
    
    # Perform all health checks
    db_health = await check_database_health(db)
    app_health = check_application_health()
    disk_health = check_disk_space()
    memory_health = check_memory()
    cpu_health = check_cpu()
    
    checks = {
        "database": db_health.dict(),
        "application": app_health,
        "disk": disk_health,
        "memory": memory_health,
        "cpu": cpu_health
    }
    
    # Determine overall status
    unhealthy_checks = [
        name for name, check in checks.items()
        if check.get("status") == "unhealthy"
    ]
    
    if unhealthy_checks:
        overall_status = "unhealthy"
    else:
        warning_checks = [
            name for name, check in checks.items()
            if check.get("status") == "warning"
        ]
        overall_status = "warning" if warning_checks else "healthy"
    
    status_code = (
        status.HTTP_200_OK if overall_status == "healthy" else
        status.HTTP_503_SERVICE_UNAVAILABLE
    )
    
    health_status = HealthStatus(
        status=overall_status,
        timestamp=current_time,
        version=getattr(settings, 'version', '1.0.0'),
        environment=getattr(settings, 'environment', 'development'),
        uptime_seconds=uptime,
        checks=checks
    )
    
    return JSONResponse(
        status_code=status_code,
        content=health_status.dict()
    )


# ============================================================================
# METRICS ENDPOINTS
# ============================================================================

@metrics_router.get(
    "/",
    response_model=MetricsResponse,
    summary="Application Metrics",
    description="Returns system and application metrics"
)
async def get_metrics():
    """Get application and system metrics."""
    current_time = datetime.now(timezone.utc)
    
    try:
        system_metrics = get_system_metrics()
        app_metrics = get_application_metrics()
        
        metrics = MetricsResponse(
            timestamp=current_time,
            system=system_metrics,
            application=app_metrics
        )
        
        # Log metrics collection
        default_logger.info(
            "Metrics collected",
            category=LogCategory.MONITORING,
            cpu_percent=system_metrics.cpu_percent,
            memory_percent=system_metrics.memory_percent,
            disk_usage_percent=system_metrics.disk_usage_percent
        )
        
        return metrics
        
    except Exception as e:
        default_logger.error(
            f"Failed to collect metrics: {str(e)}",
            category=LogCategory.ERROR,
            error=e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to collect metrics"
        )


@metrics_router.get(
    "/prometheus",
    summary="Prometheus Metrics",
    description="Returns metrics in Prometheus format"
)
async def get_prometheus_metrics():
    """Get metrics in Prometheus format."""
    try:
        system_metrics = get_system_metrics()
        app_metrics = get_application_metrics()
        
        # Format as Prometheus metrics
        prometheus_output = f"""# HELP ideafly_cpu_percent CPU usage percentage
# TYPE ideafly_cpu_percent gauge
ideafly_cpu_percent {system_metrics.cpu_percent}

# HELP ideafly_memory_percent Memory usage percentage  
# TYPE ideafly_memory_percent gauge
ideafly_memory_percent {system_metrics.memory_percent}

# HELP ideafly_disk_percent Disk usage percentage
# TYPE ideafly_disk_percent gauge
ideafly_disk_percent {system_metrics.disk_usage_percent}

# HELP ideafly_process_memory_rss Process resident memory in bytes
# TYPE ideafly_process_memory_rss gauge
ideafly_process_memory_rss {app_metrics.memory_rss_mb * 1024 * 1024}

# HELP ideafly_process_cpu_percent Process CPU percentage
# TYPE ideafly_process_cpu_percent gauge
ideafly_process_cpu_percent {app_metrics.cpu_percent}

# HELP ideafly_process_threads Process thread count
# TYPE ideafly_process_threads gauge
ideafly_process_threads {app_metrics.threads_count}

# HELP ideafly_process_open_files Process open file descriptors
# TYPE ideafly_process_open_files gauge
ideafly_process_open_files {app_metrics.open_files}

# HELP ideafly_uptime_seconds Application uptime in seconds
# TYPE ideafly_uptime_seconds counter
ideafly_uptime_seconds {time.time() - _app_start_time}
"""
        
        return JSONResponse(
            content=prometheus_output,
            media_type="text/plain"
        )
        
    except Exception as e:
        default_logger.error(
            f"Failed to generate Prometheus metrics: {str(e)}",
            category=LogCategory.ERROR,
            error=e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate metrics"
        )


# ============================================================================
# INCLUDE ROUTERS FUNCTION
# ============================================================================

def include_health_routers(app):
    """Include health and metrics routers in the FastAPI app."""
    app.include_router(health_router)
    app.include_router(metrics_router)