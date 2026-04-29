import asyncio

import pytest
from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes
from sqlmodel import Session

from axionara.app.api.deps import get_current_user
from axionara.app.api.endpoints.auth import (
    current_user_profile,
    login_access_token,
    user_register,
)
from axionara.app.api.endpoints.health import check_system_status
from axionara.app.utils.security import verift_access_token
from axionara.core.model.base import SystemStatusType
from axionara.core.model.user import ScopeType, TokenPayload, UserBasicInfo
from tests.conftest import DataStore

TEMP_USER: dict = {
    "username": "provider_user",
    "password": "123456",
    "full_name": "Provider User",
    "organization": "Axionara Lab",
    "email": "provider@test.com",
    "role": ScopeType.PROVIDER.value,
}


@pytest.mark.run(order=1)
def test_system_status():
    response = asyncio.run(check_system_status())
    assert response.status == SystemStatusType.HEALTH.value


@pytest.mark.run(order=2)
@pytest.mark.parametrize(
    "user",
    [TEMP_USER],
)
def test_user_register(db_session: Session, user: dict):
    payload = asyncio.run(user_register(user=UserBasicInfo(**user), db=db_session))
    assert payload.username == user["username"]
    assert payload.role == user["role"]


@pytest.mark.run(order=3)
@pytest.mark.parametrize(
    "user",
    [TEMP_USER],
)
def test_user_login_api(db_session: Session, data_store: DataStore, user: dict):
    payload = asyncio.run(
        login_access_token(
            db=db_session,
            form_data=OAuth2PasswordRequestForm(
                username=user["username"],
                password=user["password"],
                scope="",
            ),
        )
    )

    assert payload.access_token

    # store token data
    data_store.provider_token_data = payload.access_token
    data_store.provider_user_id = payload.user_id


@pytest.mark.run(order=4)
def test_user_token(db_session: Session, data_store: DataStore):
    token_payload: TokenPayload = verift_access_token(data_store.provider_token_data)
    user = asyncio.run(
        get_current_user(
            security_scopes=SecurityScopes(scopes=[ScopeType.PROVIDER.value]),
            db=db_session,
            token=data_store.provider_token_data,
        )
    )

    assert user is not None
    profile = asyncio.run(current_user_profile(current_user=user))
    assert token_payload.username == TEMP_USER["username"]
    assert profile.username == TEMP_USER["username"]
