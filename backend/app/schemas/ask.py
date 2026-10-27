import uuid
from typing import Literal

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    conversation_id: uuid.UUID | None = None
    segment: Literal["wajaha", "aayan", "standard", "business"] | None = None


class SourceOut(BaseModel):
    number: int
    file: str
    title: str


class AskResponse(BaseModel):
    conversation_id: uuid.UUID
    text: str
    sources: list[SourceOut]
