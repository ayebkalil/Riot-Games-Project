# Smoke tests for existing API endpoints through R bridge.
# No backend/frontend interface changes.

source("r_migration/api_client.R")

safe_run <- function(name, expr) {
  cat("\n", paste(rep("=", 72), collapse = ""), "\n", sep = "")
  cat("TEST:", name, "\n")
  cat(paste(rep("-", 72), collapse = ""), "\n", sep = "")

  out <- tryCatch(
    {
      value <- eval(expr)
      print(value)
      list(ok = TRUE, value = value)
    },
    error = function(e) {
      message("ERROR: ", e$message)
      list(ok = FALSE, error = e$message)
    }
  )

  invisible(out)
}

rank_payload <- list(
  avg_kda = 3.2,
  avg_cs_per_min = 6.5,
  avg_gold_per_min = 430,
  avg_damage_per_min = 610,
  avg_vision = 25,
  avg_vision_per_min = 1.2,
  avg_kill_participation = 0.58,
  team_first_blood_rate = 0.52,
  team_first_tower_rate = 0.49,
  team_first_dragon_rate = 0.47,
  player_first_blood_rate = 0.11,
  win_rate = 0.54,
  champ_pool_size = 18,
  recent_form_30 = 0.53,
  recent_form_10 = 0.56,
  kda_consistency = 0.71,
  champion_pool = 20,
  role_focus_pct = 0.74,
  gold_std = 95,
  damage_std = 110,
  goldPerMinute = 430,
  damagePerMinute = 610,
  visionScorePerMinute = 1.2,
  skillshotAccuracy = 0.48,
  killParticipation = 0.58,
  controlWardsPlaced = 3,
  wardTakedowns = 5,
  soloKills = 1,
  deathTimeRatio = 0.82,
  earlyCS = 70,
  turretPlates = 2,
  killsNearTurret = 1,
  epicMonsterSteals = 0,
  objectivesStolen = 0,
  bountyGold = 120,
  champion_pool_size = 18,
  role_consistency = 0.77,
  total_games = 240,
  matches_analyzed = 80,
  wins_in_matches = 44
)

progression_payload <- list(
  delta_kda = 0.2,
  delta_cs = 0.4,
  delta_gold = 15,
  delta_damage = 18,
  delta_vision = 1.1,
  delta_kill_participation = 0.02,
  delta_team_first_blood = 0.01,
  delta_team_first_tower = 0.02,
  delta_team_first_dragon = 0.01,
  delta_player_first_blood = 0.00,
  win_streak = 3,
  delta_goldPerMinute = 8,
  delta_damagePerMinute = 10,
  delta_visionScorePerMinute = 0.08,
  delta_skillshotAccuracy = 0.02,
  champion_pool_growth = 1,
  total_matches_analyzed = 40
)

smurf_payload <- list(
  winrate_zscore = -0.5,
  kda_zscore = -0.3,
  dmg_share = 0.28,
  gold_share = 0.25,
  avg_game_time = 31.5,
  champ_mastery_entropy = 2.1,
  avg_kill_participation = 0.55,
  avg_gold_per_min = 380,
  avg_damage_per_min = 520,
  avg_vision_per_min = 0.9,
  team_first_blood_rate = 0.48,
  team_first_tower_rate = 0.45,
  team_first_dragon_rate = 0.42,
  player_first_blood_rate = 0.12,
  current_win_streak = 2,
  current_loss_streak = 1,
  longest_win_streak_20 = 5,
  longest_loss_streak_20 = 4,
  recent_winrate_5 = 0.42,
  recent_winrate_10 = 0.48,
  winrate_trend_10 = 0.05,
  recent_kda_5 = 2.1,
  recent_kda_10 = 2.3,
  kda_trend_10 = -0.15,
  kda_volatility_10 = 0.8
)

summoner_payload <- list(
  summoner_name = "gone#VIDEX",
  region = "euw1",
  match_count = 20
)

results <- list(
  health = safe_run("GET /health", quote(health_check())),
  riot_health = safe_run("GET /health/riot", quote(riot_health_check())),
  models = safe_run("GET /match-outcome/models", quote(list_match_outcome_models())),
  early = safe_run("POST /match-outcome/predict/early", quote(predict_match_outcome_early(list(
    lane_cs_10m = 62,
    jungle_cs_10m = 11,
    total_cs_10m = 73,
    takedowns_early = 4,
    aces_before_15m = 0,
    first_turret_kills = 1,
    first_turret_time_sec = 860,
    earliest_dragon_time_sec = 420,
    earliest_baron_time_sec = 1300,
    early_laning_advantage = 950,
    control_wards_placed = 3,
    avg_kill_participation = 0.57,
    total_gold_earned = 6100,
    total_xp = 6450,
    avg_champion_level = 8.3
  )))),
  rank = safe_run("POST /rank/predict", quote(predict_rank(rank_payload))),
  progression = safe_run("POST /progression/predict", quote(predict_progression(progression_payload))),
  smurf = safe_run("POST /smurf/predict", quote(predict_smurf(smurf_payload))),
  summoner = safe_run("POST /summoner/predict", quote(predict_summoner(summoner_payload)))
)

ok_count <- sum(vapply(results, function(x) isTRUE(x$ok), logical(1)))
cat("\n", paste(rep("=", 72), collapse = ""), "\n", sep = "")
cat("SUCCESS:", ok_count, "/", length(results), "tests passed\n")
cat(paste(rep("=", 72), collapse = ""), "\n", sep = "")
