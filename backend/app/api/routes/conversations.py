import uuid

from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import select

from app.db.models import ChatMessage, Conversation
from app.db.session import SessionLocal
from app.schemas.conversations import ConversationOut, MessageOut

router = APIRouter(prefix="/conversations")


@router.get("")
async def list_conversations(
    x_visitor_id: str = Header(min_length=8, max_length=64),
) -> list[ConversationOut]:
    async with SessionLocal() as session:
        rows = await session.scalars(
            select(Conversation)
            .where(Conversation.visitor_id == x_visitor_id)
            .order_by(Conversation.created_at.desc())
        )
        return [ConversationOut.model_validate(c) for c in rows]


@router.get("/{conversation_id}/messages")
async def list_messages(
    conversation_id: uuid.UUID,
    x_visitor_id: str = Header(min_length=8, max_length=64),
) -> list[MessageOut]:
    async with SessionLocal() as session:
        conversation = await session.get(Conversation, conversation_id)
        if conversation is None or conversation.visitor_id != x_visitor_id:
            raise HTTPException(status_code=404, detail="Conversation not found.")

        rows = await session.scalars(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.id)
        )
        return [MessageOut.model_validate(m) for m in rows]


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: uuid.UUID,
    x_visitor_id: str = Header(min_length=8, max_length=64),
) -> None:
    async with SessionLocal() as session:
        conversation = await session.get(Conversation, conversation_id)
        if conversation is None or conversation.visitor_id != x_visitor_id:
            raise HTTPException(status_code=404, detail="Conversation not found.")

        await session.delete(conversation)
        await session.commit()
