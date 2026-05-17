import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.services.feature_extractor import FeatureExtractor
import httpx

print("Fetching summoner data from Riot API...")
try:
    # Get summoner PUUID first
    response = httpx.get(
        f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/gone/VIDEX",
        headers={"X-Riot-Token": "RGAPI-c847c945-5fc6-4a1b-8f47-9b42eaa45886"}
    )
    if response.status_code == 200:
        puuid = response.json()["puuid"]
        print(f"Found PUUID: {puuid}")
        
        # Get match history
        matches_response = httpx.get(
            f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids",
            params={"start": 0, "count": 20},
            headers={"X-Riot-Token": "RGAPI-c847c945-5fc6-4a1b-8f47-9b42eaa45886"}
        )
        
        if matches_response.status_code == 200:
            match_ids = matches_response.json()
            print(f"Found {len(match_ids)} matches")
            
            # Get match details for first match
            match_response = httpx.get(
                f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_ids[0]}",
                headers={"X-Riot-Token": "RGAPI-c847c945-5fc6-4a1b-8f47-9b42eaa45886"}
            )
            
            if match_response.status_code == 200:
                match_data = match_response.json()
                
                # Extract features
                features = FeatureExtractor.calculate_rank_features([match_data], puuid)
                
                print(f"\nExtracted {len(features)} features:")
                for i, (key, val) in enumerate(features.items()):
                    print(f"  {i}: {key} = {val}")
        else:
            print(f"Error fetching matches: {matches_response.status_code}")
    else:
        print(f"Error fetching summoner: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
