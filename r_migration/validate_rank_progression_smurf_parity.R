# Validate parity/stability for rank, progression, and smurf endpoints.
# This keeps existing backend/frontend interfaces unchanged.

source("r_migration/api_client.R")

num_or_zero <- function(value) {
  out <- suppressWarnings(as.numeric(value))
  if (is.na(out)) {
    return(0.0)
  }
  out
}

rank_feature_cols <- c(
  "avg_kda", "avg_cs_per_min", "avg_gold_per_min", "avg_damage_per_min",
  "avg_vision", "avg_vision_per_min", "avg_kill_participation", "team_first_blood_rate",
  "team_first_tower_rate", "team_first_dragon_rate", "player_first_blood_rate", "win_rate",
  "champ_pool_size", "recent_form_30", "recent_form_10", "kda_consistency", "champion_pool",
  "role_focus_pct", "gold_std", "damage_std", "goldPerMinute", "damagePerMinute",
  "visionScorePerMinute", "skillshotAccuracy", "killParticipation", "controlWardsPlaced",
  "wardTakedowns", "soloKills", "deathTimeRatio", "earlyCS", "turretPlates",
  "killsNearTurret", "epicMonsterSteals", "objectivesStolen", "bountyGold",
  "champion_pool_size", "role_consistency", "total_games", "matches_analyzed", "wins_in_matches"
)

progression_feature_cols <- c(
  "delta_kda", "delta_cs", "delta_gold", "delta_damage", "delta_vision",
  "delta_kill_participation", "delta_team_first_blood", "delta_team_first_tower",
  "delta_team_first_dragon", "delta_player_first_blood", "win_streak", "delta_goldPerMinute",
  "delta_damagePerMinute", "delta_visionScorePerMinute", "delta_skillshotAccuracy",
  "champion_pool_growth", "total_matches_analyzed"
)

smurf_feature_cols <- c(
  "winrate_zscore", "kda_zscore", "dmg_share", "gold_share", "avg_game_time",
  "champ_mastery_entropy", "avg_kill_participation", "avg_gold_per_min", "avg_damage_per_min",
  "avg_vision_per_min", "team_first_blood_rate", "team_first_tower_rate", "team_first_dragon_rate",
  "player_first_blood_rate", "current_win_streak", "current_loss_streak", "longest_win_streak_20",
  "longest_loss_streak_20", "recent_winrate_5", "recent_winrate_10", "winrate_trend_10",
  "recent_kda_5", "recent_kda_10", "kda_trend_10", "kda_volatility_10"
)

pick_rows <- function(df, cols, limit = 30) {
  missing <- cols[!(cols %in% names(df))]
  if (length(missing) > 0) {
    stop(sprintf("Missing columns: %s", paste(missing, collapse = ", ")), call. = FALSE)
  }

  subset <- df[, cols, drop = FALSE]
  subset <- subset[seq_len(min(nrow(subset), limit)), , drop = FALSE]
  subset
}

row_to_payload <- function(row, cols) {
  payload <- lapply(cols, function(col) num_or_zero(row[[col]]))
  names(payload) <- cols
  payload
}

