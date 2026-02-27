import requests
import json

# Valid player profile with realistic stats
valid_payload = {
    "avg_kda": 3.2,
    "avg_cs_per_min": 6.5,
    "avg_gold_per_min": 430,
    "avg_damage_per_min": 610,
    "avg_vision": 25,
    "avg_vision_per_min": 1.2,
    "avg_kill_participation": 0.58,
    "team_first_blood_rate": 0.52,
    "team_first_tower_rate": 0.49,
    "team_first_dragon_rate": 0.47,
    "player_first_blood_rate": 0.11,
    "win_rate": 0.54,
    "champ_pool_size": 18,
    "recent_form_30": 0.53,
    "recent_form_10": 0.56,
    "kda_consistency": 0.71,
    "champion_pool": 20,
    "role_focus_pct": 0.74,
    "gold_std": 95,
    "damage_std": 110,
    "goldPerMinute": 430,
    "damagePerMinute": 610,
    "visionScorePerMinute": 1.2,
    "skillshotAccuracy": 0.48,
    "killParticipation": 0.58,
    "controlWardsPlaced": 3,
    "wardTakedowns": 5,
    "soloKills": 1,
    "deathTimeRatio": 0.82,
    "earlyCS": 70,
    "turretPlates": 2,
    "killsNearTurret": 1,
    "epicMonsterSteals": 0,
    "objectivesStolen": 0,
    "bountyGold": 120,
    "champion_pool_size": 18,
    "role_consistency": 0.77,
    "total_games": 240,
    "matches_analyzed": 80,
    "wins_in_matches": 44
}

print("=" * 70)
print("Testing VALID Rank Payload (Real Player Stats)")
print("=" * 70)

response = requests.post("http://127.0.0.1:8001/api/v1/rank/predict", json=valid_payload)

print(f"\n✓ Status Code: {response.status_code}")
print(f"\nResponse:")
print(json.dumps(response.json(), indent=2))

if response.status_code == 200:
    result = response.json()
    print(f"\n✅ SUCCESS: API returned a tier prediction!")
    print(f"   Predicted Tier: {result.get('predicted_tier')}")
    print(f"   Class Index: {result.get('predicted_class_index')}")
else:
    print(f"\n❌ Error: Unexpected status code {response.status_code}")
