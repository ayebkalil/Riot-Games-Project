# Generate one consolidated parity report for migration tracking.

source("r_migration/validate_match_outcome_early_parity.R")
source("r_migration/validate_rank_progression_smurf_parity.R")

fmt_metric <- function(value, digits = 4) {
  if (is.null(value) || length(value) == 0 || is.na(value)) {
    return("N/A")
  }
  format(round(as.numeric(value), digits), nsmall = digits)
}

run_all <- function(limit = 30) {
  early_df <- run_validation(limit = limit)
  early_acc <- mean(early_df$truth == early_df$predicted_label)

  ext <- run_extended_validations(limit = limit)

  report_lines <- c(
    "# R Migration Parity Report",
    "",
    sprintf("Generated at: %s", as.character(Sys.time())),
    sprintf("Sample size per endpoint: %d", as.integer(limit)),
    "",
    "## Match Outcome (Early)",
    sprintf("- Accuracy: %s", fmt_metric(early_acc)),
    "- CSV: r_migration/parity_match_outcome_early_results.csv",
    "",
    "## Rank",
    sprintf("- Class accuracy: %s", fmt_metric(ext$rank$class_accuracy)),
    sprintf("- Rows: %d", as.integer(ext$rank$rows)),
    sprintf("- CSV: %s", ext$rank$output_csv),
    "",
    "## Progression",
    sprintf("- MAE: %s", fmt_metric(ext$progression$mae)),
    sprintf("- RMSE: %s", fmt_metric(ext$progression$rmse)),
    sprintf("- Rows: %d", as.integer(ext$progression$rows)),
    sprintf("- CSV: %s", ext$progression$output_csv),
    "",
    "## Smurf",
    sprintf("- Anomaly accuracy: %s", fmt_metric(ext$smurf$anomaly_accuracy)),
    sprintf("- Rows: %d", as.integer(ext$smurf$rows)),
    sprintf("- CSV: %s", ext$smurf$output_csv),
    "",
    "## Notes",
    "- This report validates the R bridge against existing Python API endpoints.",
    "- No backend/frontend interfaces were changed.",
    ""
  )

  report_path <- "r_migration/PARITY_REPORT.md"
  writeLines(report_lines, con = report_path)
  cat("Saved:", report_path, "\n")

  invisible(list(early = early_acc, extended = ext, report_path = report_path))
}

if (sys.nframe() == 0) {
  run_all(limit = 30)
}
