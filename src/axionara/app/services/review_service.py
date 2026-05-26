from datetime import datetime

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.utils.constant import CONSTANT
from axionara.common.util import generate_random_token
from axionara.core.db.crud import (
    insert_dataset_review,
    select_dataset_by_id,
    select_dataset_reviews,
    select_latest_dataset_analysis,
    select_latest_dataset_review,
    update_dataset_asset,
    update_dataset_review,
)
from axionara.core.db.models import DatasetReview, UserAccount
from axionara.core.model.dataset import DatasetAssetStatus


class ReviewService:
    async def approve_dataset(
        self,
        db: AsyncSession,
        dataset_id: str,
        reviewer: UserAccount,
        comment: str | None = None,
    ) -> DatasetReview:
        dataset = await self._get_dataset_for_review(db=db, dataset_id=dataset_id)
        analysis = await select_latest_dataset_analysis(db=db, dataset_id=dataset_id)
        if analysis is None:
            raise HTTPException(**CONSTANT.RESP_ANALYSIS_NOT_EXISTS)

        review = await insert_dataset_review(
            db=db,
            review=DatasetReview(
                id=generate_random_token(prefix="REV", length=24),
                dataset_id=dataset_id,
                analysis_id=analysis.id,
                reviewer_id=reviewer.id,
                review_status="approved",
                review_comment=comment,
                reviewed_at=datetime.now(),
            ),
        )
        dataset.status = DatasetAssetStatus.REVIEWED.value
        await update_dataset_asset(db=db, dataset=dataset)
        return review

    async def reject_dataset(
        self,
        db: AsyncSession,
        dataset_id: str,
        reviewer: UserAccount,
        comment: str | None = None,
    ) -> DatasetReview:
        dataset = await select_dataset_by_id(db=db, dataset_id=dataset_id)
        if dataset is None:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)
        analysis = await select_latest_dataset_analysis(db=db, dataset_id=dataset_id)
        if analysis is None:
            raise HTTPException(**CONSTANT.RESP_ANALYSIS_NOT_EXISTS)

        review = await insert_dataset_review(
            db=db,
            review=DatasetReview(
                id=generate_random_token(prefix="REV", length=24),
                dataset_id=dataset_id,
                analysis_id=analysis.id,
                reviewer_id=reviewer.id,
                review_status="rejected",
                review_comment=comment,
                reviewed_at=datetime.now(),
            ),
        )
        dataset.status = DatasetAssetStatus.REJECTED.value
        await update_dataset_asset(db=db, dataset=dataset)
        return review

    async def publish_dataset(
        self,
        db: AsyncSession,
        dataset_id: str,
        publisher: UserAccount,
        comment: str | None = None,
    ) -> DatasetReview:
        dataset = await select_dataset_by_id(db=db, dataset_id=dataset_id)
        if dataset is None:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)
        review = await select_latest_dataset_review(db=db, dataset_id=dataset_id)
        if review is None or review.review_status not in {"approved", "published"}:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_PUBLISHABLE)

        review.review_status = "published"
        review.publish_comment = comment
        review.published_at = datetime.now()
        review.reviewer_id = review.reviewer_id or publisher.id
        dataset.status = DatasetAssetStatus.PUBLISHED.value
        await update_dataset_asset(db=db, dataset=dataset)
        return await update_dataset_review(db=db, review=review)

    async def archive_dataset(
        self,
        db: AsyncSession,
        dataset_id: str,
        reviewer: UserAccount,
        comment: str | None = None,
    ) -> DatasetReview:
        dataset = await select_dataset_by_id(db=db, dataset_id=dataset_id)
        if dataset is None:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)
        if dataset.status not in {
            DatasetAssetStatus.PUBLISHED.value,
            DatasetAssetStatus.REJECTED.value,
        }:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_ARCHIVABLE)
        analysis = await select_latest_dataset_analysis(db=db, dataset_id=dataset_id)
        if analysis is None:
            raise HTTPException(**CONSTANT.RESP_ANALYSIS_NOT_EXISTS)

        dataset.status = DatasetAssetStatus.ARCHIVED.value
        await update_dataset_asset(db=db, dataset=dataset)
        return await insert_dataset_review(
            db=db,
            review=DatasetReview(
                id=generate_random_token(prefix="REV", length=24),
                dataset_id=dataset_id,
                analysis_id=analysis.id,
                reviewer_id=reviewer.id,
                review_status="archived",
                review_comment=comment,
                reviewed_at=datetime.now(),
            ),
        )

    async def list_reviews(
        self,
        db: AsyncSession,
        dataset_id: str | None = None,
        review_status: str | None = None,
    ) -> list[DatasetReview]:
        return await select_dataset_reviews(
            db=db,
            dataset_id=dataset_id,
            review_status=review_status,
        )

    async def _get_dataset_for_review(self, db: AsyncSession, dataset_id: str):
        dataset = await select_dataset_by_id(db=db, dataset_id=dataset_id)
        if dataset is None:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)
        if dataset.status not in {
            DatasetAssetStatus.REVIEWED.value,
            DatasetAssetStatus.PROCESSING_REVIEW.value,
        }:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_REVIEWABLE)
        return dataset
