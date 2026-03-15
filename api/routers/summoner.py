"""Router for summoner-based predictions using live Riot API data."""
from fastapi import APIRouter, HTTPException, Depends
import logging
import httpx
import asyncio
import time
from typing import Any, Dict

from api.schemas.summoner import SummonerRequest, SummonerPredictionResponse, SummonerProfile, MatchSummary
from api.schemas.rank import RankClassificationFeatures
from api.schemas.smurf import SmurfDetectionFeatures
from api.services.riot_client import RiotAPIClient
from api.services.feature_extractor import FeatureExtractor
from api.services.rank_service import predict_rank_tier
from api.services.smurf_service import predict_smurf_anomaly


router = APIRouter(prefix="/summoner", tags=["summoner"])
logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 600
_SUMMONER_CACHE: Dict[str, Dict[str, Any]] = {}


def get_riot_client() -> RiotAPIClient:
    """Dependency to get Riot API client."""
    try:
        return RiotAPIClient()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


def _cache_key(request: SummonerRequest) -> str:
    return f"{request.region.lower()}::{request.summoner_name.strip().lower()}::{request.match_count}"


def _get_cached_response(request: SummonerRequest) -> SummonerPredictionResponse | None:
    key = _cache_key(request)
    entry = _SUMMONER_CACHE.get(key)
    if not entry:
        return None

    age_seconds = int(time.time() - entry["cached_at"])
    if age_seconds > CACHE_TTL_SECONDS:
        _SUMMONER_CACHE.pop(key, None)
        return None

    return SummonerPredictionResponse(
        success=True,
        profile=entry["profile"],
        from_cache=True,
        cache_age_seconds=age_seconds,
        generated_at=int(time.time()),
        error="Live fetch unavailable; showing recent cached data.",
    )


def _set_cached_response(request: SummonerRequest, profile: SummonerProfile) -> None:
    _SUMMONER_CACHE[_cache_key(request)] = {
        "profile": profile,
        "cached_at": time.time(),
    }


async def _call_with_retry(coro_factory, retries: int = 2, base_delay: float = 1.0):
    last_error = None
    for attempt in range(retries + 1):
        try:
            return await coro_factory()
        except httpx.HTTPStatusError as exc:
            last_error = exc
            status = exc.response.status_code
            retryable = status in (429, 500, 502, 503, 504)
            if attempt >= retries or not retryable:
                raise
            await asyncio.sleep(base_delay * (2 ** attempt))

    if last_error:
        raise last_error


