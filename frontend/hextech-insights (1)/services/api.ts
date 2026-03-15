export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8001/api/v1';

type JsonObject = Record<string, unknown>;

async function getJson<TResponse>(path: string): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  const body = await response.json();

  if (!response.ok) {
    const message = typeof body?.detail === 'string' ? body.detail : JSON.stringify(body);
    throw new Error(message || `Request failed (${response.status})`);
  }

  return body as TResponse;
}

async function postJson<TResponse>(path: string, payload: JsonObject): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const body = await response.json();

  if (!response.ok) {
    const message = typeof body?.detail === 'string' ? body.detail : JSON.stringify(body);
    throw new Error(message || `Request failed (${response.status})`);
  }

  return body as TResponse;
}

export interface MatchOutcomeResponse {
  win_probability: number;
  predicted_label: number;
}

export interface RankResponse {
  predicted_tier: string;
  predicted_class_index: number;
}

export interface ProgressionResponse {
  predicted_delta_winrate: number;
}

export interface SmurfResponse {
  is_smurf_anomaly: boolean;
  anomaly_score: number;
  predicted_label: number;
}

export interface MatchSummary {
  match_id: string;
  champion: string;
  role: string;
  kills: number;
  deaths: number;
  assists: number;
  win: boolean;
  game_duration: number;
  timestamp: number;
}

export interface SummonerProfile {
  summoner_name: string;
  summoner_level: number;
  puuid: string;
  region: string;
  ranked_tier: string | null;
  ranked_division: string | null;
  ranked_lp: number | null;
  ranked_wins: number | null;
  ranked_losses: number | null;
  predicted_rank_tier: string;
  predicted_rank_class: number;
  smurf_is_anomaly: boolean;
  smurf_anomaly_score: number;
  smurf_predicted_label: number;
  matches_analyzed: number;
  recent_matches: MatchSummary[];
  overall_winrate: number;
  avg_kda: number;
  avg_cs_per_min: number;
  avg_gold_per_min: number;
  champion_pool_size: number;
}

export interface SummonerPredictionResponse {
  success: boolean;
  profile: SummonerProfile | null;
  error: string | null;
  from_cache: boolean;
  cache_age_seconds: number | null;
  generated_at: number | null;
}

export interface HealthResponse {
  status: string;
  riot?: {
    key_configured: boolean;
    api_access: string;
  };
}

export interface RiotHealthResponse {
  status: string;
  riot: {
    key_configured: boolean;
    api_access: string;
  };
}

export interface MatchModelsResponse {
  models: string[];
}

export function getHealth() {
  return getJson<HealthResponse>('/health');
}

export function getRiotHealth() {
  return getJson<RiotHealthResponse>('/health');
}

export function listMatchOutcomeModels() {
  return getJson<MatchModelsResponse>('/match-outcome/models');
}

export function predictMatchOutcomeEarly(payload: JsonObject) {
  return postJson<MatchOutcomeResponse>('/match-outcome/predict/early', payload);
}

export function predictMatchOutcomeFromSummary(payload: MatchSummary) {
  return postJson<MatchOutcomeResponse>('/match-outcome/predict/from-summary', {
    kills: payload.kills,
    deaths: payload.deaths,
    assists: payload.assists,
    kda: payload.deaths > 0 ? (payload.kills + payload.assists) / payload.deaths : (payload.kills + payload.assists),
    win: payload.win,
    game_duration_sec: payload.game_duration,
    champion: payload.champion
  });
}

export function predictRank(payload: JsonObject) {
  return postJson<RankResponse>('/rank/predict', payload);
}

export function predictProgression(payload: JsonObject) {
  return postJson<ProgressionResponse>('/progression/predict', payload);
}

export function predictSmurf(payload: JsonObject) {
  return postJson<SmurfResponse>('/smurf/predict', payload);
}

export interface SummonerRequest {
  summoner_name: string;
  region?: string;
  match_count?: number;
}

export function getSummonerPredictions(request: SummonerRequest) {
  return postJson<SummonerPredictionResponse>('/summoner/predict', {
    summoner_name: request.summoner_name,
    region: request.region ?? 'na1',
    match_count: request.match_count ?? 20,
  });
}
