import asyncio

import pytest
from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.api.deps import get_current_user
from axionara.app.api.endpoints.auth import (
    current_user_profile,
    login_access_token,
    user_register,
)
from axionara.app.api.endpoints.health import check_storage_status, check_system_status
from axionara.app.utils.security import verift_access_token
from axionara.common.config import settings
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

TEMP_ADMIN: dict = {
    "username": "admin_user",
    "password": "123456",
    "full_name": "Admin User",
    "organization": "Axionara Lab",
    "email": "admin@test.com",
    "role": ScopeType.ADMIN.value,
}

TEMP_CONSUMER: dict = {
    "username": "consumer_user",
    "password": "123456",
    "full_name": "Consumer User",
    "organization": "Axionara Lab",
    "email": "consumer@test.com",
    "role": ScopeType.CONSUMER.value,
}


@pytest.mark.run(order=1)
def test_system_status():
    response = asyncio.run(check_system_status())
    assert response.status == SystemStatusType.HEALTH.value


def test_storage_status_local_backend(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
    monkeypatch.setattr(settings, "LOCAL_STORAGE_ROOT", str(tmp_path / "storage"))

    response = asyncio.run(check_storage_status())

    assert response.status == SystemStatusType.HEALTH.value
    assert response.backend == "local"
    assert response.details["root_exists"] is True


@pytest.mark.run(order=2)
@pytest.mark.parametrize(
    "user",
    [TEMP_USER],
)
def test_user_register(db_session: AsyncSession, user: dict):
    payload = asyncio.run(user_register(user=UserBasicInfo(**user), db=db_session))
    assert payload.username == user["username"]
    assert payload.role == user["role"]


@pytest.mark.run(order=3)
@pytest.mark.parametrize(
    "user",
    [TEMP_USER],
)
def test_user_login_api(db_session: AsyncSession, data_store: DataStore, user: dict):
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
def test_user_token(db_session: AsyncSession, data_store: DataStore):
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


@pytest.mark.run(order=5)
def test_admin_register(db_session: AsyncSession, data_store: DataStore):
    payload = asyncio.run(user_register(user=UserBasicInfo(**TEMP_ADMIN), db=db_session))
    data_store.admin_user_id = payload.id
    assert payload.role == ScopeType.ADMIN.value


@pytest.mark.run(order=6)
def test_consumer_register(db_session: AsyncSession, data_store: DataStore):
    payload = asyncio.run(
        user_register(user=UserBasicInfo(**TEMP_CONSUMER), db=db_session)
    )
    data_store.consumer_user_id = payload.id
    assert payload.role == ScopeType.CONSUMER.value
