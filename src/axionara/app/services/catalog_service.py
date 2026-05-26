from fastapi import HTTPException
from sqlmodel import Session

from axionara.app.utils.constant import CONSTANT
from axionara.core.db.crud import (
    select_all_active_tags,
    select_dataset_by_id,
    select_dataset_profile_by_dataset_id,
    select_dataset_tags,
    select_datasets_by_status,
)
from axionara.core.db.models import DatasetAsset, DatasetProfile, Tag
from axionara.core.model.dataset import DatasetAssetStatus


class CatalogService:
    def list_published_datasets(
        self,
        db: Session,
        tag_slug: str | None = None,
        category: str | None = None,
        source_format: str | None = None,
        keyword: str | None = None,
    ) -> list[tuple[DatasetAsset, DatasetProfile, list[Tag]]]:
        datasets = select_datasets_by_status(
            db=db, status=DatasetAssetStatus.PUBLISHED.value
        )
        result = []
        for dataset in datasets:
            if source_format and dataset.source_format != source_format:
                continue
            if keyword and keyword.lower() not in (
                f"{dataset.title} {dataset.description or ''}".lower()
            ):
                continue
            profile = select_dataset_profile_by_dataset_id(db=db, dataset_id=dataset.id)
            if profile is None:
                continue
            tags = self._load_tags(db=db, dataset_id=dataset.id)
            if tag_slug and not any(tag.slug == tag_slug for tag in tags):
                continue
            if category and not any(tag.category == category for tag in tags):
                continue
            result.append((dataset, profile, tags))
        return result

    def get_published_dataset(
        self, db: Session, dataset_id: str
    ) -> tuple[DatasetAsset, DatasetProfile, list[Tag]]:
        dataset = select_dataset_by_id(db=db, dataset_id=dataset_id)
        if dataset is None or dataset.status != DatasetAssetStatus.PUBLISHED.value:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)
        profile = select_dataset_profile_by_dataset_id(db=db, dataset_id=dataset_id)
        if profile is None:
            raise HTTPException(**CONSTANT.RESP_PROFILE_NOT_EXISTS)
        return dataset, profile, self._load_tags(db=db, dataset_id=dataset_id)

    def list_tags(self, db: Session) -> list[Tag]:
        return select_all_active_tags(db=db)

    def _load_tags(self, db: Session, dataset_id: str) -> list[Tag]:
        dataset_tags = select_dataset_tags(db=db, dataset_id=dataset_id)
        tags = []
        all_tags = {tag.id: tag for tag in select_all_active_tags(db=db)}
        for dataset_tag in dataset_tags:
            tag = all_tags.get(dataset_tag.tag_id)
            if tag is not None:
                tags.append(tag)
        return tags
