from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_available():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    body = response.json()
    assert "openapi" in body
    assert "/api/v1/match-outcome/models" in body["paths"]
    assert "/api/v1/match-outcome/predict/early" in body["paths"]
    assert "/api/v1/match-outcome/predict/full" in body["paths"]
    assert "/api/v1/match-outcome/predict/cascade" in body["paths"]
    assert "/api/v1/match-outcome/predict/strict" in body["paths"]
    assert "/api/v1/rank/predict" in body["paths"]
    assert "/api/v1/progression/predict" in body["paths"]
    assert "/api/v1/smurf/predict" in body["paths"]


def test_swagger_ui_available():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text


def test_models_endpoint():
    response = client.get("/api/v1/match-outcome/models")
    assert response.status_code == 200
    result = response.json()
    assert "models" in result
    assert "early-15m" in result["models"]
    assert "full-post-game" in result["models"]
    assert "strict-no-leakage" in result["models"]
    assert "cascade-early-plus-post" in result["models"]


def test_prediction_early_endpoint():
    payload = {
        "lane_cs_10m": 90,
        "jungle_cs_10m": 25,
        "total_cs_10m": 115,
        "takedowns_early": 8,
        "aces_before_15m": 0,
        "first_turret_kills": 1,
        "first_turret_time_sec": 780,
        "earliest_dragon_time_sec": 620,
        "earliest_baron_time_sec": 0,
        "early_laning_advantage": 1,
        "control_wards_placed": 6,
        "avg_kill_participation": 0.62,
        "total_gold_earned": 27000,
        "total_xp": 31000,
        "avg_champion_level": 10.5,
    }

    response = client.post("/api/v1/match-outcome/predict/early", json=payload)
    assert response.status_code == 200

    result = response.json()
    assert "win_probability" in result
    assert "predicted_label" in result
    assert 0.0 <= result["win_probability"] <= 1.0
    assert result["predicted_label"] in (0, 1)


def test_prediction_full_endpoint():
    payload = {
        "gold_diff": 1200,
        "damage_diff": 4500,
        "kills_diff": 6,
        "deaths_diff": -4,
        "assists_diff": 10,
        "vision_diff": 12,
        "turrets_diff": 2,
        "dragons_diff": 1,
        "barons_diff": 0,
        "cs_diff": 35,
    }

    response = client.post("/api/v1/match-outcome/predict/full", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert 0.0 <= result["win_probability"] <= 1.0
    assert result["predicted_label"] in (0, 1)


def test_prediction_cascade_endpoint():
    payload = {
        "lane_cs_10m": 90,
        "jungle_cs_10m": 25,
        "total_cs_10m": 115,
        "takedowns_early": 8,
        "aces_before_15m": 0,
        "first_turret_kills": 1,
        "first_turret_time_sec": 780,
        "earliest_dragon_time_sec": 620,
        "earliest_baron_time_sec": 0,
        "early_laning_advantage": 1,
        "control_wards_placed": 6,
        "avg_kill_participation": 0.62,
        "total_gold_earned": 27000,
        "total_xp": 31000,
        "avg_champion_level": 10.5,
        "gold_diff": 1200,
        "damage_diff": 4500,
        "kills_diff": 6,
        "deaths_diff": -4,
        "assists_diff": 10,
        "vision_diff": 12,
        "turrets_diff": 2,
        "dragons_diff": 1,
        "barons_diff": 0,
        "cs_diff": 35,
    }

    response = client.post("/api/v1/match-outcome/predict/cascade", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert 0.0 <= result["win_probability"] <= 1.0
    assert result["predicted_label"] in (0, 1)


def test_prediction_strict_endpoint():
    payload = {
        "rank_diff": 1
    }

    response = client.post("/api/v1/match-outcome/predict/strict", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert 0.0 <= result["win_probability"] <= 1.0
    assert result["predicted_label"] in (0, 1)


def test_rank_prediction_endpoint():
    payload = {
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

    response = client.post("/api/v1/rank/predict", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert "predicted_tier" in result
    assert "predicted_class_index" in result


def test_rank_prediction_rejects_all_zero_payload():
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

    response = client.post("/api/v1/rank/predict", json=payload)
    assert response.status_code == 422


def test_progression_prediction_endpoint():
    payload = {
        "delta_kda": 0.25,
        "delta_cs": 0.4,
        "delta_gold": 120,
        "delta_damage": 180,
        "delta_vision": 0.1,
        "delta_kill_participation": 0.03,
        "delta_team_first_blood": 0.02,
        "delta_team_first_tower": 0.01,
        "delta_team_first_dragon": 0.01,
        "delta_player_first_blood": 0.0,
        "win_streak": 2,
        "delta_goldPerMinute": 10,
        "delta_damagePerMinute": 25,
        "delta_visionScorePerMinute": 0.05,
        "delta_skillshotAccuracy": 0.02,
        "champion_pool_growth": 1,
        "total_matches_analyzed": 80
    }

    response = client.post("/api/v1/progression/predict", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert "predicted_delta_winrate" in result


def test_smurf_prediction_endpoint():
    payload = {
        "winrate_zscore": 1.5,
        "kda_zscore": 1.7,
        "dmg_share": 0.28,
        "gold_share": 0.27,
        "avg_game_time": 1620,
        "champ_mastery_entropy": 0.45,
        "avg_kill_participation": 0.62,
        "avg_gold_per_min": 430,
        "avg_damage_per_min": 650,
        "avg_vision_per_min": 1.1,
        "team_first_blood_rate": 0.58,
        "team_first_tower_rate": 0.53,
        "team_first_dragon_rate": 0.5,
        "player_first_blood_rate": 0.16,
        "current_win_streak": 3,
        "current_loss_streak": 0,
        "longest_win_streak_20": 6,
        "longest_loss_streak_20": 2,
        "recent_winrate_5": 0.8,
        "recent_winrate_10": 0.7,
        "winrate_trend_10": 0.08,
        "recent_kda_5": 4.2,
        "recent_kda_10": 3.9,
        "kda_trend_10": 0.3,
        "kda_volatility_10": 0.4
    }

    response = client.post("/api/v1/smurf/predict", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert "is_smurf_anomaly" in result
    assert "anomaly_score" in result
    assert "predicted_label" in result
