from typing import Any

from fastapi import APIRouter, Depends, Security
from sqlmodel import Session

from axionara.app.api.deps import get_current_user, get_db
from axionara.app.services.analysis_service import AnalysisOrchestrator
from axionara.app.services.review_service import ReviewService
from axionara.core.db.crud import select_datasets_by_status
from axionara.core.db.models import UserAccount
from axionara.core.model.dataset import (
    AnalysisJobRead,
    DatasetAnalysisRead,
    DatasetAssetRead,
    DatasetReviewRead,
    ReviewRequest,
)
from axionara.core.model.user import ScopeType

router = APIRouter()


@router.post("/datasets/{dataset_id}/analyze", response_model=AnalysisJobRead)
async def analyze_dataset(
    dataset_id: str,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: Session = Depends(get_db),
) -> Any:
    return AnalysisOrchestrator().run_dataset_analysis(
        db=db, dataset_id=dataset_id, triggered_by=current_user, use_llm=False
    )


@router.get("/datasets/{dataset_id}/analysis/latest", response_model=DatasetAnalysisRead)
async def latest_dataset_analysis(
    dataset_id: str,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: Session = Depends(get_db),
) -> Any:
    _ = current_user
    return AnalysisOrchestrator().get_latest_analysis(db=db, dataset_id=dataset_id)


@router.get("/datasets/pending", response_model=list[DatasetAssetRead])
async def pending_datasets(
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: Session = Depends(get_db),
) -> Any:
    _ = current_user
    return select_datasets_by_status(db=db, status="reviewed")


@router.post("/datasets/{dataset_id}/approve", response_model=DatasetReviewRead)
async def approve_dataset(
    dataset_id: str,
    request: ReviewRequest | None = None,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: Session = Depends(get_db),
) -> Any:
    return ReviewService().approve_dataset(
        db=db,
        dataset_id=dataset_id,
        reviewer=current_user,
        comment=request.comment if request else None,
    )


@router.post("/datasets/{dataset_id}/reject", response_model=DatasetReviewRead)
async def reject_dataset(
    dataset_id: str,
    request: ReviewRequest | None = None,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: Session = Depends(get_db),
) -> Any:
    return ReviewService().reject_dataset(
        db=db,
        dataset_id=dataset_id,
        reviewer=current_user,
        comment=request.comment if request else None,
    )


@router.post("/datasets/{dataset_id}/publish", response_model=DatasetReviewRead)
async def publish_dataset(
    dataset_id: str,
    request: ReviewRequest | None = None,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: Session = Depends(get_db),
) -> Any:
    return ReviewService().publish_dataset(
        db=db,
        dataset_id=dataset_id,
        publisher=current_user,
        comment=request.comment if request else None,
    )
