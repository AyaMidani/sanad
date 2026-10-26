import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.ask import SourceOut


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    created_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: str
    text: str
    sources: list[SourceOut] | None
