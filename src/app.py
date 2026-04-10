from __future__ import annotations

from fastapi import FastAPI

from src.claims.adapters.api import router as claims_router
from src.adjudication.adapters.api import router as adjudication_router


def create_app() -> FastAPI:
    app = FastAPI(title="PFML")
    app.include_router(claims_router)
    app.include_router(adjudication_router)
    return app
