"""Schemas for summoner-based predictions."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class SummonerRequest(BaseModel):
    """Request for summoner-based prediction."""
    summoner_name: str = Field(..., description="Summoner name")
    region: str = Field(default="na1", description="Platform region (na1, euw1, kr, etc.)")
    match_count: int = Field(default=20, ge=5, le=100, description="Number of recent matches to analyze")


class MatchSummary(BaseModel):
    """Summary of a single match."""
    match_id: str
    champion: str
    role: str
    kills: int
    deaths: int
    assists: int
    win: bool
    game_duration: int
    timestamp: int


class SummonerProfile(BaseModel):
    """Summoner profile with ML predictions."""
    summoner_name: str
    summoner_level: int
    puuid: str
    region: str
    
    # Ranked stats
    ranked_tier: Optional[str] = None
    ranked_division: Optional[str] = None
    ranked_lp: Optional[int] = None
    ranked_wins: Optional[int] = None
    ranked_losses: Optional[int] = None
    
    # ML Predictions
    predicted_rank_tier: str
    predicted_rank_class: int
    
    smurf_is_anomaly: bool
    smurf_anomaly_score: float
    smurf_predicted_label: int
    
    # Match history
    matches_analyzed: int
    recent_matches: List[MatchSummary]
    
    # Statistics
    overall_winrate: float
    avg_kda: float
    avg_cs_per_min: float
    avg_gold_per_min: float
    champion_pool_size: int


class SummonerPredictionResponse(BaseModel):
    """Complete prediction response for a summoner."""
    success: bool
    profile: Optional[SummonerProfile] = None
    error: Optional[str] = None
    from_cache: bool = False
    cache_age_seconds: Optional[int] = None
    generated_at: Optional[int] = None
