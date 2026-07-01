from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.exceptions import register_exception_handlers
from src.core.database import engine
from src.api.v1 import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    description="Система обработки платежей",
    lifespan=lifespan,
)
register_exception_handlers(app)

app.include_router(router)
