#!/usr/bin/env python3
"""
Quick fix to rebuild models with correct feature ordering.
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

print("Rebuilding models with correct feature alignment...")

# Load data
rank_df = pd.read_csv(PROJECT_ROOT / "rank_features_enriched_v2.csv")
smurf_df = pd.read_csv(PROJECT_ROOT / "smurf_features_with_predictions.csv")

# Get the actual features from CSV columns (these are the features that the extractor will produce)
actual_rank_features = [col for col in rank_df.columns if col not in ['puuid', 'tier', 'matches_used', 'main_role']]
print(f"Found {len(actual_rank_features)} actual rank features")

actual_smurf_features = [col for col in smurf_df.columns if col not in ['puuid', 'tier', 'is_anomaly', 'prediction', 'anomaly_score']]
print(f"Found {len(actual_smurf_features)} actual smurf features")

# Create rank model with actual features
X_rank = rank_df[actual_rank_features].fillna(0)
y_rank = rank_df["tier"].map({"Iron": 0, "Bronze": 0, "Silver": 0, "Gold": 1, "Platinum": 1, "Diamond": 2, "Master": 3, "Grandmaster": 3, "Challenger": 3}).fillna(0).astype(int)

rank_scaler = StandardScaler()
X_rank_scaled = rank_scaler.fit_transform(X_rank)
rank_model = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1, eval_metric='mlogloss')
rank_model.fit(X_rank_scaled, y_rank)

settings.rank_model_path.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(rank_model, settings.rank_model_path)
joblib.dump(rank_scaler, settings.rank_scaler_path)
print(f"✓ Saved rank model with {len(actual_rank_features)} features")

# Create smurf model with actual features
X_smurf = smurf_df[actual_smurf_features].fillna(0)
y_smurf = smurf_df["is_anomaly"].astype(int)

smurf_scaler = StandardScaler()
X_smurf_scaled = smurf_scaler.fit_transform(X_smurf)
smurf_model = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1, eval_metric='logloss')
smurf_model.fit(X_smurf_scaled, y_smurf)

settings.smurf_model_path.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(smurf_model, settings.smurf_model_path)
joblib.dump(smurf_scaler, settings.smurf_scaler_path)
print(f"✓ Saved smurf model with {len(actual_smurf_features)} features")

# Save feature info for debugging
print("\nSaving feature information...")
with open(PROJECT_ROOT / "model_features_info.txt", "w") as f:
    f.write("Rank Features:\n")
    for i, feat in enumerate(actual_rank_features):
        f.write(f"  {i}: {feat}\n")
    f.write(f"\nTotal: {len(actual_rank_features)} features\n\n")
    
    f.write("Smurf Features:\n")
    for i, feat in enumerate(actual_smurf_features):
        f.write(f"  {i}: {feat}\n")
    f.write(f"\nTotal: {len(actual_smurf_features)} features\n")

print("✅ Models rebuilt successfully!")
