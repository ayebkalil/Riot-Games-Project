from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Riot Games Project API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    debug: bool = False
    
    # Riot Games API Key
    riot_api_key: str = Field(default="", description="Riot Games API Key")

    early_model_path: Path = Field(
        default=ROOT_DIR / "models" / "4_match_outcome_predictor" / "models" / "match_outcome_model_early_15m.pkl"
    )
    early_scaler_path: Path = Field(
        default=ROOT_DIR / "models" / "4_match_outcome_predictor" / "models" / "scaler.pkl"
    )

    full_model_path: Path = Field(
        default=ROOT_DIR / "models" / "4_match_outcome_predictor" / "models" / "match_outcome_model_full.pkl"
    )

    strict_model_path: Path = Field(
        default=ROOT_DIR / "models" / "4_match_outcome_predictor" / "models" / "match_outcome_model_strict.pkl"
    )
    strict_scaler_path: Path = Field(
        default=ROOT_DIR / "models" / "4_match_outcome_predictor" / "models" / "scaler_strict.pkl"
    )

    cascade_stage1_model_path: Path = Field(
        default=ROOT_DIR / "models" / "4_match_outcome_predictor" / "models" / "cascade_stage1_early_model.pkl"
    )
    cascade_stage1_scaler_path: Path = Field(
        default=ROOT_DIR / "models" / "4_match_outcome_predictor" / "models" / "cascade_stage1_scaler.pkl"
    )
    cascade_stage2_model_path: Path = Field(
        default=ROOT_DIR / "models" / "4_match_outcome_predictor" / "models" / "cascade_stage2_cascaded_model.pkl"
    )

    rank_model_path: Path = Field(
        default=ROOT_DIR / "models" / "1_rank_tier_classifier" / "models" / "rank_tier_model_v2_enriched.pkl"
    )
    rank_scaler_path: Path = Field(
        default=ROOT_DIR / "models" / "1_rank_tier_classifier" / "models" / "scaler_v2_enriched.pkl"
    )

    progression_model_path: Path = Field(
        default=ROOT_DIR / "models" / "2_progression_regressor" / "models" / "progression_model_v2_enriched.pkl"
    )
    progression_scaler_path: Path = Field(
        default=ROOT_DIR / "models" / "2_progression_regressor" / "models" / "scaler_v2_enriched.pkl"
    )

    smurf_model_path: Path = Field(
        default=ROOT_DIR / "models" / "3_smurf_anomaly_detector" / "models" / "smurf_anomaly_model.pkl"
    )
    smurf_scaler_path: Path = Field(
        default=ROOT_DIR / "models" / "3_smurf_anomaly_detector" / "models" / "scaler.pkl"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
