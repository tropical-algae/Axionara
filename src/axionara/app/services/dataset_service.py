from datetime import date
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.services.storage_service import get_storage_service
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

SUPPORTED_UPLOAD_FORMATS = {item.value for item in DatasetSourceFormat}


def detect_source_format(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower().lstrip(".")
    if suffix not in SUPPORTED_UPLOAD_FORMATS:
        raise HTTPException(**CONSTANT.RESP_DATASET_UNSUPPORTED_TYPE)
    return suffix


async def create_dataset_asset(
    db: AsyncSession,
    owner: UserAccount,
    title: str,
    description: str | None,
    upload_file: UploadFile,
    category: str | None = None,
    source_organization: str | None = None,
    coverage_start: date | None = None,
    coverage_end: date | None = None,
    update_frequency: str | None = None,
    sensitivity_level: str | None = None,
    intended_visibility: str | None = None,
    access_policy: str | None = None,
    usage_restrictions: str | None = None,
    contact_name: str | None = None,
    contact_email: str | None = None,
) -> DatasetAsset:
    source_format = detect_source_format(upload_file.filename)
    dataset_id = generate_random_token(prefix="DAT", length=24)
    original_filename = Path(upload_file.filename or f"{dataset_id}.{source_format}").name
    object_key = f"raw/{dataset_id}/{original_filename}"
    payload = upload_file.file.read()
    upload_file.file.close()

    storage = get_storage_service()
    stored = storage.save_bytes(
        bucket=settings.MINIO_BUCKET_RAW,
        object_key=object_key,
        content=payload,
        content_type=upload_file.content_type,
    )

    dataset = DatasetAsset(
        id=dataset_id,
        title=title,
        description=description,
        category=category,
        source_organization=source_organization,
        coverage_start=coverage_start,
        coverage_end=coverage_end,
        update_frequency=update_frequency,
        sensitivity_level=sensitivity_level,
        intended_visibility=intended_visibility,
        access_policy=access_policy,
        usage_restrictions=usage_restrictions,
        contact_name=contact_name,
        contact_email=contact_email,
        owner_id=owner.id,
        source_format=source_format,
        original_filename=original_filename,
        storage_uri=stored.uri,
        raw_bucket=stored.bucket,
        raw_object_key=stored.object_key,
        content_type=stored.content_type,
        etag=stored.etag,
        file_size_bytes=stored.size,
        status=DatasetAssetStatus.UPLOADED.value,
    )
    return await insert_dataset_asset(db=db, dataset=dataset)


async def list_provider_datasets(
    db: AsyncSession, owner: UserAccount
) -> list[DatasetAsset]:
    return await select_datasets_by_owner(db=db, owner_id=owner.id)


async def get_provider_dataset(
    db: AsyncSession, owner: UserAccount, dataset_id: str
) -> DatasetAsset:
    dataset = await select_dataset_by_id(db=db, dataset_id=dataset_id)
    if dataset is None:
        raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)
    if dataset.owner_id != owner.id and owner.role != "admin":
        raise HTTPException(**CONSTANT.RESP_DATASET_FORBIDDEN)
    return dataset
