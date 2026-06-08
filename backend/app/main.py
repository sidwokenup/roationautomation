from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import structlog
import sentry_sdk
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.api.router import api_router

# Sentry integration
if getattr(settings, "SENTRY_DSN", None):
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

# Structlog config
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

# SlowAPI Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

from contextlib import asynccontextmanager
from app.db.session import engine, Base
import asyncio

async def local_scheduler():
    from app.services.rotation_scheduler import RotationSchedulerService
    logger = structlog.get_logger()
    logger.info("Starting local dev scheduler")
    
    # Run recovery once at startup
    try:
        await RotationSchedulerService.recover_jobs()
    except Exception as e:
        logger.error("Local scheduler recovery failed", error=str(e))
        
    while True:
        await asyncio.sleep(60)
        try:
            logger.info("Local scheduler: dispatching rotations")
            await RotationSchedulerService.dispatch_due_jobs()
        except Exception as e:
            logger.error("Local scheduler dispatch failed", error=str(e))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables for local testing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    scheduler_task = None
    if settings.DEV_MODE:
        scheduler_task = asyncio.create_task(local_scheduler())
        
    yield
    
    if scheduler_task:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": traceback.format_exc()}
    )

app.add_middleware(SlowAPIMiddleware)  # Rate limiting


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if not settings.DEV_MODE:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
@limiter.limit("10/minute")
def root(request: Request):
    logger = structlog.get_logger()
    logger.info("root_accessed", endpoint="/")
    return {"message": "Welcome to Palladium Automation API"}