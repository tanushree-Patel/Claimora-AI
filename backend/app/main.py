# backend/app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.codes import router as codes_router
from app.api.v1.documents import router as documents_router
from app.api.v1.health import router as health_router
from app.core.logging import configure_logging, get_logger
from app.graph.checkpointer import close_checkpointer, init_checkpointer

configure_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_checkpointer()
    logger.info("Application startup complete")
    yield
    await close_checkpointer()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="AI Medical Coding & Cashless Claims Automation Assistant",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(codes_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")



