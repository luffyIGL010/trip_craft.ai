from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.db import crud

router = APIRouter()


@router.get("/api/sessions")
async def get_sessions(
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user),
):
    sessions = await crud.list_sessions(db)
    return [
        {"id": s.id, "title": s.title, "updated_at": s.updated_at.isoformat() if s.updated_at else None}
        for s in sessions
    ]


@router.get("/api/sessions/{session_id}/messages")
async def get_session_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user),
):
    msgs = await crud.get_session_messages(db, session_id)
    return [
        {"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
        for m in msgs
    ]


@router.delete("/api/sessions/{session_id}")
async def remove_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_user),
):
    ok = await crud.delete_session(db, session_id)
    return {"success": ok}
