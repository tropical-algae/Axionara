from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Security
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.api.deps import get_current_user, get_db
from axionara.app.services.analysis_service import (
    AnalysisOrchestrator,
    process_analysis_job_background,
)
from axionara.app.services.review_service import ReviewService
from axionara.core.db.crud import select_all_datasets, select_datasets_by_status
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


@router.get("/datasets", response_model=list[DatasetAssetRead])
async def admin_datasets(
    status: str | None = None,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    _ = current_user
    if status is not None:
        return await select_datasets_by_status(db=db, status=status)
    return await select_all_datasets(db=db)


@router.post("/datasets/{dataset_id}/analyze", response_model=AnalysisJobRead)
async def analyze_dataset(
    dataset_id: str,
    background_tasks: BackgroundTasks,
    use_llm: bool = False,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    job = await AnalysisOrchestrator().create_analysis_job(
        db=db, dataset_id=dataset_id, triggered_by=current_user
    )
    background_tasks.add_task(process_analysis_job_background, job.id, use_llm)
    return job


@router.get("/datasets/{dataset_id}/analysis/latest", response_model=DatasetAnalysisRead)
async def latest_dataset_analysis(
    dataset_id: str,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    _ = current_user
    return await AnalysisOrchestrator().get_latest_analysis(db=db, dataset_id=dataset_id)


@router.get("/analysis-jobs", response_model=list[AnalysisJobRead])
async def analysis_jobs(
    dataset_id: str | None = None,
    job_status: str | None = None,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    _ = current_user
    return await AnalysisOrchestrator().list_analysis_jobs(
        db=db,
        dataset_id=dataset_id,
        job_status=job_status,
    )


@router.get("/analysis-jobs/{job_id}", response_model=AnalysisJobRead)
async def analysis_job_detail(
    job_id: str,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    _ = current_user
    return await AnalysisOrchestrator().get_analysis_job(db=db, job_id=job_id)


@router.get("/reviews", response_model=list[DatasetReviewRead])
async def dataset_reviews(
    dataset_id: str | None = None,
    review_status: str | None = None,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    _ = current_user
    return await ReviewService().list_reviews(
        db=db,
        dataset_id=dataset_id,
        review_status=review_status,
    )


@router.post("/analysis-jobs/{job_id}/retry", response_model=AnalysisJobRead)
async def retry_analysis_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    use_llm: bool = False,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    job = await AnalysisOrchestrator().create_retry_analysis_job(
        db=db,
        job_id=job_id,
        triggered_by=current_user,
    )
    background_tasks.add_task(process_analysis_job_background, job.id, use_llm)
    return job


@router.get("/datasets/pending", response_model=list[DatasetAssetRead])
async def pending_datasets(
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    _ = current_user
    return await select_datasets_by_status(db=db, status="reviewed")


@router.post("/datasets/{dataset_id}/approve", response_model=DatasetReviewRead)
async def approve_dataset(
    dataset_id: str,
    request: ReviewRequest | None = None,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await ReviewService().approve_dataset(
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
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await ReviewService().reject_dataset(
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
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await ReviewService().publish_dataset(
        db=db,
        dataset_id=dataset_id,
        publisher=current_user,
        comment=request.comment if request else None,
    )


@router.post("/datasets/{dataset_id}/archive", response_model=DatasetReviewRead)
async def archive_dataset(
    dataset_id: str,
    request: ReviewRequest | None = None,
    current_user: UserAccount = Security(
        get_current_user, scopes=[ScopeType.ADMIN.value]
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await ReviewService().archive_dataset(
        db=db,
        dataset_id=dataset_id,
        reviewer=current_user,
        comment=request.comment if request else None,
    )
