from fastapi import APIRouter

from axionara.app.api.endpoints import auth, health, provider_dataset

router = APIRouter()
router.include_router(health.router, prefix="/system", tags=["system status"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(
    provider_dataset.router, prefix="/provider", tags=["provider dataset"]
)
