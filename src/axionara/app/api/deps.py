from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.utils.constant import CONSTANT
from axionara.app.utils.security import verift_access_token
from axionara.common.config import settings
from axionara.core.db.crud import select_user_by_id
from axionara.core.db.models import UserAccount
from axionara.core.db.session import local_session
from axionara.core.model.user import ScopeType

AUTHENTICATE_HEADER = "WWW-Authenticate"


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/access-token",
    scopes={
        ScopeType.ADMIN.value: CONSTANT.ROLE_ADMIN_DESCRIPTION,
        ScopeType.PROVIDER.value: CONSTANT.ROLE_PROVIDER_DESCRIPTION,
        ScopeType.CONSUMER.value: CONSTANT.ROLE_CONSUMER_DESCRIPTION,
    },
    auto_error=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as db:
        yield db


async def get_current_user(
    security_scopes: SecurityScopes,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2),
) -> UserAccount:
    headers = {AUTHENTICATE_HEADER: "Bearer"}
    if security_scopes.scopes:
        headers = {AUTHENTICATE_HEADER: f'Bearer scope="{security_scopes.scope_str}"'}
    payload = verift_access_token(token=token, headers=headers)
    user = await select_user_by_id(db=db, user_id=payload.userid)
    if user is None:
        raise HTTPException(headers=headers, **CONSTANT.RESP_USER_NOT_EXISTS)
    if len(security_scopes.scopes) != 0 and not payload.match_scope(
        security_scopes.scopes
    ):
        raise HTTPException(headers=headers, **CONSTANT.RESP_USER_FORBIDDEN)
    return user