@router.post("/predict", response_model=SummonerPredictionResponse)
async def predict_summoner(
    request: SummonerRequest,
    riot_client: RiotAPIClient = Depends(get_riot_client),
):
    """Get comprehensive ML predictions for a summoner using live Riot API data.
    
    This endpoint:
    1. Fetches summoner data from Riot API
    2. Retrieves recent match history
    3. Extracts ML features from matches
    4. Runs rank classification and smurf detection models
    5. Returns complete profile with predictions
    """
    try:
        # Fetch summoner data
        logger.info(f"Fetching summoner: {request.summoner_name} in {request.region}")
        normalized_name = request.summoner_name.strip()

        if "#" in normalized_name:
            game_name, tag_line = normalized_name.split("#", 1)
        else:
            raise HTTPException(status_code=400, detail="Riot ID must include a hashtag (e.g., Name#Tag)")

        account = await _call_with_retry(
            lambda: riot_client.get_account_by_riot_id(request.region, game_name, tag_line)
        )
        puuid = account["puuid"]
        full_riot_id = f"{account.get('gameName', game_name)}#{account.get('tagLine', tag_line)}"

        summoner = await _call_with_retry(
            lambda: riot_client.get_summoner_by_puuid(request.region, puuid)
        )
        
        # Fetch ranked stats using PUUID
        ranked_stats = await _call_with_retry(
            lambda: riot_client.get_summoner_ranked_stats(request.region, puuid)
        )
        solo_queue = next((r for r in ranked_stats if r['queueType'] == 'RANKED_SOLO_5x5'), None)
        
        # Fetch match history
        logger.info(f"Fetching {request.match_count} matches for {puuid}")
        match_ids = await _call_with_retry(
            lambda: riot_client.get_match_history(
                request.region,
                puuid,
                count=request.match_count,
                queue=420,
            )
        )
        
        if not match_ids:
            raise HTTPException(status_code=404, detail="No ranked matches found for this summoner")
        
        # Fetch detailed match data
        logger.info(f"Fetching details for {len(match_ids)} matches")
        matches = []
        for match_id in match_ids:
            try:
                match_data = await riot_client.get_match_details(request.region, match_id)
                matches.append(match_data)
            except Exception as e:
                logger.warning(f"Failed to fetch match {match_id}: {e}")
                continue
        
        if not matches:
            raise HTTPException(status_code=500, detail="Failed to fetch any match details")
        
        # Extract features for ML models
        logger.info("Extracting features from matches")
        rank_features_dict = FeatureExtractor.calculate_rank_features(matches, puuid)
        smurf_features_dict = FeatureExtractor.calculate_smurf_features(matches, puuid)
        
        # Convert to Pydantic models
        rank_features = RankClassificationFeatures(**rank_features_dict)
        smurf_features = SmurfDetectionFeatures(**smurf_features_dict)
        
        # Run predictions
        logger.info("Running ML predictions")
        predicted_rank_tier, predicted_rank_class = predict_rank_tier(rank_features)
        smurf_is_anomaly, smurf_anomaly_score, smurf_predicted_label = predict_smurf_anomaly(smurf_features)
        
        # Build recent matches summary
        recent_matches = []
        recent_match_limit = max(1, min(request.match_count, 20))
        for match in matches[:recent_match_limit]:
            participant = FeatureExtractor.extract_participant_stats(match, puuid)
            if participant:
                recent_matches.append(MatchSummary(
                    match_id=match['metadata']['matchId'],
                    champion=participant.get('championName', 'Unknown'),
                    role=participant.get('teamPosition', 'UTILITY'),
                    kills=participant.get('kills', 0),
                    deaths=participant.get('deaths', 0),
                    assists=participant.get('assists', 0),
                    win=participant.get('win', False),
                    game_duration=match['info'].get('gameDuration', 0),
                    timestamp=match['info'].get('gameCreation', 0)
                ))
        
        # Build profile
        profile = SummonerProfile(
            summoner_name=full_riot_id,
            summoner_level=summoner['summonerLevel'],
            puuid=puuid,
            region=request.region,
            ranked_tier=solo_queue['tier'] if solo_queue else None,
            ranked_division=solo_queue['rank'] if solo_queue else None,
            ranked_lp=solo_queue['leaguePoints'] if solo_queue else None,
            ranked_wins=solo_queue['wins'] if solo_queue else None,
            ranked_losses=solo_queue['losses'] if solo_queue else None,
            predicted_rank_tier=predicted_rank_tier,
            predicted_rank_class=predicted_rank_class,
            smurf_is_anomaly=smurf_is_anomaly,
            smurf_anomaly_score=smurf_anomaly_score,
            smurf_predicted_label=smurf_predicted_label,
            matches_analyzed=len(matches),
            recent_matches=recent_matches,
            overall_winrate=rank_features_dict['win_rate'],
            avg_kda=rank_features_dict['avg_kda'],
            avg_cs_per_min=rank_features_dict['avg_cs_per_min'],
            avg_gold_per_min=rank_features_dict['avg_gold_per_min'],
            champion_pool_size=int(rank_features_dict['champion_pool_size'])
        )

        _set_cached_response(request, profile)
        
        return SummonerPredictionResponse(
            success=True,
            profile=profile,
            from_cache=False,
            cache_age_seconds=0,
            generated_at=int(time.time()),
        )
        
    except HTTPException:
        raise
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code

        cached = _get_cached_response(request)
        if cached:
            return cached

        if status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Riot API returned 401 Unauthorized. Your API key is invalid, expired, or not active yet.",
            ) from exc
        if status_code == 403:
            raise HTTPException(
                status_code=403,
                detail="Riot API returned 403 Forbidden. Your API key is not currently authorized for this request (expired/revoked/restricted).",
            ) from exc
        if status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Riot API rate limit reached. Try again in 30 seconds.",
            ) from exc
        if status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Summoner/Riot ID not found for the selected region.",
            ) from exc

        raise HTTPException(
            status_code=status_code,
            detail=f"Riot API error ({status_code}) while fetching summoner data.",
        ) from exc
    except Exception as e:
        logger.error(f"Error processing summoner prediction: {e}", exc_info=True)

        cached = _get_cached_response(request)
        if cached:
            return cached

        return SummonerPredictionResponse(
            success=False,
            error=f"Failed to process summoner data: {str(e)}",
            from_cache=False,
            generated_at=int(time.time()),
        )
