from __future__ import annotations

from functools import lru_cache

import joblib
import numpy as np

from api.core.settings import settings
from api.schemas.prediction import (
    MatchOutcomeCascadeFeatures,
    MatchOutcomeFeatures,
    MatchOutcomeFullFeatures,
    MatchOutcomeStrictFeatures,
    MatchSummaryFeatures,
)


FEATURE_ORDER = [
    "lane_cs_10m",
    "jungle_cs_10m",
    "total_cs_10m",
    "takedowns_early",
    "aces_before_15m",
    "first_turret_kills",
    "first_turret_time_sec",
    "earliest_dragon_time_sec",
    "earliest_baron_time_sec",
    "early_laning_advantage",
    "control_wards_placed",
    "avg_kill_participation",
    "total_gold_earned",
    "total_xp",
    "avg_champion_level",
]

FULL_FEATURE_ORDER = [
    "gold_diff",
    "damage_diff",
    "kills_diff",
    "deaths_diff",
    "assists_diff",
    "vision_diff",
    "turrets_diff",
    "dragons_diff",
    "barons_diff",
    "cs_diff",
]


@lru_cache(maxsize=1)
def _load_early_model_bundle():
    model = joblib.load(settings.early_model_path)
    scaler = joblib.load(settings.early_scaler_path)
    return model, scaler


@lru_cache(maxsize=1)
def _load_full_model():
    return joblib.load(settings.full_model_path)


@lru_cache(maxsize=1)
def _load_strict_model_bundle():
    model = joblib.load(settings.strict_model_path)
    scaler = joblib.load(settings.strict_scaler_path)
    return model, scaler


@lru_cache(maxsize=1)
def _load_cascade_bundle():
    stage1_model = joblib.load(settings.cascade_stage1_model_path)
    stage1_scaler = joblib.load(settings.cascade_stage1_scaler_path)
    stage2_model = joblib.load(settings.cascade_stage2_model_path)
    return stage1_model, stage1_scaler, stage2_model


def predict_match_outcome(features: MatchOutcomeFeatures) -> tuple[float, int]:
    model, scaler = _load_early_model_bundle()

    raw_vector = np.array([[getattr(features, name) for name in FEATURE_ORDER]], dtype=float)
    scaled = scaler.transform(raw_vector)

    probability = float(model.predict_proba(scaled)[0, 1])
    predicted_label = int(probability >= 0.5)
    return probability, predicted_label


def predict_match_outcome_full(features: MatchOutcomeFullFeatures) -> tuple[float, int]:
    model = _load_full_model()
    raw_vector = np.array([[getattr(features, name) for name in FULL_FEATURE_ORDER]], dtype=float)
    probability = float(model.predict_proba(raw_vector)[0, 1])
    predicted_label = int(probability >= 0.5)
    return probability, predicted_label


def predict_match_outcome_cascade(features: MatchOutcomeCascadeFeatures) -> tuple[float, int]:
    stage1_model, stage1_scaler, stage2_model = _load_cascade_bundle()

    early_raw = np.array([[getattr(features, name) for name in FEATURE_ORDER]], dtype=float)
    early_scaled = stage1_scaler.transform(early_raw)
    p_early = float(stage1_model.predict_proba(early_scaled)[0, 1])

    post_raw = np.array([[getattr(features, name) for name in FULL_FEATURE_ORDER]], dtype=float)
    stage2_input = np.concatenate([post_raw, np.array([[p_early]], dtype=float)], axis=1)

    probability = float(stage2_model.predict_proba(stage2_input)[0, 1])
    predicted_label = int(probability >= 0.5)
    return probability, predicted_label


def predict_match_outcome_strict(features: MatchOutcomeStrictFeatures) -> tuple[float, int]:
    model, scaler = _load_strict_model_bundle()
    raw_vector = np.array([[features.rank_diff]], dtype=float)
    scaled = scaler.transform(raw_vector)
    probability = float(model.predict_proba(scaled)[0, 1])
    predicted_label = int(probability >= 0.5)
    return probability, predicted_label


def predict_match_outcome_from_summary(features: MatchSummaryFeatures) -> tuple[float, int]:
    """Predict or retroactively explain an outcome based on basic Match History summary stats."""
    model, scaler = _load_early_model_bundle()
    
    # We don't have all 15 early features from just the match history card.
    # So we'll synthesize an "Early Laning Advantage" and "Total Gold Earned" proxy based on KDA.
    # If the match was already a win, we heavily bias the proxy features toward a win so the model aligns with reality.
    
    advantage_multiplier = 1.0 if features.win else -1.0
    
    # Synthesize proxy features that map to the early 15m feature expectation
    takedowns_early = (features.kills + features.assists) * 0.4  # Assume 40% of takedowns were early
    early_laning_advantage = (features.kda - 2.0) * 1000 * advantage_multiplier
    total_gold_earned = 5000 + (features.kills * 300) + (features.assists * 100)
    
    # Fill the exact FEATURE_ORDER array with dummy/proxy values
    synth_features = {
        "lane_cs_10m": 60,
        "jungle_cs_10m": 10,
        "total_cs_10m": 70,
        "takedowns_early": takedowns_early,
        "aces_before_15m": 1 if features.kda > 5 else 0,
        "first_turret_kills": 1 if takedowns_early > 2 else 0,
        "first_turret_time_sec": 800,
        "earliest_dragon_time_sec": 400,
        "earliest_baron_time_sec": 1200,
        "early_laning_advantage": early_laning_advantage,
        "control_wards_placed": 2,
        "avg_kill_participation": 0.5,
        "total_gold_earned": total_gold_earned,
        "total_xp": 6000,
        "avg_champion_level": 8,
    }
    
    raw_vector = np.array([[synth_features[name] for name in FEATURE_ORDER]], dtype=float)
    scaled = scaler.transform(raw_vector)

    probability = float(model.predict_proba(scaled)[0, 1])
    predicted_label = int(probability >= 0.5)
    
    # Force alignment: If we know they won, floor prob at 0.51. If lost, cap at 0.49.
    if features.win and probability < 0.5:
        probability = 0.51 + (probability * 0.4)
    elif not features.win and probability >= 0.5:
        probability = probability * 0.99
        if probability >= 0.5:
            probability = 0.49
            
    predicted_label = int(probability >= 0.5)
    
    return probability, predicted_label


def available_models() -> list[str]:
    return ["early-15m", "full-post-game", "strict-no-leakage", "cascade-early-plus-post"]
