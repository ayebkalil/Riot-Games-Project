from __future__ import annotations

from functools import lru_cache

import joblib
import numpy as np

from api.core.settings import settings
from api.schemas.progression import ProgressionFeatures


PROGRESSION_FEATURE_ORDER = [
    "delta_kda",
    "delta_cs",
    "delta_gold",
    "delta_damage",
    "delta_vision",
    "delta_kill_participation",
    "delta_team_first_blood",
    "delta_team_first_tower",
    "delta_team_first_dragon",
    "delta_player_first_blood",
    "win_streak",
    "delta_goldPerMinute",
    "delta_damagePerMinute",
    "delta_visionScorePerMinute",
    "delta_skillshotAccuracy",
    "champion_pool_growth",
    "total_matches_analyzed",
]


@lru_cache(maxsize=1)
def _load_progression_bundle():
    model = joblib.load(settings.progression_model_path)
    scaler = joblib.load(settings.progression_scaler_path)
    return model, scaler


def predict_progression(features: ProgressionFeatures) -> float:
    model, scaler = _load_progression_bundle()
    raw_vector = np.array([[getattr(features, name) for name in PROGRESSION_FEATURE_ORDER]], dtype=float)
    scaled = scaler.transform(raw_vector)
    prediction = float(model.predict(scaled)[0])
    return prediction
