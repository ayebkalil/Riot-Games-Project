from fastapi import APIRouter, HTTPException

from api.schemas.rank import RankClassificationFeatures, RankClassificationPrediction
from api.services.rank_service import predict_rank_tier


router = APIRouter(prefix="/rank", tags=["rank"])


@router.post("/predict", response_model=RankClassificationPrediction)
def predict_rank(features: RankClassificationFeatures) -> RankClassificationPrediction:
    try:
        class_name, class_index = predict_rank_tier(features)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return RankClassificationPrediction(predicted_tier=class_name, predicted_class_index=class_index)
