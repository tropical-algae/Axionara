from fastapi import APIRouter

from axionara.app.services.storage_service import check_storage_health
from axionara.common.config import settings
from axionara.core.model.base import StorageHealth, SystemStatus, SystemStatusType

router = APIRouter()


@router.get("/status", response_model=SystemStatus)
async def check_system_status() -> SystemStatus:
    return SystemStatus(status=SystemStatusType.HEALTH.value, version=settings.VERSION)


@router.get("/storage", response_model=StorageHealth)
async def check_storage_status() -> StorageHealth:
    return StorageHealth(**check_storage_health())
