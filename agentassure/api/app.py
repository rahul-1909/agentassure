"""FastAPI Application Factory and Server Entrypoint."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from agentassure.api.deps import limiter
from agentassure.api.routers import (
    auth_router,
    failure_router,
    health_router,
    release_gate_router,
    reporting_router,
    review_router,
    sampling_router,
    simulator_router,
    ticketing_router,
)
from agentassure.config import settings
from agentassure.db.seed_data import seed_database
from agentassure.db.session import SessionLocal, init_db
from agentassure.utils.logging import get_logger

logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager to initialize DB tables and seed baseline data."""
    logger.info("Initializing AgentAssure database schema...")
    init_db()

    logger.info("Seeding enterprise mock data, personas, and rubrics...")
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    logger.info("AgentAssure backend initialized successfully.")
    yield
    logger.info("AgentAssure backend shutting down...")


def create_app() -> FastAPI:
    """FastAPI application factory configuring middleware, routes, and rate limits."""
    application = FastAPI(
        title="AgentAssure API",
        description=(
            "Human-in-the-Loop QA Workflow, Regression Testing & "
            "Closed-Loop Improvement System for Conversational AI."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Attach SlowAPI limiter state and error handler
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global Exception Handler
    @application.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    # Mount Routers
    application.include_router(health_router)
    api_prefix = settings.API_V1_PREFIX
    application.include_router(auth_router, prefix=api_prefix)
    application.include_router(review_router, prefix=api_prefix)
    application.include_router(sampling_router, prefix=api_prefix)
    application.include_router(failure_router, prefix=api_prefix)
    application.include_router(simulator_router, prefix=api_prefix)
    application.include_router(release_gate_router, prefix=api_prefix)
    application.include_router(ticketing_router, prefix=api_prefix)
    application.include_router(reporting_router, prefix=api_prefix)

    # Serve built React UI if available
    dist_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    if dist_dir.exists():
        application.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")

    return application


app = create_app()
