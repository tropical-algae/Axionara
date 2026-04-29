import json
from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from axionara.common.util import generate_random_token
from axionara.core.db.models import UserAccount


class ScopeType(StrEnum):
    ADMIN = "admin"
    PROVIDER = "provider"
    CONSUMER = "consumer"


class Token(BaseModel):
    user_id: str
    access_token: str
    token_type: str
    scopes: list[str]


class TokenPayload(BaseModel):
    userid: str
    username: str
    scopes: list[ScopeType]
    exp: datetime = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        data = self.model_dump()
        scopes: list[ScopeType] = data.get("scopes", [])
        data["scopes"] = [s.value for s in scopes]
        return data

    def match_scope(self, scope: list[str]):
        exp_str = [s.value for s in self.scopes]
        return any(s in scope for s in exp_str)


class UserBasicInfo(BaseModel):
    username: str = Field(description="User login name")
    password: str = Field(description="User password")
    email: str = Field(description="The email of user")
    full_name: str | None = Field(default=None, description="Display name of user")
    organization: str | None = Field(default=None, description="The organization of user")
    role: ScopeType = Field(default=ScopeType.CONSUMER, description="Role of user")

    def build_user(self) -> UserAccount:
        return UserAccount(
            id=generate_random_token(prefix="USR", length=24),
            username=self.username,
            full_name=self.full_name or self.username,
            password=self.password,
            email=self.email,
            scopes=json.dumps([self.role.value]),
            role=self.role.value,
            organization=self.organization,
            is_superuser=self.role == ScopeType.ADMIN,
            is_active=True,
        )


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    full_name: str | None = None
    organization: str | None = None
    role: str
    is_active: bool | None = None
    create_date: datetime | None = None
