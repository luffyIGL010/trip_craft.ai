from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.agent.travel_genie import TravelGenieAgent

router = APIRouter()
agent = TravelGenieAgent()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


@router.post("/api/chat")
async def chat_endpoint(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user),
):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    return await agent.chat(user_message=req.message, session_id=req.session_id, db=db)
