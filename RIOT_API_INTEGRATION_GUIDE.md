# Riot API Integration Setup Guide

## Overview
The application now fetches real-time summoner data directly from the Riot Games API. When you search for a summoner, the system:

1. **Fetches summoner profile** from Riot API
2. **Retrieves last 20 ranked matches** automatically
3. **Extracts ML features** from match data (KDA, CS/min, gold/min, etc.)
4. **Runs predictions** through all 4 ML models:
   - Rank Classification
   - Smurf Detection
   - Progression Analysis
   - Match Outcome Prediction
5. **Displays results** with no manual input required

## Setup Instructions

### Step 1: Get Your Riot API Key

1. Go to [Riot Developer Portal](https://developer.riotgames.com/)
2. Sign in with your Riot Games account
3. Navigate to the "Dashboard" or "Apps" section
4. Generate a **Development API Key** (refreshes every 24 hours) or register for a **Production API Key**
5. Copy your API key

### Step 2: Configure the API Key

Open the `.env` file in the project root directory:

```bash
c:\Users\ayebk\OneDrive\Desktop\Riot Games Project\.env
```

Replace `YOUR_API_KEY_HERE` with your actual API key:

```env
RIOT_API_KEY=RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Important Notes:**
- Development keys expire every 24 hours - you'll need to refresh daily
- Production keys require an approved application and have higher rate limits
- Never commit your API key to version control (`.env` is already in `.gitignore`)

### Step 3: Restart the Backend Server

If the backend is running, restart it to load the new API key:

```powershell
# Stop the current backend (Ctrl+C in the terminal where it's running)

# Start it again
.\.venv\Scripts\activate
uvicorn api.main:app --reload --port 8001
```

### Step 4: Test the Integration

1. Open the frontend at http://localhost:5173
2. Navigate to the **Profile** page
3. Enter a summoner name (e.g., "Doublelift", "Faker", etc.)
4. Select the appropriate region (NA1, KR, EUW1, etc.)
5. Click **Search**

The system will:
- Fetch the summoner's recent ranked matches
- Extract all features automatically
- Display real predictions from the ML models
- Show actual match history with KDA, champions, win/loss

## API Endpoints

### New Endpoint: `/api/v1/summoner/predict`

**Request:**
```json
{
  "summoner_name": "Doublelift",
  "region": "na1",
  "match_count": 20
}
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "summoner_name": "Doublelift",
    "summoner_level": 342,
    "puuid": "...",
    "region": "na1",
    "ranked_tier": "DIAMOND",
    "ranked_division": "I",
    "ranked_lp": 45,
    "ranked_wins": 120,
    "ranked_losses": 64,
    "predicted_rank_tier": "Diamond",
    "predicted_rank_class": 6,
    "smurf_is_anomaly": false,
    "smurf_anomaly_score": 0.023,
    "smurf_predicted_label": 0,
    "matches_analyzed": 20,
    "recent_matches": [...],
    "overall_winrate": 0.652,
    "avg_kda": 3.45,
    "avg_cs_per_min": 8.2,
    "avg_gold_per_min": 425.5,
    "champion_pool_size": 12
  }
}
```

## Supported Regions

- **NA1** - North America
- **EUW1** - Europe West
- **EUN1** - Europe Nordic & East
- **KR** - Korea
- **BR1** - Brazil
- **JP1** - Japan
- **LA1** - Latin America North
- **LA2** - Latin America South
- **OC1** - Oceania
- **TR1** - Turkey
- **RU** - Russia

## Features Automatically Extracted

The system extracts **40+ features** from match history:

### Rank Classification Features:
- Average KDA, CS/min, Gold/min, Damage/min
- Vision score per minute
- Kill participation rate
- First blood/tower/dragon rates
- Champion pool diversity
- Role consistency
- Recent form (last 10/30 games)
- And 20+ more...

### Smurf Detection Features:
- Performance z-scores (KDA, winrate)
- Damage and gold share
- Champion mastery entropy
- Win/loss streaks
- Trend analysis (last 5-10 games)
- Performance volatility
- And 15+ more...

All features are calculated automatically - **no manual input required!**

## Troubleshooting

### Error: "Riot API key not provided"
- Check that `.env` file exists in project root
- Verify `RIOT_API_KEY` is set correctly
- Restart the backend server after changing `.env`

### Error: "No ranked matches found"
- The summoner may not have played ranked games recently
- Try a summoner with more ranked game history
- Ensure you selected the correct region

### Error: "Request failed (403)"
- Your API key may be expired (development keys expire daily)
- Generate a new key from the Riot Developer Portal
- Update `.env` and restart the backend

### Error: "Request failed (429)"
- Rate limit exceeded
- Development keys have strict rate limits (20 requests/second, 100 requests/2 minutes)
- Wait a few minutes and try again
- Consider applying for a production key

## Testing with Swagger/OpenAPI

You can also test the endpoint directly at:

http://localhost:8001/docs

1. Navigate to **POST /api/v1/summoner/predict**
2. Click "Try it out"
3. Enter summoner name and region
4. Click "Execute"
5. View the full JSON response

## Architecture

```
User Input (Summoner Name + Region)
         ↓
Frontend (Profile.tsx)
         ↓
API Service (api.ts) → POST /summoner/predict
         ↓
Backend Router (summoner.py)
         ↓
Riot API Client (riot_client.py) → Riot Games API
         ↓
Feature Extractor (feature_extractor.py) → Calculate 40+ features
         ↓
ML Services (rank_service.py, smurf_service.py) → Run predictions
         ↓
Response → Frontend → Display results
```

## What Changed

### Backend:
- ✅ `api/services/riot_client.py` - Riot API integration
- ✅ `api/services/feature_extractor.py` - Automatic feature extraction
- ✅ `api/routers/summoner.py` - New summoner prediction endpoint
- ✅ `api/schemas/summoner.py` - Request/response schemas
- ✅ `api/core/settings.py` - API key configuration
- ✅ `.env` - Environment variables

### Frontend:
- ✅ `services/api.ts` - New `getSummonerPredictions()` function
- ✅ `pages/Profile.tsx` - Summoner search UI + real data display
- ✅ Automatic match history from API
- ✅ Live predictions without manual JSON editing

## Next Steps

You can now:
1. Search for any summoner by name and region
2. View their automatically generated ML predictions
3. See their real match history
4. Compare predicted rank vs actual rank
5. Detect smurf behavior automatically

The manual payload editing workflow is no longer needed - everything is automated!
