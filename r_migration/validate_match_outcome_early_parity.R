# Validate API stability and output shape over a CSV sample.
# This checks the migration bridge without changing interfaces.

source("r_migration/api_client.R")

num_or_zero <- function(value) {
  out <- suppressWarnings(as.numeric(value))
  if (is.na(out)) {
    return(0.0)
  }
  out
}

read_sample <- function(csv_path, limit = 30) {
  df <- read.csv(csv_path, stringsAsFactors = FALSE)
  cols <- c(
    "lane_cs_10m",
    "jungle_cs_10m",
    "total_cs_10m",
    "takedowns_early",
    "aces_before_15m",
    "first_turret_kills",
    "first_turret_time_sec",
    "earliest_dragon_time_sec",
    "earliest_baron_time_sec",
    "early_laning_advantage",
    "control_wards_placed",
    "avg_kill_participation",
    "total_gold_earned",
    "total_xp",
    "avg_champion_level",
    "is_winner"
  )

  missing <- cols[!(cols %in% names(df))]
  if (length(missing) > 0) {
    stop(sprintf("CSV missing columns: %s", paste(missing, collapse = ", ")), call. = FALSE)
  }

  df <- df[seq_len(min(nrow(df), limit)), cols]
  df
}

to_payload <- function(row) {
  list(
    lane_cs_10m = num_or_zero(row[["lane_cs_10m"]]),
    jungle_cs_10m = num_or_zero(row[["jungle_cs_10m"]]),
    total_cs_10m = num_or_zero(row[["total_cs_10m"]]),
    takedowns_early = num_or_zero(row[["takedowns_early"]]),
    aces_before_15m = num_or_zero(row[["aces_before_15m"]]),
    first_turret_kills = num_or_zero(row[["first_turret_kills"]]),
    first_turret_time_sec = num_or_zero(row[["first_turret_time_sec"]]),
    earliest_dragon_time_sec = num_or_zero(row[["earliest_dragon_time_sec"]]),
    earliest_baron_time_sec = num_or_zero(row[["earliest_baron_time_sec"]]),
    early_laning_advantage = num_or_zero(row[["early_laning_advantage"]]),
    control_wards_placed = num_or_zero(row[["control_wards_placed"]]),
    avg_kill_participation = num_or_zero(row[["avg_kill_participation"]]),
    total_gold_earned = num_or_zero(row[["total_gold_earned"]]),
    total_xp = num_or_zero(row[["total_xp"]]),
    avg_champion_level = num_or_zero(row[["avg_champion_level"]])
  )
}

run_validation <- function(csv_path = "match_features_early_simple_sample.csv", limit = 30) {
  df <- read_sample(csv_path, limit = limit)

  probs <- numeric(nrow(df))
  preds <- integer(nrow(df))

  for (i in seq_len(nrow(df))) {
    payload <- to_payload(df[i, , drop = FALSE])
    out <- predict_match_outcome_early(payload)

    probs[i] <- as.numeric(out$win_probability)
    preds[i] <- as.integer(out$predicted_label)
  }

  truth <- as.integer(df$is_winner)
  acc <- mean(preds == truth)

  cat("Rows tested:", nrow(df), "\n")
  cat("Accuracy vs is_winner in sample:", round(acc, 4), "\n")
  cat("Mean probability:", round(mean(probs), 4), "\n")

  output <- data.frame(
    row_id = seq_len(nrow(df)),
    truth = truth,
    predicted_label = preds,
    win_probability = probs
  )

  out_path <- "r_migration/parity_match_outcome_early_results.csv"
  write.csv(output, out_path, row.names = FALSE)
  cat("Saved:", out_path, "\n")

  invisible(output)
}

if (sys.nframe() == 0) {
  run_validation()
}
