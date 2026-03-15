from pydantic import BaseModel


class ProgressionFeatures(BaseModel):
    delta_kda: float
    delta_cs: float
    delta_gold: float
    delta_damage: float
    delta_vision: float
    delta_kill_participation: float
    delta_team_first_blood: float
    delta_team_first_tower: float
    delta_team_first_dragon: float
    delta_player_first_blood: float
    win_streak: float
    delta_goldPerMinute: float
    delta_damagePerMinute: float
    delta_visionScorePerMinute: float
    delta_skillshotAccuracy: float
    champion_pool_growth: float
    total_matches_analyzed: float


class ProgressionPrediction(BaseModel):
    predicted_delta_winrate: float
