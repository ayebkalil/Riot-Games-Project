from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.settings import settings
from api.routers.health import router as health_router
from api.routers.prediction import router as prediction_router
from api.routers.progression import router as progression_router
from api.routers.rank import router as rank_router
from api.routers.smurf import router as smurf_router
from api.routers.summoner import router as summoner_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(prediction_router, prefix=settings.api_prefix)
    app.include_router(rank_router, prefix=settings.api_prefix)
    app.include_router(progression_router, prefix=settings.api_prefix)
    app.include_router(smurf_router, prefix=settings.api_prefix)
    app.include_router(summoner_router, prefix=settings.api_prefix)
    return app


app = create_app()
