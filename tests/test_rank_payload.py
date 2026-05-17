import requests
import json

payload = {
    "avg_kda": 0,
    "avg_cs_per_min": 0,
    "avg_gold_per_min": 0,
    "avg_damage_per_min": 0,
    "avg_vision": 0,
    "avg_vision_per_min": 0,
    "avg_kill_participation": 0,
    "team_first_blood_rate": 0,
    "team_first_tower_rate": 0,
    "team_first_dragon_rate": 0,
    "player_first_blood_rate": 0,
    "win_rate": 0,
    "champ_pool_size": 0,
    "recent_form_30": 0,
    "recent_form_10": 0,
    "kda_consistency": 0,
    "champion_pool": 0,
    "role_focus_pct": 0,
    "gold_std": 0,
    "damage_std": 0,
    "goldPerMinute": 0,
    "damagePerMinute": 0,
    "visionScorePerMinute": 0,
    "skillshotAccuracy": 0,
    "killParticipation": 0,
    "controlWardsPlaced": 0,
    "wardTakedowns": 0,
    "soloKills": 0,
    "deathTimeRatio": 0,
    "earlyCS": 0,
    "turretPlates": 0,
    "killsNearTurret": 0,
    "epicMonsterSteals": 0,
    "objectivesStolen": 0,
    "bountyGold": 0,
    "champion_pool_size": 0,
    "role_consistency": 0,
    "total_games": 0,
    "matches_analyzed": 0,
    "wins_in_matches": 0
}

print("=" * 70)
print("Testing ALL-ZERO Rank Payload")
print("=" * 70)

response = requests.post("http://127.0.0.1:8001/api/v1/rank/predict", json=payload)

print(f"\n✓ Status Code: {response.status_code}")
print(f"\nResponse Body:")
print(json.dumps(response.json(), indent=2))

if response.status_code == 422:
    print("\n✅ SUCCESS: API correctly REJECTED all-zero payload with 422 status")
    print("   This means the OOD guard is working!")
else:
    print(f"\n❌ Unexpected status code: {response.status_code}")
