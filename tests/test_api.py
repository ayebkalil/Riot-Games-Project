import httpx
import json
import time

print("Testing backend health...")
try:
    response = httpx.get("http://127.0.0.1:8001/api/v1/health/riot", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\nTesting summoner prediction...")
try:
    payload = {
        "summoner_name": "gone#VIDEX",
        "region": "euw1",
        "match_count": 20
    }
    print(f"Sending request: {payload}")
    start = time.time()
    response = httpx.post("http://127.0.0.1:8001/api/v1/summoner/predict", json=payload, timeout=60)
    elapsed = time.time() - start
    print(f"Status: {response.status_code} (took {elapsed:.1f}s)")
    result = response.json()
    
    if result.get("error"):
        print(f"\n❌ Error: {result['error']}")
        if "details" in result:
            print(f"Details: {result['details']}")
    elif result.get("success") and "profile" in result:
        profile = result["profile"]
        print(f"\n✅ SUCCESS! Full prediction pipeline working!")
        print(f"\n📊 Player Profile:")
        print(f"  • Summoner: {profile.get('summoner_name', 'N/A')} (Level {profile.get('summoner_level', 'N/A')})")
        print(f"  • Region: {profile.get('region', 'N/A')}")
        print(f"  • Ranked: {profile.get('ranked_tier', 'N/A')} {profile.get('ranked_division', 'N/A')} ({profile.get('ranked_wins', 0)}W-{profile.get('ranked_losses', 0)}L)")
        print(f"\n🤖 ML Predictions:")
        print(f"  • Rank Tier: {profile.get('predicted_rank_tier', 'N/A')} (class {profile.get('predicted_rank_class', 'N/A')})")
        print(f"  • Smurf Anomaly: {'YES ⚠️' if profile.get('smurf_is_anomaly') else 'NO ✓'} (score: {profile.get('smurf_anomaly_score', 'N/A'):.4f})")
        print(f"\n📈 Performance Metrics:")
        print(f"  • Win Rate: {profile.get('overall_winrate', 'N/A'):.1%}")
        print(f"  • Avg KDA: {profile.get('avg_kda', 'N/A'):.2f}")
        print(f"  • CS/min: {profile.get('avg_cs_per_min', 'N/A'):.2f}")
        print(f"  • Gold/min: {profile.get('avg_gold_per_min', 'N/A'):.1f}")
        print(f"  • Champion Pool: {profile.get('champion_pool_size', 'N/A')} champions")
        print(f"\n📊 Analysis: {profile.get('matches_analyzed', 'N/A')} recent matches")
    else:
        print(f"\n⚠️ Unexpected response format")
        print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
