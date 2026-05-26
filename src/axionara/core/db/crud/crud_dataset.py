from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.core.db.models import DatasetAsset


async def insert_dataset_asset(db: AsyncSession, dataset: DatasetAsset) -> DatasetAsset:
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    return dataset


async def select_dataset_by_id(db: AsyncSession, dataset_id: str) -> DatasetAsset | None:
    result = await db.exec(select(DatasetAsset).where(DatasetAsset.id == dataset_id))
    return result.first()


async def select_datasets_by_owner(db: AsyncSession, owner_id: str) -> list[DatasetAsset]:
    result = await db.exec(
        select(DatasetAsset)
        .where(DatasetAsset.owner_id == owner_id)
        .order_by(DatasetAsset.create_date.desc())  # type: ignore
    )
    return list(result.all())


async def select_all_datasets(db: AsyncSession) -> list[DatasetAsset]:
    result = await db.exec(
        select(DatasetAsset).order_by(DatasetAsset.create_date.desc())  # type: ignore
    )
    return list(result.all())


async def select_datasets_by_status(db: AsyncSession, status: str) -> list[DatasetAsset]:
    result = await db.exec(
        select(DatasetAsset)
        .where(DatasetAsset.status == status)
        .order_by(DatasetAsset.create_date.desc())  # type: ignore
    )
    return list(result.all())
