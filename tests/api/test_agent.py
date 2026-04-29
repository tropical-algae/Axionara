import asyncio

import pytest
from fastapi import UploadFile
from sqlmodel import Session

from axionara.app.api.endpoints.provider_dataset import (
    my_uploaded_datasets,
    upload_dataset,
    uploaded_dataset_detail,
)
from axionara.core.db.crud import select_user_by_id, select_user_by_username
from tests.conftest import DataStore


@pytest.mark.run(order=5)
def test_provider_dataset_upload(
    db_session: Session, data_store: DataStore, csv_upload: UploadFile
):
    user = select_user_by_id(db=db_session, user_id=data_store.provider_user_id)
    if user is None:
        user = select_user_by_username(db=db_session, username="provider_user")
    assert user is not None

    response = asyncio.run(
        upload_dataset(
            title="Population Dataset",
            description="Demo csv upload",
            file=csv_upload,
            current_user=user,
            db=db_session,
        )
    )

    assert response.source_format == "csv"
    assert response.status == "uploaded"
    data_store.uploaded_dataset_id = response.id


@pytest.mark.run(order=6)
def test_provider_dataset_list(db_session: Session, data_store: DataStore):
    user = select_user_by_id(db=db_session, user_id=data_store.provider_user_id)
    if user is None:
        user = select_user_by_username(db=db_session, username="provider_user")
    assert user is not None

    response = asyncio.run(my_uploaded_datasets(current_user=user, db=db_session))
    assert len(response) == 1
    assert response[0].id == data_store.uploaded_dataset_id


@pytest.mark.run(order=7)
def test_provider_dataset_detail(db_session: Session, data_store: DataStore):
    user = select_user_by_id(db=db_session, user_id=data_store.provider_user_id)
    if user is None:
        user = select_user_by_username(db=db_session, username="provider_user")
    assert user is not None

    response = asyncio.run(
        uploaded_dataset_detail(
            dataset_id=data_store.uploaded_dataset_id,
            current_user=user,
            db=db_session,
        )
    )
    assert response.title == "Population Dataset"
