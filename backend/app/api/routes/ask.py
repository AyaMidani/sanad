from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import func, select
from voyageai.error import RateLimitError

from app.db.models import AskLog
from app.db.session import SessionLocal
from app.rag.answer import Answer, ask
from app.schemas.ask import AskRequest

router = APIRouter()

MAX_QUESTIONS_PER_HOUR = 10


@router.post("/ask")
async def ask_question(body: AskRequest, request: Request) -> Answer:
    forwarded = request.headers.get("x-forwarded-for")
    ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

    async with SessionLocal() as session:
        count = await session.scalar(
            select(func.count())
            .select_from(AskLog)
            .where(AskLog.ip == ip, AskLog.created_at > one_hour_ago)
        )
        if count >= MAX_QUESTIONS_PER_HOUR:
            raise HTTPException(
                status_code=429,
                detail="Too many questions. Please try again in an hour.",
            )
        session.add(AskLog(ip=ip))
        await session.commit()

    try:
        return await ask(body.question)
    except RateLimitError:
        raise HTTPException(
            status_code=503,
            detail="Sanad is busy right now. Please try again in a minute.",
        )
