from fastapi import APIRouter

from app.rag.answer import Answer, ask
from app.schemas.ask import AskRequest

router = APIRouter()


@router.post("/ask")
async def ask_question(request: AskRequest) -> Answer:
    return await ask(request.question)
