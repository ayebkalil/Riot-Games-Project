"""Riot Games API Client for fetching summoner and match data."""
import httpx
from typing import Dict, List, Optional, Any
from urllib.parse import quote
from pathlib import Path

from api.core.settings import settings


def _load_riot_key_from_project_env() -> Optional[str]:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return None

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("RIOT_API_KEY="):
            return stripped.split("=", 1)[1].strip().strip('"').strip("'")

    return None


class RiotAPIClient:
    """Client for interacting with Riot Games API."""
    
    BASE_URLS = {
        'na1': 'https://na1.api.riotgames.com',
        'euw1': 'https://euw1.api.riotgames.com',
        'eun1': 'https://eun1.api.riotgames.com',
        'kr': 'https://kr.api.riotgames.com',
        'br1': 'https://br1.api.riotgames.com',
        'jp1': 'https://jp1.api.riotgames.com',
        'ru': 'https://ru.api.riotgames.com',
        'oc1': 'https://oc1.api.riotgames.com',
        'tr1': 'https://tr1.api.riotgames.com',
        'la1': 'https://la1.api.riotgames.com',
        'la2': 'https://la2.api.riotgames.com',
    }
    
    REGIONAL_URLS = {
        'americas': 'https://americas.api.riotgames.com',
        'europe': 'https://europe.api.riotgames.com',
        'asia': 'https://asia.api.riotgames.com',
        'sea': 'https://sea.api.riotgames.com',
    }
    
    REGION_TO_REGIONAL = {
        'na1': 'americas',
        'br1': 'americas',
        'la1': 'americas',
        'la2': 'americas',
        'euw1': 'europe',
        'eun1': 'europe',
        'tr1': 'europe',
        'ru': 'europe',
        'kr': 'asia',
        'jp1': 'asia',
        'oc1': 'sea',
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Riot API client.
        
        Args:
            api_key: Riot API key. If None, will try to read from RIOT_API_KEY env var.
        """
        self.api_key = api_key or _load_riot_key_from_project_env() or settings.riot_api_key
        if self.api_key:
            self.api_key = self.api_key.strip().strip('"').strip("'")
        if not self.api_key:
            raise ValueError("Riot API key not provided. Set RIOT_API_KEY environment variable.")
        
        self.headers = {
            'X-Riot-Token': self.api_key
        }
    
    async def get_summoner_by_name(self, region: str, summoner_name: str) -> Dict[str, Any]:
        """Fetch summoner data by summoner name.
        
        Args:
            region: Platform routing value (e.g., 'na1', 'euw1')
            summoner_name: Summoner name
            
        Returns:
            Summoner data dict with id, accountId, puuid, name, summonerLevel, etc.
        """
        if region not in self.BASE_URLS:
            raise ValueError(f"Invalid region: {region}")

        normalized_name = summoner_name.strip()

        if "#" in normalized_name:
            game_name, tag_line = normalized_name.split("#", 1)
            account = await self.get_account_by_riot_id(region, game_name.strip(), tag_line.strip())
            return await self.get_summoner_by_puuid(region, account["puuid"])
        
        base_url = self.BASE_URLS[region]
        encoded_name = quote(normalized_name, safe="")
        url = f"{base_url}/lol/summoner/v4/summoners/by-name/{encoded_name}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_account_by_riot_id(self, region: str, game_name: str, tag_line: str) -> Dict[str, Any]:
        """Fetch account data by Riot ID (gameName + tagLine).

        Args:
            region: Platform routing value (e.g., 'na1', 'euw1')
            game_name: Riot game name (before '#')
            tag_line: Riot tag line (after '#')

        Returns:
            Account data dict containing puuid
        """
        regional_route = self.REGION_TO_REGIONAL.get(region, 'americas')
        base_url = self.REGIONAL_URLS[regional_route]

        encoded_game_name = quote(game_name.strip(), safe="")
        encoded_tag_line = quote(tag_line.strip(), safe="")
        url = f"{base_url}/riot/account/v1/accounts/by-riot-id/{encoded_game_name}/{encoded_tag_line}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def get_summoner_by_puuid(self, region: str, puuid: str) -> Dict[str, Any]:
        """Fetch summoner data by PUUID.
        
        Args:
            region: Platform routing value (e.g., 'na1', 'euw1')
            puuid: Player Universal Unique Identifier
            
        Returns:
            Summoner data dict
        """
        if region not in self.BASE_URLS:
            raise ValueError(f"Invalid region: {region}")
        
        base_url = self.BASE_URLS[region]
        url = f"{base_url}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def get_match_history(
        self, 
        region: str, 
        puuid: str, 
        count: int = 20,
        queue: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[str]:
        """Fetch match IDs for a summoner.
        
        Args:
            region: Platform routing value (e.g., 'na1', 'euw1')
            puuid: Player Universal Unique Identifier
            count: Number of matches to fetch (max 100)
            queue: Queue ID filter (420 = Ranked Solo, 440 = Ranked Flex)
            start_time: Epoch timestamp filter (matches after this time)
            end_time: Epoch timestamp filter (matches before this time)
            
        Returns:
            List of match IDs
        """
        regional_route = self.REGION_TO_REGIONAL.get(region, 'americas')
        base_url = self.REGIONAL_URLS[regional_route]
        
        # Build query params
        params = {'count': min(count, 100)}
        if queue:
            params['queue'] = queue
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        
        url = f"{base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_match_details(self, region: str, match_id: str) -> Dict[str, Any]:
        """Fetch detailed match data.
        
        Args:
            region: Platform routing value (e.g., 'na1', 'euw1')
            match_id: Match ID
            
        Returns:
            Match data dict with metadata, info, participants, etc.
        """
        regional_route = self.REGION_TO_REGIONAL.get(region, 'americas')
        base_url = self.REGIONAL_URLS[regional_route]
        
        url = f"{base_url}/lol/match/v5/matches/{match_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def get_summoner_ranked_stats(self, region: str, puuid: str) -> List[Dict[str, Any]]:
        """Fetch ranked stats for a summoner by PUUID.
        
        Args:
            region: Platform routing value (e.g., 'na1', 'euw1')
            puuid: Player Universal Unique Identifier
            
        Returns:
            List of league entries (one per queue type)
        """
        if region not in self.BASE_URLS:
            raise ValueError(f"Invalid region: {region}")
        
        base_url = self.BASE_URLS[region]
        url = f"{base_url}/lol/league/v4/entries/by-puuid/{puuid}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
