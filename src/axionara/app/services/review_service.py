from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session

from axionara.app.utils.constant import CONSTANT
from axionara.common.util import generate_random_token
from axionara.core.db.crud import (
    insert_dataset_review,
    select_dataset_by_id,
    select_latest_dataset_analysis,
    select_latest_dataset_review,
    update_dataset_asset,
    update_dataset_review,
)
from axionara.core.db.models import DatasetReview, UserAccount
from axionara.core.model.dataset import DatasetAssetStatus


class ReviewService:
    def approve_dataset(
        self,
        db: Session,
        dataset_id: str,
        reviewer: UserAccount,
        comment: str | None = None,
    ) -> DatasetReview:
        dataset = self._get_dataset_for_review(db=db, dataset_id=dataset_id)
        analysis = select_latest_dataset_analysis(db=db, dataset_id=dataset_id)
        if analysis is None:
            raise HTTPException(**CONSTANT.RESP_ANALYSIS_NOT_EXISTS)

        review = insert_dataset_review(
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
        update_dataset_asset(db=db, dataset=dataset)
        return review

    def reject_dataset(
        self,
        db: Session,
        dataset_id: str,
        reviewer: UserAccount,
        comment: str | None = None,
    ) -> DatasetReview:
        dataset = select_dataset_by_id(db=db, dataset_id=dataset_id)
        if dataset is None:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)
        analysis = select_latest_dataset_analysis(db=db, dataset_id=dataset_id)
        if analysis is None:
            raise HTTPException(**CONSTANT.RESP_ANALYSIS_NOT_EXISTS)

        review = insert_dataset_review(
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
        update_dataset_asset(db=db, dataset=dataset)
        return review

    def publish_dataset(
        self,
        db: Session,
        dataset_id: str,
        publisher: UserAccount,
        comment: str | None = None,
    ) -> DatasetReview:
        dataset = select_dataset_by_id(db=db, dataset_id=dataset_id)
        if dataset is None:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)
        review = select_latest_dataset_review(db=db, dataset_id=dataset_id)
        if review is None or review.review_status not in {"approved", "published"}:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_PUBLISHABLE)

        review.review_status = "published"
        review.publish_comment = comment
        review.published_at = datetime.now()
        review.reviewer_id = review.reviewer_id or publisher.id
        dataset.status = DatasetAssetStatus.PUBLISHED.value
        update_dataset_asset(db=db, dataset=dataset)
        return update_dataset_review(db=db, review=review)

    def _get_dataset_for_review(self, db: Session, dataset_id: str):
        dataset = select_dataset_by_id(db=db, dataset_id=dataset_id)
        if dataset is None:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)
        if dataset.status not in {
            DatasetAssetStatus.REVIEWED.value,
            DatasetAssetStatus.PROCESSING_REVIEW.value,
        }:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_REVIEWABLE)
        return dataset
