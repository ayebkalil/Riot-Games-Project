from fastapi import APIRouter

from api.schemas.progression import ProgressionFeatures, ProgressionPrediction
from api.services.progression_service import predict_progression


router = APIRouter(prefix="/progression", tags=["progression"])


@router.post("/predict", response_model=ProgressionPrediction)
def predict_progression_route(features: ProgressionFeatures) -> ProgressionPrediction:
    prediction = predict_progression(features)
    return ProgressionPrediction(predicted_delta_winrate=prediction)
