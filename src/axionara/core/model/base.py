from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field


class SystemStatusType(StrEnum):
    HEALTH = "health"
    UNHEALTH = "unhealth"


class SystemStatus(BaseModel):
    status: str
    version: str
