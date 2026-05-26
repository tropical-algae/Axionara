from datetime import date
from typing import Annotated, Any

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
    title: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    description: Annotated[str | None, Form()] = None,
    category: Annotated[str | None, Form()] = None,
    source_organization: Annotated[str | None, Form()] = None,
    coverage_start: Annotated[date | None, Form()] = None,
    coverage_end: Annotated[date | None, Form()] = None,
    update_frequency: Annotated[str | None, Form()] = None,
    sensitivity_level: Annotated[str | None, Form()] = None,
    intended_visibility: Annotated[str | None, Form()] = None,
    access_policy: Annotated[str | None, Form()] = None,
    usage_restrictions: Annotated[str | None, Form()] = None,
    contact_name: Annotated[str | None, Form()] = None,
    contact_email: Annotated[str | None, Form()] = None,
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
