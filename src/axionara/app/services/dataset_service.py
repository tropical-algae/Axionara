from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlmodel import Session

from axionara.app.utils.constant import CONSTANT
from axionara.common.config import settings
from axionara.common.util import generate_random_token
from axionara.core.db.crud import (
    insert_dataset_asset,
    select_dataset_by_id,
    select_datasets_by_owner,
)
from axionara.core.db.models import DatasetAsset, UserAccount
from axionara.core.model.dataset import DatasetAssetStatus, DatasetSourceFormat
from axionara.core.storage import LocalStorageService

SUPPORTED_UPLOAD_FORMATS = {item.value for item in DatasetSourceFormat}


def detect_source_format(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower().lstrip(".")
    if suffix not in SUPPORTED_UPLOAD_FORMATS:
        raise HTTPException(**CONSTANT.RESP_DATASET_UNSUPPORTED_TYPE)
    return suffix


async def create_dataset_asset(
    db: Session,
    owner: UserAccount,
    title: str,
    description: str | None,
    upload_file: UploadFile,
) -> DatasetAsset:
    source_format = detect_source_format(upload_file.filename)
    dataset_id = generate_random_token(prefix="DAT", length=24)
    original_filename = Path(upload_file.filename or f"{dataset_id}.{source_format}").name
    storage_uri = f"datasets/{dataset_id}/{original_filename}"
    payload = upload_file.file.read()
    upload_file.file.close()

    storage = LocalStorageService(root_dir=settings.LOCAL_STORAGE_ROOT)
    await storage.save_bytes(relative_path=storage_uri, content=payload)

    dataset = DatasetAsset(
        id=dataset_id,
        title=title,
        description=description,
        owner_id=owner.id,
        source_format=source_format,
        original_filename=original_filename,
        storage_uri=storage_uri,
        file_size_bytes=len(payload),
        status=DatasetAssetStatus.UPLOADED.value,
    )
    return insert_dataset_asset(db=db, dataset=dataset)


async def list_provider_datasets(db: Session, owner: UserAccount) -> list[DatasetAsset]:
    return select_datasets_by_owner(db=db, owner_id=owner.id)


async def get_provider_dataset(
    db: Session, owner: UserAccount, dataset_id: str
) -> DatasetAsset:
    dataset = select_dataset_by_id(db=db, dataset_id=dataset_id)
    if dataset is None:
        raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)
    if dataset.owner_id != owner.id and owner.role != "admin":
        raise HTTPException(**CONSTANT.RESP_DATASET_FORBIDDEN)
    return dataset
