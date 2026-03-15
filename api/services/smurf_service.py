from __future__ import annotations

from functools import lru_cache

import joblib
import numpy as np

from api.core.settings import settings
from api.schemas.smurf import SmurfDetectionFeatures


SMURF_FEATURE_ORDER = [
    "winrate_zscore",
    "kda_zscore",
    "dmg_share",
    "gold_share",
    "avg_game_time",
    "champ_mastery_entropy",
    "avg_kill_participation",
    "avg_gold_per_min",
    "avg_damage_per_min",
    "avg_vision_per_min",
    "team_first_blood_rate",
    "team_first_tower_rate",
    "team_first_dragon_rate",
    "player_first_blood_rate",
    "current_win_streak",
    "current_loss_streak",
    "longest_win_streak_20",
    "longest_loss_streak_20",
    "recent_winrate_5",
    "recent_winrate_10",
    "winrate_trend_10",
    "recent_kda_5",
    "recent_kda_10",
    "kda_trend_10",
    "kda_volatility_10",
]


@lru_cache(maxsize=1)
def _load_smurf_bundle():
    model = joblib.load(settings.smurf_model_path)
    scaler = joblib.load(settings.smurf_scaler_path)
    return model, scaler


def predict_smurf_anomaly(features: SmurfDetectionFeatures) -> tuple[bool, float, int]:
    model, scaler = _load_smurf_bundle()
    raw_vector = np.array([[getattr(features, name) for name in SMURF_FEATURE_ORDER]], dtype=float)
    scaled = scaler.transform(raw_vector)

    predicted_label = int(model.predict(scaled)[0])
    anomaly_score = float(model.decision_function(scaled)[0])
    is_smurf_anomaly = predicted_label == -1

    return is_smurf_anomaly, anomaly_score, predicted_label
