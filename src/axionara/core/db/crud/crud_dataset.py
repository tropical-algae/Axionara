from sqlmodel import Session, select

from axionara.core.db.models import DatasetAsset


def insert_dataset_asset(db: Session, dataset: DatasetAsset) -> DatasetAsset:
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def select_dataset_by_id(db: Session, dataset_id: str) -> DatasetAsset | None:
    result = db.exec(select(DatasetAsset).where(DatasetAsset.id == dataset_id))
    return result.first()


def select_datasets_by_owner(db: Session, owner_id: str) -> list[DatasetAsset]:
    result = db.exec(
        select(DatasetAsset)
        .where(DatasetAsset.owner_id == owner_id)
        .order_by(DatasetAsset.create_date.desc())
    )
    return list(result.all())


def select_all_datasets(db: Session) -> list[DatasetAsset]:
    result = db.exec(select(DatasetAsset).order_by(DatasetAsset.create_date.desc()))
    return list(result.all())


def select_datasets_by_status(db: Session, status: str) -> list[DatasetAsset]:
    result = db.exec(
        select(DatasetAsset)
        .where(DatasetAsset.status == status)
        .order_by(DatasetAsset.create_date.desc())
    )
    return list(result.all())
