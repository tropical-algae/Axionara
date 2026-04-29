import shutil
from collections.abc import Generator
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile
from pydantic import BaseModel
from sqlmodel import Session

from axionara.core.db.session import init_db_models, local_session


class DataStore(BaseModel):
    provider_token_data: str | None = None
    provider_user_id: str | None = None
    uploaded_dataset_id: str | None = None


@pytest.fixture(scope="session", autouse=True)
def initialize_database() -> Generator[None, None, None]:
    Path("cache/database.db").unlink(missing_ok=True)
    shutil.rmtree("cache/storage", ignore_errors=True)
    init_db_models()
    return


@pytest.fixture(scope="session", name="db_session")
def test_db_session() -> Generator[Session, None, None]:
    with local_session() as db:
        yield db


@pytest.fixture(scope="session", name="data_store")
def test_data_store() -> DataStore:  # type: ignore
    return DataStore()


@pytest.fixture(name="csv_upload")
def test_csv_upload() -> UploadFile:
    return UploadFile(
        filename="population.csv",
        file=BytesIO(b"region,population\nA,10\nB,20\n"),
    )
