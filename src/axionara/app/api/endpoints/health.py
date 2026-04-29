from fastapi import APIRouter, HTTPException, Request, Security

from axionara.common.config import settings
from axionara.core.model.base import SystemStatus, SystemStatusType

router = APIRouter()


@router.get("/status", response_model=SystemStatus)
async def check_system_status() -> SystemStatus:
    return SystemStatus(status=SystemStatusType.HEALTH.value, version=settings.VERSION)
