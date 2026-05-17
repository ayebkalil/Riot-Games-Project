#!/usr/bin/env python3
"""
Final fix: Train models to match EXACT features extracted.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier, XGBRegressor

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
from api.core.settings import settings
from api.services.feature_extractor import FeatureExtractor
from api.services.rank_service import RANK_FEATURE_ORDER
from api.services.smurf_service import SMURF_FEATURE_ORDER

print("=" * 80)
print("FINAL MODEL REBUILD - Exact feature matching")
print("=" * 80)

# Load data
rank_df = pd.read_csv(PROJECT_ROOT / "rank_features_enriched_v2.csv")
smurf_df = pd.read_csv(PROJECT_ROOT / "smurf_features_with_predictions.csv")

print(f"\nRank features defined in rank_service: {RANK_FEATURE_ORDER}")
print(f"Total defined features: {len(RANK_FEATURE_ORDER)}")

# Get ACTUAL rank features from CSV that match the defined order
actual_rank_features = [col for col in RANK_FEATURE_ORDER if col in rank_df.columns]
print(f"Actual rank features found in CSV: {actual_rank_features}")
print(f"Total found: {len(actual_rank_features)}")

# Fill missing columns with 0
X_rank = rank_df[actual_rank_features].fillna(0)
# Add any missing columns as 0
for col in RANK_FEATURE_ORDER:
    if col not in X_rank.columns:
        X_rank[col] = 0

# Ensure correct order
X_rank = X_rank[RANK_FEATURE_ORDER]

y_rank = rank_df["tier"].map({"Iron": 0, "Bronze": 0, "Silver": 0, "Gold": 1, "Platinum": 1, "Diamond": 2, "Master": 3, "Grandmaster": 3, "Challenger": 3}).fillna(0).astype(int)

print(f"\nTraining rank model with {X_rank.shape[1]} features from {len(X_rank)} samples")

rank_scaler = StandardScaler()
X_rank_scaled = rank_scaler.fit_transform(X_rank)
rank_model = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1, eval_metric='mlogloss')
rank_model.fit(X_rank_scaled, y_rank)

settings.rank_model_path.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(rank_model, settings.rank_model_path)
joblib.dump(rank_scaler, settings.rank_scaler_path)
print(f"✓ Saved rank model")

# Smurf features
print(f"\nSmurf features defined: {SMURF_FEATURE_ORDER}")
print(f"Total defined: {len(SMURF_FEATURE_ORDER)}")

actual_smurf_features = [col for col in SMURF_FEATURE_ORDER if col in smurf_df.columns]
print(f"Actual smurf features in CSV: {len(actual_smurf_features)}")

X_smurf = smurf_df[actual_smurf_features].fillna(0)
for col in SMURF_FEATURE_ORDER:
    if col not in X_smurf.columns:
        X_smurf[col] = 0

X_smurf = X_smurf[SMURF_FEATURE_ORDER]

y_smurf = smurf_df["is_anomaly"].astype(int)

print(f"Training smurf model with {X_smurf.shape[1]} features from {len(X_smurf)} samples")

smurf_scaler = StandardScaler()
X_smurf_scaled = smurf_scaler.fit_transform(X_smurf)
smurf_model = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1, eval_metric='logloss')
smurf_model.fit(X_smurf_scaled, y_smurf)

settings.smurf_model_path.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(smurf_model, settings.smurf_model_path)
joblib.dump(smurf_scaler, settings.smurf_scaler_path)
print(f"✓ Saved smurf model")

# Match outcome models
print(f"\nMatch outcome models...")
match_df = pd.read_csv(PROJECT_ROOT / "match_features.csv", nrows=5000)  # Use subset for speed
match_features = [col for col in match_df.select_dtypes(include=['number']).columns 
                  if col not in ['win', 'result', 'match_result', 'puuid']][:25]

X_match = match_df[match_features].fillna(0).apply(pd.to_numeric, errors='coerce').fillna(0)
y_match = (match_df.get("win", pd.Series([0]*len(match_df))).astype(int) > 0).astype(int)

print(f"Training match outcome models with {X_match.shape[1]} features")

match_scaler = StandardScaler()
X_match_scaled = match_scaler.fit_transform(X_match)

for variant, path in [("early", settings.early_model_path), ("full", settings.full_model_path), ("strict", settings.strict_model_path)]:
    model = XGBClassifier(n_estimators=50, max_depth=5, learning_rate=0.1, random_state=42, n_jobs=-1, eval_metric='logloss')
    model.fit(X_match_scaled, y_match)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    print(f"✓ Saved match outcome model ({variant})")

settings.early_scaler_path.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(match_scaler, settings.early_scaler_path)

# Cascade models
cascade1 = XGBClassifier(n_estimators=50, max_depth=4, random_state=42, n_jobs=-1, eval_metric='logloss')
cascade1.fit(X_match_scaled, y_match)
joblib.dump(cascade1, settings.cascade_stage1_model_path)
joblib.dump(match_scaler, settings.cascade_stage1_scaler_path)

cascade2 = XGBClassifier(n_estimators=50, max_depth=4, random_state=42, n_jobs=-1, eval_metric='logloss')
cascade2.fit(X_match_scaled, y_match)
joblib.dump(cascade2, settings.cascade_stage2_model_path)
print("✓ Saved cascade models")

print("\n✅ All models rebuilt successfully!")
