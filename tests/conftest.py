import asyncio
import shutil
from collections.abc import Generator
from io import BytesIO

import pytest
from fastapi import UploadFile
from openpyxl import Workbook
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.core.db.session import init_db_models, local_session
from tests import TEMP_SQLITE_FILEPATH, TEMP_STORAGE_ROOT


class DataStore(BaseModel):
    provider_token_data: str | None = None
    provider_user_id: str | None = None
    admin_user_id: str | None = None
    consumer_user_id: str | None = None
    uploaded_dataset_id: str | None = None
    uploaded_pdf_dataset_id: str | None = None
    uploaded_sql_dataset_id: str | None = None
    uploaded_xlsx_dataset_id: str | None = None


@pytest.fixture(scope="session", autouse=True)
def _initialize_database() -> None:
    TEMP_SQLITE_FILEPATH.unlink(missing_ok=True)
    shutil.rmtree(TEMP_STORAGE_ROOT, ignore_errors=True)
    TEMP_SQLITE_FILEPATH.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(init_db_models())


@pytest.fixture(name="db_session")
def test_db_session() -> Generator[AsyncSession, None, None]:
    db = local_session()
    try:
        yield db
    finally:
        asyncio.run(db.close())


@pytest.fixture(scope="session", name="data_store")
def test_data_store() -> DataStore:  # type: ignore
    return DataStore()


@pytest.fixture(name="csv_upload")
def test_csv_upload() -> UploadFile:
    return UploadFile(
        filename="population.csv",
        file=BytesIO(b"region,population\nA,10\nB,20\n"),
    )


@pytest.fixture(name="pdf_upload")
def test_pdf_upload() -> UploadFile:
    return UploadFile(
        filename="report.pdf",
        file=BytesIO(b"%PDF-1.4\n% demo pdf bytes\n"),
    )


@pytest.fixture(name="sql_upload")
def test_sql_upload() -> UploadFile:
    return UploadFile(
        filename="population.sql",
        file=BytesIO(
            b"CREATE TABLE population (region TEXT, population INTEGER);\n"
            b"INSERT INTO population VALUES ('A', 10);\n"
        ),
    )


@pytest.fixture(name="xlsx_upload")
def test_xlsx_upload() -> UploadFile:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "population"
    worksheet.append(["region", "population"])
    worksheet.append(["A", 10])
    worksheet.append(["B", 20])
    content = BytesIO()
    workbook.save(content)
    content.seek(0)
    return UploadFile(filename="population.xlsx", file=content)
