from pydantic import BaseModel


class MatchOutcomeFeatures(BaseModel):
    lane_cs_10m: float
    jungle_cs_10m: float
    total_cs_10m: float
    takedowns_early: float
    aces_before_15m: float
    first_turret_kills: float
    first_turret_time_sec: float
    earliest_dragon_time_sec: float
    earliest_baron_time_sec: float
    early_laning_advantage: float
    control_wards_placed: float
    avg_kill_participation: float
    total_gold_earned: float
    total_xp: float
    avg_champion_level: float


class MatchOutcomePrediction(BaseModel):
    win_probability: float
    predicted_label: int


class MatchOutcomeFullFeatures(BaseModel):
    gold_diff: float
    damage_diff: float
    kills_diff: float
    deaths_diff: float
    assists_diff: float
    vision_diff: float
    turrets_diff: float
    dragons_diff: float
    barons_diff: float
    cs_diff: float


class MatchOutcomeCascadeFeatures(BaseModel):
    lane_cs_10m: float
    jungle_cs_10m: float
    total_cs_10m: float
    takedowns_early: float
    aces_before_15m: float
    first_turret_kills: float
    first_turret_time_sec: float
    earliest_dragon_time_sec: float
    earliest_baron_time_sec: float
    early_laning_advantage: float
    control_wards_placed: float
    avg_kill_participation: float
    total_gold_earned: float
    total_xp: float
    avg_champion_level: float

    gold_diff: float
    damage_diff: float
    kills_diff: float
    deaths_diff: float
    assists_diff: float
    vision_diff: float
    turrets_diff: float
    dragons_diff: float
    barons_diff: float
    cs_diff: float


class MatchOutcomeStrictFeatures(BaseModel):
    rank_diff: float


class MatchSummaryFeatures(BaseModel):
    kills: int
    deaths: int
    assists: int
    kda: float
    win: bool
    game_duration_sec: int
    champion: str
