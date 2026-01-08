import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.middleware import configure_middleware
from contextlib import asynccontextmanager
from app.api.v1.api import api_router
from app.core.database import Base, engine


configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AKM SIR BIO API", version=settings.version)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")
    yield
    # Shutdown
    logger.info("Shutting down AKM SIR BIO API")


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="AKM SIR BIO API",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    lifespan=lifespan,
)

configure_middleware(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)
os.makedirs("uploads", exist_ok=True)
app.mount(f"{settings.api_v1_prefix}/static", StaticFiles(directory="uploads"), name="static")

@app.get(f"{settings.api_v1_prefix}/", tags=["root"])
async def root():
    return{
        "message":"AKM SIR BIO API",
        "version":settings.version,
        "docs":f"{settings.api_v1_prefix}/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
       "app.main:app",
        host=settings.host,
        port=settings.port, 
        reload=settings.debug,
        workers= 1 if settings.debug else settings.workers,
        log_level=settings.log_level.lower(),
    )


