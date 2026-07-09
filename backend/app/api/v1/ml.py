from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.services.stress_service import stress_service
from pydantic import BaseModel

router = APIRouter(prefix="/ml", tags=["ml"])

class StressScoreRequest(BaseModel):
    hr_variability: float
    motion_intensity: float
    time_of_day: str

class DistressAudioRequest(BaseModel):
    embedding: list[float]

@router.post("/stress-score")
def get_stress_score(payload: StressScoreRequest, current_user: dict = Depends(get_current_user)):
    """Proxy stress score calculation to SageMaker Random Forest model"""
    score, risk = stress_service.get_stress_score(
        payload.hr_variability,
        payload.motion_intensity,
        payload.time_of_day
    )
    return {
        "stress_index": score,
        "risk_level": risk
    }

@router.post("/distress-classify")
def classify_distress_audio(payload: DistressAudioRequest, current_user: dict = Depends(get_current_user)):
    """Proxy audio classification to SageMaker CNN model"""
    is_distress, confidence = stress_service.classify_distress_audio(payload.embedding)
    return {
        "is_distress": is_distress,
        "confidence": confidence
    }
