from fastapi import APIRouter

from axionara.app.api.endpoints import (
    admin_dataset,
    auth,
    catalog,
    health,
    me,
    provider_dataset,
)

router = APIRouter()
router.include_router(health.router, prefix="/system", tags=["system status"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(
    provider_dataset.router, prefix="/provider", tags=["provider dataset"]
)
router.include_router(admin_dataset.router, prefix="/admin", tags=["admin dataset"])
router.include_router(catalog.router, prefix="/catalog", tags=["catalog"])
router.include_router(me.router, prefix="/me", tags=["my datasets"])
