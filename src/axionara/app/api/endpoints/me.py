from typing import Any

from fastapi import APIRouter, Depends, Security
from sqlmodel import Session

from axionara.app.api.deps import get_current_user, get_db
from axionara.app.services.access_service import AccessService
from axionara.core.db.models import UserAccount
from axionara.core.model.dataset import (
    AccessGrantRead,
    DatasetAssetRead,
    DatasetProfileRead,
    MyDatasetRead,
)
from axionara.core.model.user import ScopeType

router = APIRouter()


@router.get("/datasets", response_model=list[MyDatasetRead])
async def my_datasets(
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.CONSUMER.value, ScopeType.ADMIN.value]
    ),
    db: Session = Depends(get_db),
) -> Any:
    rows = AccessService().list_my_datasets(db=db, user=current_user)
    return [
        MyDatasetRead(
            grant=AccessGrantRead.model_validate(grant),
            dataset=DatasetAssetRead.model_validate(dataset),
            profile=DatasetProfileRead.model_validate(profile),
            tags=[tag.slug for tag in tags],
        )
        for grant, dataset, profile, tags in rows
    ]