sanitize_rank_payload <- function(payload) {
  gt_zero <- c("avg_kda", "avg_cs_per_min", "avg_gold_per_min", "avg_damage_per_min", "goldPerMinute", "damagePerMinute")
  ge_one <- c("champ_pool_size", "champion_pool", "champion_pool_size")
  unit_interval <- c(
    "avg_kill_participation", "team_first_blood_rate", "team_first_tower_rate", "team_first_dragon_rate",
    "player_first_blood_rate", "win_rate", "recent_form_30", "recent_form_10", "kda_consistency",
    "role_focus_pct", "skillshotAccuracy", "killParticipation", "deathTimeRatio", "role_consistency"
  )

  for (name in gt_zero) {
    if (!is.null(payload[[name]]) && payload[[name]] <= 0) {
      payload[[name]] <- 0.001
    }
  }

  for (name in ge_one) {
    if (!is.null(payload[[name]]) && payload[[name]] < 1) {
      payload[[name]] <- 1.0
    }
  }

  for (name in unit_interval) {
    if (!is.null(payload[[name]])) {
      payload[[name]] <- max(0.0, min(1.0, payload[[name]]))
    }
  }

  if (!is.null(payload[["total_games"]])) {
    payload[["total_games"]] <- max(5.0, payload[["total_games"]])
  }
  if (!is.null(payload[["matches_analyzed"]])) {
    payload[["matches_analyzed"]] <- max(5.0, payload[["matches_analyzed"]])
  }
  if (!is.null(payload[["wins_in_matches"]])) {
    payload[["wins_in_matches"]] <- max(0.0, payload[["wins_in_matches"]])
  }

  if (!is.null(payload[["matches_analyzed"]]) && !is.null(payload[["total_games"]])) {
    payload[["matches_analyzed"]] <- min(payload[["matches_analyzed"]], payload[["total_games"]])
  }
  if (!is.null(payload[["wins_in_matches"]]) && !is.null(payload[["matches_analyzed"]])) {
    payload[["wins_in_matches"]] <- min(payload[["wins_in_matches"]], payload[["matches_analyzed"]])
  }

  payload
}

tier_to_class <- function(tier_value) {
  tier <- tolower(as.character(tier_value))
  if (tier %in% c("iron", "bronze", "silver")) {
    return(list(class_index = 0L, class_name = "Low"))
  }
  if (tier %in% c("gold", "platinum")) {
    return(list(class_index = 1L, class_name = "Mid"))
  }
  if (tier %in% c("diamond")) {
    return(list(class_index = 2L, class_name = "High"))
  }
  if (tier %in% c("master", "grandmaster", "challenger")) {
    return(list(class_index = 3L, class_name = "Elite"))
  }
  list(class_index = NA_integer_, class_name = NA_character_)
}

run_rank_validation <- function(csv_path = "rank_features_enriched_v2.csv", limit = 30) {
  df <- read.csv(csv_path, stringsAsFactors = FALSE)
  x <- pick_rows(df, rank_feature_cols, limit = limit)

  pred_class <- integer(nrow(x))
  pred_tier <- character(nrow(x))

  for (i in seq_len(nrow(x))) {
    payload <- row_to_payload(x[i, , drop = FALSE], rank_feature_cols)
    payload <- sanitize_rank_payload(payload)
    out <- predict_rank(payload)
    pred_class[i] <- as.integer(out$predicted_class_index)
    pred_tier[i] <- as.character(out$predicted_tier)
  }

  truth_class <- rep(NA_integer_, nrow(x))
  truth_tier <- rep(NA_character_, nrow(x))
  if ("tier" %in% names(df)) {
    truth_tier <- as.character(df[seq_len(nrow(x)), "tier"])
    mapped <- lapply(truth_tier, tier_to_class)
    truth_class <- as.integer(vapply(mapped, function(m) m$class_index, integer(1)))
  }

  results <- data.frame(
    row_id = seq_len(nrow(x)),
    truth_tier = truth_tier,
    truth_class_index = truth_class,
    predicted_tier = pred_tier,
    predicted_class_index = pred_class,
    stringsAsFactors = FALSE
  )

  class_acc <- if (all(is.na(results$truth_class_index))) NA_real_ else mean(results$truth_class_index == results$predicted_class_index, na.rm = TRUE)

  out_path <- "r_migration/parity_rank_results.csv"
  write.csv(results, out_path, row.names = FALSE)

  list(
    endpoint = "rank",
    rows = nrow(results),
    class_accuracy = class_acc,
    output_csv = out_path
  )
}

