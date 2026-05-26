from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.services.catalog_service import CatalogService
from axionara.app.utils.constant import CONSTANT
from axionara.common.util import generate_random_token
from axionara.core.db.crud import (
    insert_access_grant,
    select_access_grants_by_user,
    select_active_access_grant,
    select_dataset_by_id,
    select_dataset_profile_by_dataset_id,
)
from axionara.core.db.models import (
    AccessGrant,
    DatasetAsset,
    DatasetProfile,
    Tag,
    UserAccount,
)
from axionara.core.model.dataset import DatasetAssetStatus


class AccessService:
    async def acquire_dataset(
        self,
        db: AsyncSession,
        dataset_id: str,
        user: UserAccount,
        grant_method: str = "demo_click",
    ) -> AccessGrant:
        dataset = await select_dataset_by_id(db=db, dataset_id=dataset_id)
        if dataset is None or dataset.status != DatasetAssetStatus.PUBLISHED.value:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)

        existing = await select_active_access_grant(
            db=db, dataset_id=dataset_id, user_id=user.id
        )
        if existing is not None:
            return existing

        return await insert_access_grant(
            db=db,
            grant=AccessGrant(
                id=generate_random_token(prefix="GRT", length=24),
                dataset_id=dataset_id,
                user_id=user.id,
                grant_method=grant_method,
                grant_status="granted",
            ),
        )

    async def list_my_datasets(
        self, db: AsyncSession, user: UserAccount
    ) -> list[tuple[AccessGrant, DatasetAsset, DatasetProfile, list[Tag]]]:
        rows = []
        catalog = CatalogService()
        grants = await select_access_grants_by_user(db=db, user_id=user.id)
        for grant in grants:
            dataset = await select_dataset_by_id(db=db, dataset_id=grant.dataset_id)
            if dataset is None or dataset.status != DatasetAssetStatus.PUBLISHED.value:
                continue
            profile = await select_dataset_profile_by_dataset_id(
                db=db, dataset_id=dataset.id
            )
            if profile is None:
                continue
            _, _, tags = await catalog.get_published_dataset(db=db, dataset_id=dataset.id)
            rows.append((grant, dataset, profile, tags))
        return rows
