import json
from pathlib import Path

from app.config import settings
from app.models.session import Session, SessionCreate, SessionUpdate
from app.services.problem_service import get_problem


def _get_sessions_dir() -> Path:
    d = Path(__file__).resolve().parent.parent.parent / settings.sessions_dir
    d.mkdir(parents=True, exist_ok=True)
    return d


def create_session(req: SessionCreate) -> Session:
    problem = get_problem(req.problem_id)
    if not problem:
        raise ValueError(f"Problem not found: {req.problem_id}")

    session = Session(
        problem_id=req.problem_id,
        code=problem.starter_code,
        time_remaining_seconds=problem.time_limit_minutes * 60,
    )
    _save_session(session)
    return session


def get_session(session_id: str) -> Session | None:
    path = _get_sessions_dir() / f"{session_id}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return Session(**json.load(f))


def update_session(session_id: str, update: SessionUpdate) -> Session | None:
    session = get_session(session_id)
    if not session:
        return None

    if update.code is not None:
        session.code = update.code
    if update.time_remaining_seconds is not None:
        session.time_remaining_seconds = update.time_remaining_seconds
    if update.status is not None:
        session.status = update.status

    _save_session(session)
    return session


def list_sessions() -> list[Session]:
    sessions_dir = _get_sessions_dir()
    sessions = []
    for path in sorted(sessions_dir.glob("*.json"), reverse=True):
        with open(path) as f:
            sessions.append(Session(**json.load(f)))
    return sessions


def _save_session(session: Session) -> None:
    path = _get_sessions_dir() / f"{session.id}.json"
    with open(path, "w") as f:
        json.dump(session.model_dump(), f, indent=2)