run_progression_validation <- function(csv_path = "progression_features_enriched_v2.csv", limit = 30) {
  df <- read.csv(csv_path, stringsAsFactors = FALSE)
  x <- pick_rows(df, progression_feature_cols, limit = limit)

  pred <- numeric(nrow(x))
  for (i in seq_len(nrow(x))) {
    out <- predict_progression(row_to_payload(x[i, , drop = FALSE], progression_feature_cols))
    pred[i] <- as.numeric(out$predicted_delta_winrate)
  }

  truth <- rep(NA_real_, nrow(x))
  if ("delta_winrate" %in% names(df)) {
    truth <- as.numeric(df[seq_len(nrow(x)), "delta_winrate"])
  }

  results <- data.frame(
    row_id = seq_len(nrow(x)),
    truth_delta_winrate = truth,
    predicted_delta_winrate = pred,
    abs_error = abs(truth - pred)
  )

  mae <- if (all(is.na(results$truth_delta_winrate))) NA_real_ else mean(results$abs_error, na.rm = TRUE)
  rmse <- if (all(is.na(results$truth_delta_winrate))) NA_real_ else sqrt(mean((results$truth_delta_winrate - results$predicted_delta_winrate)^2, na.rm = TRUE))

  out_path <- "r_migration/parity_progression_results.csv"
  write.csv(results, out_path, row.names = FALSE)

  list(
    endpoint = "progression",
    rows = nrow(results),
    mae = mae,
    rmse = rmse,
    output_csv = out_path
  )
}

run_smurf_validation <- function(csv_path = "smurf_features_with_predictions.csv", limit = 30) {
  df <- read.csv(csv_path, stringsAsFactors = FALSE)
  x <- pick_rows(df, smurf_feature_cols, limit = limit)

  pred_label <- integer(nrow(x))
  pred_anomaly <- logical(nrow(x))
  pred_score <- numeric(nrow(x))

  for (i in seq_len(nrow(x))) {
    out <- predict_smurf(row_to_payload(x[i, , drop = FALSE], smurf_feature_cols))
    pred_label[i] <- as.integer(out$predicted_label)
    pred_anomaly[i] <- as.logical(out$is_smurf_anomaly)
    pred_score[i] <- as.numeric(out$anomaly_score)
  }

  truth_anomaly <- rep(NA_integer_, nrow(x))
  if ("is_anomaly" %in% names(df)) {
    raw_truth <- df[seq_len(nrow(x)), "is_anomaly"]
    truth_anomaly <- vapply(raw_truth, function(v) {
      sv <- tolower(as.character(v))
      if (sv %in% c("true", "1")) {
        return(1L)
      }
      if (sv %in% c("false", "0")) {
        return(0L)
      }
      return(NA_integer_)
    }, integer(1))
  }

  predicted_as_binary <- as.integer(pred_anomaly)

  results <- data.frame(
    row_id = seq_len(nrow(x)),
    truth_is_anomaly = truth_anomaly,
    predicted_is_anomaly = predicted_as_binary,
    predicted_label = pred_label,
    anomaly_score = pred_score
  )

  acc <- if (all(is.na(results$truth_is_anomaly))) NA_real_ else mean(results$truth_is_anomaly == results$predicted_is_anomaly, na.rm = TRUE)

  out_path <- "r_migration/parity_smurf_results.csv"
  write.csv(results, out_path, row.names = FALSE)

  list(
    endpoint = "smurf",
    rows = nrow(results),
    anomaly_accuracy = acc,
    output_csv = out_path
  )
}

run_extended_validations <- function(limit = 30) {
  rank_summary <- run_rank_validation(limit = limit)
  progression_summary <- run_progression_validation(limit = limit)
  smurf_summary <- run_smurf_validation(limit = limit)

  summary <- list(
    generated_at = as.character(Sys.time()),
    limit = as.integer(limit),
    rank = rank_summary,
    progression = progression_summary,
    smurf = smurf_summary
  )

  ensure_packages()
  library(jsonlite)

  json_path <- "r_migration/parity_extended_summary.json"
  writeLines(toJSON(summary, auto_unbox = TRUE, pretty = TRUE), con = json_path)

  summary
}

if (sys.nframe() == 0) {
  out <- run_extended_validations(limit = 30)
  print(out)
}
