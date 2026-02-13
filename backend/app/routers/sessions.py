from fastapi import APIRouter, HTTPException

from app.models.session import Session, SessionCreate, SessionUpdate
from app.services.session_service import (
    create_session,
    get_session,
    update_session,
    list_sessions,
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=Session)
def create_new_session(req: SessionCreate):
    try:
        return create_session(req)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", response_model=list[Session])
def get_all_sessions():
    return list_sessions()


@router.get("/{session_id}", response_model=Session)
def get_session_detail(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/{session_id}", response_model=Session)
def update_existing_session(session_id: str, update: SessionUpdate):
    session = update_session(session_id, update)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
