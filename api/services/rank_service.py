from __future__ import annotations

from functools import lru_cache

import joblib
import numpy as np

from api.core.settings import settings
from api.schemas.rank import RankClassificationFeatures


RANK_FEATURE_ORDER = [
    "avg_kda",
    "avg_cs_per_min",
    "avg_gold_per_min",
    "avg_damage_per_min",
    "avg_vision",
    "avg_vision_per_min",
    "avg_kill_participation",
    "team_first_blood_rate",
    "team_first_tower_rate",
    "team_first_dragon_rate",
    "player_first_blood_rate",
    "win_rate",
    "champ_pool_size",
    "recent_form_30",
    "recent_form_10",
    "kda_consistency",
    "champion_pool",
    "role_focus_pct",
    "gold_std",
    "damage_std",
    "goldPerMinute",
    "damagePerMinute",
    "visionScorePerMinute",
    "skillshotAccuracy",
    "killParticipation",
    "controlWardsPlaced",
    "wardTakedowns",
    "soloKills",
    "deathTimeRatio",
    "earlyCS",
    "turretPlates",
    "killsNearTurret",
    "epicMonsterSteals",
    "objectivesStolen",
    "bountyGold",
    "champion_pool_size",
    "role_consistency",
    "total_games",
    "matches_analyzed",
    "wins_in_matches",
]

RANK_CLASS_NAMES = ["Low", "Mid", "High", "Elite"]


@lru_cache(maxsize=1)
def _load_rank_bundle():
    model = joblib.load(settings.rank_model_path)
    scaler = joblib.load(settings.rank_scaler_path)
    return model, scaler


def predict_rank_tier(features: RankClassificationFeatures) -> tuple[str, int]:
    model, scaler = _load_rank_bundle()
    raw_vector = np.array([[getattr(features, name) for name in RANK_FEATURE_ORDER]], dtype=float)
    scaled = scaler.transform(raw_vector)

    # mean_abs_z = float(np.mean(np.abs(scaled)))
    # if mean_abs_z > 3.0:
    #     logger.warning(f"Input is out-of-distribution for rank model (mean_abs_z: {mean_abs_z:.2f})")
    #     # raise ValueError("Input is out-of-distribution for rank model")

    class_index = int(model.predict(scaled)[0])
    class_name = RANK_CLASS_NAMES[class_index] if 0 <= class_index < len(RANK_CLASS_NAMES) else str(class_index)
    return class_name, class_index
