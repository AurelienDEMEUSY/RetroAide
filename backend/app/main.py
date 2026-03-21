"""Application FastAPI RetroAide."""

from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.logging_config import setup_logging

setup_logging()

from app.routers import analyze, glossary

logger = logging.getLogger(__name__)


def _cors_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "http://localhost:3000")
    return [x.strip() for x in raw.split(",") if x.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== RetroAide API démarrage | version=0.1.0 ===")
    logger.info("CORS allow_origins=%s", _cors_origins())
    logger.info("LOG_LEVEL=%r", os.environ.get("LOG_LEVEL", "DEBUG (défaut)"))
    yield
    logger.info("=== RetroAide API arrêt ===")


app = FastAPI(title="RetroAide API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(analyze.router, prefix="/api/v1")
app.include_router(glossary.router, prefix="/api/v1")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Chaque requête HTTP est journalisée (visible dans docker compose logs)."""
    path = request.url.path
    logger.info("→ %s %s | client=%s", request.method, path, request.client.host if request.client else "?")
    t0 = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        logger.exception("✗ %s %s | erreur après %.1f ms", request.method, path, elapsed_ms)
        raise
    elapsed_ms = (time.perf_counter() - t0) * 1000
    logger.info(
        "← %s %s | status=%s | %.1f ms",
        request.method,
        path,
        response.status_code,
        elapsed_ms,
    )
    return response
