from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import SessionLocal
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health")
async def health() -> HealthResponse:
    async with SessionLocal() as session:
        await session.execute(text("SELECT 1"))

    return HealthResponse(status="ok", database="ok")
