# R Migration (Hybrid, No Interface Changes)

This folder starts a progressive migration to R while keeping current interfaces unchanged.

## What is included

- `api_client.R`: small R client for existing FastAPI endpoints.
- `predict_early_from_json.R`: quick prediction example against current API.
- `validate_match_outcome_early_parity.R`: parity/stability check over a CSV sample.
- `smoke_test_endpoints.R`: smoke tests for health, models, rank, progression, smurf, and summoner endpoints.
- `validate_rank_progression_smurf_parity.R`: parity metrics for rank/progression/smurf endpoints.
- `generate_parity_report.R`: consolidated Markdown report across validations.
- `bootstrap_r_env.R`: installs required R packages.
- `install_r_windows.ps1`: helper to install R via winget on Windows.

## Important

- No backend route is changed.
- No frontend contract is changed.
- Existing Python service remains the source of truth.

## Base URL config

By default, R scripts call:

- `http://127.0.0.1:8001/api/v1`

If your backend runs elsewhere, set:

- `RIOT_API_BASE_URL`

## Run order

1) Start backend as usual.
2) Run R scripts from project root.

## Commands

```powershell
# 1) Start Python backend (existing command)
./start_backend.bat

# 2) In another terminal, run R scripts
set RIOT_API_BASE_URL=http://127.0.0.1:8001/api/v1
Rscript r_migration/bootstrap_r_env.R
Rscript r_migration/predict_early_from_json.R
Rscript r_migration/validate_match_outcome_early_parity.R
Rscript r_migration/validate_rank_progression_smurf_parity.R
Rscript r_migration/generate_parity_report.R
Rscript r_migration/smoke_test_endpoints.R
```

If `Rscript` is not found in PATH on Windows, use explicit executable path:

```powershell
& "C:\Program Files\R\R-4.6.0\bin\Rscript.exe" r_migration/bootstrap_r_env.R
& "C:\Program Files\R\R-4.6.0\bin\Rscript.exe" r_migration/generate_parity_report.R
```

## Next migration steps

1. Re-train one model in R and compare metrics before any production swap.
2. Add CI job to run R parity scripts automatically.
3. Introduce an R-native API layer only after parity is validated.
