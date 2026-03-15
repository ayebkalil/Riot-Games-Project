from pydantic import BaseModel


class SmurfDetectionFeatures(BaseModel):
    winrate_zscore: float
    kda_zscore: float
    dmg_share: float
    gold_share: float
    avg_game_time: float
    champ_mastery_entropy: float
    avg_kill_participation: float
    avg_gold_per_min: float
    avg_damage_per_min: float
    avg_vision_per_min: float
    team_first_blood_rate: float
    team_first_tower_rate: float
    team_first_dragon_rate: float
    player_first_blood_rate: float
    current_win_streak: float
    current_loss_streak: float
    longest_win_streak_20: float
    longest_loss_streak_20: float
    recent_winrate_5: float
    recent_winrate_10: float
    winrate_trend_10: float
    recent_kda_5: float
    recent_kda_10: float
    kda_trend_10: float
    kda_volatility_10: float


class SmurfDetectionPrediction(BaseModel):
    is_smurf_anomaly: bool
    anomaly_score: float
    predicted_label: int
