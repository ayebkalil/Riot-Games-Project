from fastapi import APIRouter
import httpx

from api.core.settings import settings


router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    riot = await riot_health_check()
    if riot.get("status") == "ok":
        return {"status": "ok", "riot": riot.get("riot")}

    return {"status": "degraded", "riot": riot.get("riot")}


@router.get("/health/riot")
async def riot_health_check() -> dict:
    key = (settings.riot_api_key or "").strip().strip('"').strip("'")
    if not key:
        return {
            "status": "error",
            "riot": {
                "key_configured": False,
                "api_access": "not_configured",
            },
        }

    headers = {"X-Riot-Token": key}
    url = "https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/healthcheck/NA1"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)

        if response.status_code in (200, 404):
            return {
                "status": "ok",
                "riot": {
                    "key_configured": True,
                    "api_access": "active",
                },
            }

        if response.status_code in (401, 403):
            return {
                "status": "degraded",
                "riot": {
                    "key_configured": True,
                    "api_access": "expired",
                },
            }

        if response.status_code == 429:
            return {
                "status": "degraded",
                "riot": {
                    "key_configured": True,
                    "api_access": "rate_limited",
                },
            }

        return {
            "status": "degraded",
            "riot": {
                "key_configured": True,
                "api_access": f"http_{response.status_code}",
            },
        }
    except Exception:
        return {
            "status": "degraded",
            "riot": {
                "key_configured": True,
                "api_access": "unreachable",
            },
        }
