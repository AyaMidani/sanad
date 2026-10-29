from dataclasses import asdict
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy import func, select
from voyageai.error import RateLimitError

from app.db.models import AskLog, ChatMessage, Conversation
from app.db.session import SessionLocal
from app.rag.agent import ask_agent
from app.rag.answer import ask
from app.schemas.ask import AskRequest, AskResponse

router = APIRouter()

MAX_QUESTIONS_PER_HOUR = 10
USE_AGENT = True


@router.post("/ask")
async def ask_question(
    body: AskRequest,
    request: Request,
    x_visitor_id: str = Header(min_length=8, max_length=64),
) -> AskResponse:
    forwarded = request.headers.get("x-forwarded-for")
    ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
    one_hour_ago = datetime.now(UTC) - timedelta(hours=1)

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

        if body.conversation_id:
            conversation = await session.get(Conversation, body.conversation_id)
            if conversation is None or conversation.visitor_id != x_visitor_id:
                raise HTTPException(status_code=404, detail="Conversation not found.")
        else:
            conversation = Conversation(
                visitor_id=x_visitor_id, title=body.question[:60]
            )
            session.add(conversation)

        await session.flush()
        session.add(
            ChatMessage(
                conversation_id=conversation.id, role="user", text=body.question
            )
        )
        await session.commit()
        conversation_id = conversation.id

    try:
        if USE_AGENT:
            answer = await ask_agent(body.question, body.segment)
        else:
            answer = await ask(body.question, body.segment)
    except RateLimitError:
        raise HTTPException(
            status_code=503,
            detail="Sanad is busy right now. Please try again in a minute.",
        )

    sources = [asdict(s) for s in answer.sources]
    async with SessionLocal() as session:
        session.add(
            ChatMessage(
                conversation_id=conversation_id,
                role="assistant",
                text=answer.text,
                sources=sources,
            )
        )
        await session.commit()

    return AskResponse(
        conversation_id=conversation_id, text=answer.text, sources=sources
    )
