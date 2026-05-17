from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier, XGBRegressor


ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"


def retrain_early_model() -> None:
    df = pd.read_csv(ROOT / "match_features_early_simple_sample.csv")

    feature_order = [
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

    X = df[feature_order].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    y = pd.to_numeric(df["is_winner"], errors="coerce").fillna(0).astype(int)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_scaled, y)

    out_dir = MODELS_DIR / "4_match_outcome_predictor" / "models"
    out_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, out_dir / "match_outcome_model_early_15m.pkl")
    joblib.dump(scaler, out_dir / "scaler.pkl")
    print("Saved early model/scaler with", len(feature_order), "features")


def retrain_full_model() -> None:
    df = pd.read_csv(ROOT / "match_features.csv")

    feature_order = [
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

    X = df[feature_order].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    y = pd.to_numeric(df["team_won"], errors="coerce").fillna(0).astype(int)

    model = XGBClassifier(
        n_estimators=280,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X, y)

    out_dir = MODELS_DIR / "4_match_outcome_predictor" / "models"
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_dir / "match_outcome_model_full.pkl")
    print("Saved full model with", len(feature_order), "features")


def retrain_progression_model() -> None:
    df = pd.read_csv(ROOT / "progression_features_enriched_v2.csv")

    feature_order = [
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

    X = df[feature_order].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    y = pd.to_numeric(df["delta_winrate"], errors="coerce").fillna(0.0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = XGBRegressor(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.07,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        random_state=42,
    )
    model.fit(X_scaled, y)

    out_dir = MODELS_DIR / "2_progression_regressor" / "models"
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_dir / "progression_model_v2_enriched.pkl")
    joblib.dump(scaler, out_dir / "scaler_v2_enriched.pkl")
    print("Saved progression model/scaler with", len(feature_order), "features")


def main() -> None:
    retrain_early_model()
    retrain_full_model()
    retrain_progression_model()
    print("Compatibility retraining complete")


if __name__ == "__main__":
    main()
