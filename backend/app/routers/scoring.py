from fastapi import APIRouter, HTTPException

from app.models.scoring import EvaluationRequest, EvaluationResult
from app.services.scoring_service import evaluate_session

router = APIRouter(prefix="/api/scoring", tags=["scoring"])


@router.post("/evaluate", response_model=EvaluationResult)
async def evaluate(req: EvaluationRequest):
    try:
        return await evaluate_session(req.session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
