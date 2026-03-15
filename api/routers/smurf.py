from fastapi import APIRouter

from api.schemas.smurf import SmurfDetectionFeatures, SmurfDetectionPrediction
from api.services.smurf_service import predict_smurf_anomaly


router = APIRouter(prefix="/smurf", tags=["smurf"])


@router.post("/predict", response_model=SmurfDetectionPrediction)
def predict_smurf(features: SmurfDetectionFeatures) -> SmurfDetectionPrediction:
    is_smurf_anomaly, anomaly_score, predicted_label = predict_smurf_anomaly(features)
    return SmurfDetectionPrediction(
        is_smurf_anomaly=is_smurf_anomaly,
        anomaly_score=anomaly_score,
        predicted_label=predicted_label,
    )
