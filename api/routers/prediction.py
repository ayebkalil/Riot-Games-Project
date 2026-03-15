from fastapi import APIRouter

from api.schemas.prediction import (
    MatchOutcomeCascadeFeatures,
    MatchOutcomeFeatures,
    MatchOutcomeFullFeatures,
    MatchOutcomePrediction,
    MatchOutcomeStrictFeatures,
    MatchSummaryFeatures,
)
from api.services.predictor import (
    available_models,
    predict_match_outcome,
    predict_match_outcome_cascade,
    predict_match_outcome_full,
    predict_match_outcome_strict,
    predict_match_outcome_from_summary,
)


router = APIRouter(prefix="/match-outcome", tags=["match-outcome"])


@router.get("/models")
def list_models() -> dict:
    return {"models": available_models()}


@router.post("/predict/early", response_model=MatchOutcomePrediction)
def predict_early(features: MatchOutcomeFeatures) -> MatchOutcomePrediction:
    probability, label = predict_match_outcome(features)
    return MatchOutcomePrediction(win_probability=probability, predicted_label=label)


@router.post("/predict/full", response_model=MatchOutcomePrediction)
def predict_full(features: MatchOutcomeFullFeatures) -> MatchOutcomePrediction:
    probability, label = predict_match_outcome_full(features)
    return MatchOutcomePrediction(win_probability=probability, predicted_label=label)


@router.post("/predict/cascade", response_model=MatchOutcomePrediction)
def predict_cascade(features: MatchOutcomeCascadeFeatures) -> MatchOutcomePrediction:
    probability, label = predict_match_outcome_cascade(features)
    return MatchOutcomePrediction(win_probability=probability, predicted_label=label)


@router.post("/predict/strict", response_model=MatchOutcomePrediction)
def predict_strict(features: MatchOutcomeStrictFeatures) -> MatchOutcomePrediction:
    probability, label = predict_match_outcome_strict(features)
    return MatchOutcomePrediction(win_probability=probability, predicted_label=label)


@router.post("/predict/from-summary", response_model=MatchOutcomePrediction)
def predict_from_summary(features: MatchSummaryFeatures) -> MatchOutcomePrediction:
    """Run an approximate match outcome prediction using only basic Match History UI data."""
    probability, label = predict_match_outcome_from_summary(features)
    return MatchOutcomePrediction(win_probability=probability, predicted_label=label)
