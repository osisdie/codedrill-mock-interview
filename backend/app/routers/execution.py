from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.executor import execute_run, execute_submit, ExecutionError

router = APIRouter(prefix="/api/execute", tags=["execution"])


class ExecuteRequest(BaseModel):
    session_id: str


@router.post("/run")
def run_code_endpoint(req: ExecuteRequest):
    try:
        return execute_run(req.session_id)
    except ExecutionError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/submit")
def submit_code_endpoint(req: ExecuteRequest):
    try:
        return execute_submit(req.session_id)
    except ExecutionError as e:
        raise HTTPException(status_code=404, detail=str(e))
