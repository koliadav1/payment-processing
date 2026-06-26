from collections.abc import AsyncGenerator
from typing import Annotated
from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ForbiddenError
from src.core.database import session_maker
from src.core.config import settings
from src.repositories.unit_of_work import SQLAlchUnitOfWork


async def get_uow():
    return SQLAlchUnitOfWork(session_maker)


async def verify_api_key(
    x_api_key: Annotated[
        str,
        Header(..., description="Ключ для доступа к API", alias="X-API-Key"),
    ],
):
    """Проверка API ключа"""
    if x_api_key != settings.API_KEY:
        raise ForbiddenError("Wrong X-API-Key, Forbidden")

    return True
