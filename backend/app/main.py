# backend/app/main.py
from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="AI Medical Coding & Cashless Claims Automation Assistant",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Application startup complete")