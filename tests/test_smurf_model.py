import requests
import json

print("\n" + "=" * 80)
print("SMURF DETECTION MODEL - TEST CASES")
print("=" * 80)

# Test 1: All-zero payload (anomalous - likely to be flagged)
zero_payload = {
    "winrate_zscore": 0,
    "kda_zscore": 0,
    "dmg_share": 0,
    "gold_share": 0,
    "avg_game_time": 0,
    "champ_mastery_entropy": 0,
    "avg_kill_participation": 0,
    "avg_gold_per_min": 0,
    "avg_damage_per_min": 0,
    "avg_vision_per_min": 0,
    "team_first_blood_rate": 0,
    "team_first_tower_rate": 0,
    "team_first_dragon_rate": 0,
    "player_first_blood_rate": 0,
    "current_win_streak": 0,
    "current_loss_streak": 0,
    "longest_win_streak_20": 0,
    "longest_loss_streak_20": 0,
    "recent_winrate_5": 0,
    "recent_winrate_10": 0,
    "winrate_trend_10": 0,
    "recent_kda_5": 0,
    "recent_kda_10": 0,
    "kda_trend_10": 0,
    "kda_volatility_10": 0
}

# Test 2: Realistic normal player profile (not a smurf)
normal_payload = {
    "winrate_zscore": -0.5,
    "kda_zscore": -0.3,
    "dmg_share": 0.28,
    "gold_share": 0.25,
    "avg_game_time": 31.5,
    "champ_mastery_entropy": 2.1,
    "avg_kill_participation": 0.55,
    "avg_gold_per_min": 380,
    "avg_damage_per_min": 520,
    "avg_vision_per_min": 0.9,
    "team_first_blood_rate": 0.48,
    "team_first_tower_rate": 0.45,
    "team_first_dragon_rate": 0.42,
    "player_first_blood_rate": 0.12,
    "current_win_streak": 2,
    "current_loss_streak": 1,
    "longest_win_streak_20": 5,
    "longest_loss_streak_20": 4,
    "recent_winrate_5": 0.42,
    "recent_winrate_10": 0.48,
    "winrate_trend_10": 0.05,
    "recent_kda_5": 2.1,
    "recent_kda_10": 2.3,
    "kda_trend_10": -0.15,
    "kda_volatility_10": 0.8
}

# Test 3: Suspicious smurf-like profile (high anomaly score)
smurf_payload = {
    "winrate_zscore": 3.2,
    "kda_zscore": 2.8,
    "dmg_share": 0.42,
    "gold_share": 0.38,
    "avg_game_time": 28.2,
    "champ_mastery_entropy": 0.5,
    "avg_kill_participation": 0.78,
    "avg_gold_per_min": 520,
    "avg_damage_per_min": 680,
    "avg_vision_per_min": 1.8,
    "team_first_blood_rate": 0.72,
    "team_first_tower_rate": 0.68,
    "team_first_dragon_rate": 0.65,
    "player_first_blood_rate": 0.35,
    "current_win_streak": 15,
    "current_loss_streak": 0,
    "longest_win_streak_20": 17,
    "longest_loss_streak_20": 2,
    "recent_winrate_5": 0.95,
    "recent_winrate_10": 0.88,
    "winrate_trend_10": 0.25,
    "recent_kda_5": 5.2,
    "recent_kda_10": 4.8,
    "kda_trend_10": 0.35,
    "kda_volatility_10": 0.4
}

test_cases = [
    ("All-Zero Payload", zero_payload),
    ("Normal Player Profile", normal_payload),
    ("Suspicious Smurf Profile", smurf_payload)
]

for test_name, payload in test_cases:
    print(f"\n{'-' * 80}")
    print(f"TEST: {test_name}")
    print(f"{'-' * 80}")
    
    try:
        response = requests.post("http://127.0.0.1:8001/api/v1/smurf/predict", json=payload)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"\nResponse:")
        print(json.dumps(result, indent=2))
        
        if response.status_code == 200:
            print(f"\n✓ is_smurf_anomaly: {result.get('is_smurf_anomaly')}")
            print(f"✓ anomaly_score: {result.get('anomaly_score'):.4f}")
            print(f"✓ predicted_label: {result.get('predicted_label')}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("COPY AND PASTE INTO SWAGGER:")
print("=" * 80)
print("\nNormal Player (use this to test):")
print(json.dumps(normal_payload, indent=2))
print("\nSuspicious Smurf (use this to see high anomaly score):")
print(json.dumps(smurf_payload, indent=2))
