from pydantic import BaseModel, Field, model_validator


class RankClassificationFeatures(BaseModel):
    avg_kda: float = Field(gt=0)
    avg_cs_per_min: float = Field(gt=0)
    avg_gold_per_min: float = Field(gt=0)
    avg_damage_per_min: float = Field(gt=0)
    avg_vision: float = Field(ge=0)
    avg_vision_per_min: float = Field(ge=0)
    avg_kill_participation: float = Field(ge=0, le=1)
    team_first_blood_rate: float = Field(ge=0, le=1)
    team_first_tower_rate: float = Field(ge=0, le=1)
    team_first_dragon_rate: float = Field(ge=0, le=1)
    player_first_blood_rate: float = Field(ge=0, le=1)
    win_rate: float = Field(ge=0, le=1)
    champ_pool_size: float = Field(ge=1)
    recent_form_30: float = Field(ge=0, le=1)
    recent_form_10: float = Field(ge=0, le=1)
    kda_consistency: float = Field(ge=0, le=1)
    champion_pool: float = Field(ge=1)
    role_focus_pct: float = Field(ge=0, le=1)
    gold_std: float = Field(ge=0)
    damage_std: float = Field(ge=0)
    goldPerMinute: float = Field(gt=0)
    damagePerMinute: float = Field(gt=0)
    visionScorePerMinute: float = Field(ge=0)
    skillshotAccuracy: float = Field(ge=0, le=1)
    killParticipation: float = Field(ge=0, le=1)
    controlWardsPlaced: float = Field(ge=0)
    wardTakedowns: float = Field(ge=0)
    soloKills: float = Field(ge=0)
    deathTimeRatio: float = Field(ge=0, le=1)
    earlyCS: float = Field(ge=0)
    turretPlates: float = Field(ge=0)
    killsNearTurret: float = Field(ge=0)
    epicMonsterSteals: float = Field(ge=0)
    objectivesStolen: float = Field(ge=0)
    bountyGold: float = Field(ge=0)
    champion_pool_size: float = Field(ge=1)
    role_consistency: float = Field(ge=0, le=1)
    total_games: float = Field(ge=5)
    matches_analyzed: float = Field(ge=5)
    wins_in_matches: float = Field(ge=0)

    @model_validator(mode="after")
    def validate_cross_fields(self):
        if self.matches_analyzed > self.total_games:
            raise ValueError("matches_analyzed cannot be greater than total_games")
        if self.wins_in_matches > self.matches_analyzed:
            raise ValueError("wins_in_matches cannot be greater than matches_analyzed")
        return self


class RankClassificationPrediction(BaseModel):
    predicted_tier: str
    predicted_class_index: int
