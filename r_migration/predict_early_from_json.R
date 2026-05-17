# Quick runner for early match outcome prediction through existing API.

source("r_migration/api_client.R")

# Example payload that matches the existing Python schema and endpoint.
payload <- list(
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
)

result <- predict_match_outcome_early(payload)
print(result)
