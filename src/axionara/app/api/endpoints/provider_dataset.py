from typing import Any

from fastapi import APIRouter, Depends, File, Form, Security, UploadFile
from sqlmodel import Session

from axionara.app.api.deps import get_current_user, get_db
from axionara.app.services.dataset_service import (
    create_dataset_asset,
    get_provider_dataset,
    list_provider_datasets,
)
from axionara.core.db.models import UserAccount
from axionara.core.model.dataset import DatasetAssetRead
from axionara.core.model.user import ScopeType

router = APIRouter()


@router.post("/datasets/upload", response_model=DatasetAssetRead)
async def upload_dataset(
    title: str = Form(...),
    description: str | None = Form(default=None),
    file: UploadFile = File(...),
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.PROVIDER.value, ScopeType.ADMIN.value]
    ),
    db: Session = Depends(get_db),
) -> Any:
    return await create_dataset_asset(
        db=db,
        owner=current_user,
        title=title,
        description=description,
        upload_file=file,
    )


@router.get("/datasets", response_model=list[DatasetAssetRead])
async def my_uploaded_datasets(
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.PROVIDER.value, ScopeType.ADMIN.value]
    ),
    db: Session = Depends(get_db),
) -> Any:
    return await list_provider_datasets(db=db, owner=current_user)


@router.get("/datasets/{dataset_id}", response_model=DatasetAssetRead)
async def uploaded_dataset_detail(
    dataset_id: str,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.PROVIDER.value, ScopeType.ADMIN.value]
    ),
    db: Session = Depends(get_db),
) -> Any:
    return await get_provider_dataset(db=db, owner=current_user, dataset_id=dataset_id)
