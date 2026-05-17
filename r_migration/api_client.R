# R client for the existing FastAPI service.
# This layer does not modify backend interfaces.

ensure_packages <- function() {
  needed <- c("httr2", "jsonlite")
  missing <- needed[!(needed %in% rownames(installed.packages()))]
  if (length(missing) > 0) {
    message("Installing missing packages: ", paste(missing, collapse = ", "))
    install.packages(missing, repos = "https://cloud.r-project.org")
  }
}

default_api_base_url <- function() {
  configured <- Sys.getenv("RIOT_API_BASE_URL", unset = "")
  if (nzchar(configured)) {
    return(configured)
  }

  # Project tests mostly use port 8001.
  "http://127.0.0.1:8001/api/v1"
}

build_api_url <- function(path, base_url = default_api_base_url()) {
  paste0(sub("/$", "", base_url), path)
}

post_json <- function(path, payload, base_url = default_api_base_url()) {
  ensure_packages()
  library(httr2)
  library(jsonlite)

  req <- request(build_api_url(path, base_url = base_url)) |>
    req_method("POST") |>
    req_headers("Content-Type" = "application/json") |>
    req_body_json(payload, auto_unbox = TRUE)

  resp <- req_perform(req)
  body <- resp_body_string(resp)

  if (resp_status(resp) >= 400) {
    stop(sprintf("HTTP %s on %s: %s", resp_status(resp), path, body), call. = FALSE)
  }

  fromJSON(body)
}

get_json <- function(path, base_url = default_api_base_url()) {
  ensure_packages()
  library(httr2)
  library(jsonlite)

  req <- request(build_api_url(path, base_url = base_url)) |>
    req_method("GET")

  resp <- req_perform(req)
  body <- resp_body_string(resp)

  if (resp_status(resp) >= 400) {
    stop(sprintf("HTTP %s on %s: %s", resp_status(resp), path, body), call. = FALSE)
  }

  fromJSON(body)
}

list_match_outcome_models <- function(base_url = default_api_base_url()) {
  get_json("/match-outcome/models", base_url = base_url)
}

predict_match_outcome_early <- function(features, base_url = default_api_base_url()) {
  post_json("/match-outcome/predict/early", features, base_url = base_url)
}

predict_match_outcome_full <- function(features, base_url = default_api_base_url()) {
  post_json("/match-outcome/predict/full", features, base_url = base_url)
}

predict_match_outcome_cascade <- function(features, base_url = default_api_base_url()) {
  post_json("/match-outcome/predict/cascade", features, base_url = base_url)
}

predict_match_outcome_strict <- function(features, base_url = default_api_base_url()) {
  post_json("/match-outcome/predict/strict", features, base_url = base_url)
}

predict_match_outcome_from_summary <- function(features, base_url = default_api_base_url()) {
  post_json("/match-outcome/predict/from-summary", features, base_url = base_url)
}

predict_rank <- function(features, base_url = default_api_base_url()) {
  post_json("/rank/predict", features, base_url = base_url)
}

predict_progression <- function(features, base_url = default_api_base_url()) {
  post_json("/progression/predict", features, base_url = base_url)
}

predict_smurf <- function(features, base_url = default_api_base_url()) {
  post_json("/smurf/predict", features, base_url = base_url)
}

predict_summoner <- function(request_payload, base_url = default_api_base_url()) {
  post_json("/summoner/predict", request_payload, base_url = base_url)
}

health_check <- function(base_url = default_api_base_url()) {
  get_json("/health", base_url = base_url)
}

riot_health_check <- function(base_url = default_api_base_url()) {
  get_json("/health/riot", base_url = base_url)
}
