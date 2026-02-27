# 📋 Project Structure Index

## 🎯 Quick Navigation

```
📁 Riot Games Project
├── 📁 scripts/                          # All Python scripts organized by function
│   ├── 1_data_processing/              # Raw data cleaning & preparation
│   ├── 2_feature_engineering/          # Feature creation & transformation
│   ├── 3_model_training/               # Model training & MLflow config
│   ├── 4_analysis_visualization/       # Analysis, reports, visualizations
│   └── 5_api_testing/                  # API tests & data scraping
│
├── 📁 models/                          # Trained models & shared utilities
│   ├── 1_rank_tier_classifier/        # Model 1
│   ├── 2_progression_regressor/       # Model 2
│   ├── 3_smurf_anomaly_detector/      # Model 3
│   ├── 4_match_outcome_predictor/     # Models 4, 5, 6 (including cascade)
│   └── shared/                         # Shared utilities (DataLoader, MLflowTracker)
│
├── 📁 data/                            # Datasets
│   ├── raw/                            # Original data files
│   └── processed/                      # Feature engineered datasets
│
├── 📁 frontend/                        # HTML dashboards
├── 📁 documentation/                   # All .md files (guides, reports)
├── 📁 mlruns/                          # MLflow experiment runs
├── 📁 opgg/                            # OP.GG leaderboard data
└── 📁 .venv/                           # Python virtual environment
```

---

## 📂 Scripts Breakdown

### **1_data_processing/** (Data Preparation)
Raw data cleaning, feature extraction, and dataset preparation.

| File | Purpose |
|------|---------|
| `data_prep.py` | Initial data loading & cleaning |
| `build_match_features_noleak.py` | Create match features with no data leakage |
| `build_match_features_early_simple.py` | Extract early-game features (10m snapshot) |
| `build_match_features_early_timeline.py` | Extract features from timeline data |
| `cleanup_csvs.py` | CSV validation & cleanup |
| `generate_match_features.py` | Generate post-game match features |
| `split_csv_by_rank.py` | Organize data by player rank tiers |
| `check_match_leakage_impact.py` | Validate no temporal leakage |
| `fix_grandmaster_tier.py` | Fix Grandmaster rank classification |
| `fix_smurf_highest_tiers.py` | Fix smurf tier assignments |

**Run Order:** 
1. `data_prep.py` → 2. `build_match_features_*.py` → 3. `cleanup_csvs.py`

---

### **2_feature_engineering/** (Feature Creation)
Transform raw features into ML-ready engineered features.

| File | Purpose |
|------|---------|
| `feature_engineering.py` | Main feature pipeline |
| `extract_advanced_features.py` | Complex feature derivations |
| `add_smurf_temporal_features.py` | Add time-based smurf indicators |
| `create_progression_enriched.py` | Create enriched progression features |

---

### **3_model_training/** (Model Training & Orchestration)
Train all 6 models and configure MLflow tracking.

| File | Purpose |
|------|---------|
| `train_all_models.py` ⭐ | **MAIN ENTRY** - Trains all 6 models sequentially |
| `mlflow_setup.py` | Initialize MLflow experiments |
| `mlflow_model_comparison.py` | Compare models in MLflow UI |
| `retrain_match_outcome_strict.py` | Retrain with strict anti-leakage rules |

**Quick Start:**
```bash
# Train all 6 models
python scripts/3_model_training/train_all_models.py

# View results (MLflow must be running)
mlflow ui --port 5000
# Then open: http://localhost:5000
```

---

### **4_analysis_visualization/** (Analysis & Reports)
Exploratory data analysis, model evaluation, and visualization.

| File | Purpose |
|------|---------|
| `analyze_performance.py` | Model performance analysis |
| `quick_analysis.py` | Quick exploratory queries |
| `analyze_early_features.py` | Early-game feature importance |
| `show_final_results.py` | Display final model results |
| `show_fix_summary.py` | Show data quality fixes |
| `show_latest_anomaly_results.py` | Latest smurf detection results |
| `visualize_comparison.py` | Model comparison visualizations |
| `model_comparison.py` | Detailed model metrics |
| `download_match_timelines.py` | Download raw match data |

---

### **5_api_testing/** (API & Validation)
API testing and external data validation.

| File | Purpose |
|------|---------|
| `riot_api_test.py` | Test Riot API connectivity |
| `craping.py` | Web scraping utilities |

---

## 📚 Documentation

All `.md` files moved to `documentation/` folder:

| File | Content |
|------|---------|
| `PROJECT_ANALYSIS.md` | Overall project design & architecture |
| `TRAINING_SETUP.md` | Model training guide |
| `TRAINING_RESULTS.md` | Final training metrics |
| `MLFLOW_VISUALIZATION_GUIDE.md` | MLflow UI tutorial |
| `FEATURE_ENGINEERING_SUMMARY.md` | Feature definitions |
| `README.md` | Main project readme |
| `DEMO_GUIDE.md` | Demo walkthrough |
| ...and more | 12+ guides total |

---

## 🚀 Common Workflows

### Train All Models
```bash
cd scripts/3_model_training/
python train_all_models.py
```

### Run Data Pipeline
```bash
cd scripts/1_data_processing/
python data_prep.py
python build_match_features_early_simple.py
python build_match_features_noleak.py
```

### Analyze Results
```bash
cd scripts/4_analysis_visualization/
python show_final_results.py
python analyze_performance.py
```

### View in MLflow
```bash
mlflow ui --port 5000
# Open http://localhost:5000
```

---

## 📊 Models Included

✓ **Model 1:** Rank Tier Classifier  
✓ **Model 2:** Progression Predictor  
✓ **Model 3:** Smurf Anomaly Detector  
✓ **Model 4:** Match Outcome (Post-Game)  
✓ **Model 5:** Match Outcome (Early-Game 15m)  
✓ **Model 6:** Match Outcome (Cascade 2-Stage)  

All trained models saved in `models/{model_number}/models/`

---

## 🔧 Setup & Requirements

- **Python:** 3.13+ (venv configured)
- **Key Packages:** sklearn, xgboost, lightgbm, mlflow, pandas, numpy
- **LLMs:** Integration ready (GPT-4, Claude available)

See `requirements.txt` for full dependency list.

---

## 📝 Last Updated
- **Date:** Feb 23, 2026
- **Status:** All 6 models trained ✓
- **MLflow:** Running on port 5000 ✓
