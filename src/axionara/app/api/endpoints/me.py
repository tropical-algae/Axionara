from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Security
from fastapi.responses import Response
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.api.deps import get_current_user, get_db
from axionara.app.services.access_service import AccessService
from axionara.app.services.content_rag_service import AuthorizedContentRagService
from axionara.app.services.export_service import (
    ExportService,
    process_export_job_background,
)
from axionara.core.db.models import UserAccount
from axionara.core.model.dataset import (
    AccessGrantRead,
    ContentRagRequest,
    ContentRagResponse,
    DatasetAssetRead,
    DatasetProfileRead,
    ExportJobRead,
    ExportRequest,
    MyDatasetRead,
)
from axionara.core.model.user import ScopeType

router = APIRouter()


@router.get("/datasets", response_model=list[MyDatasetRead])
async def my_datasets(
    current_user: UserAccount = Security(
        get_current_user,
        scopes=[
            ScopeType.CONSUMER.value,
            ScopeType.PROVIDER.value,
            ScopeType.ADMIN.value,
        ],
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    rows = await AccessService().list_my_datasets(db=db, user=current_user)
    return [
        MyDatasetRead(
            grant=AccessGrantRead.model_validate(grant),
            dataset=DatasetAssetRead.model_validate(dataset),
            profile=DatasetProfileRead.model_validate(profile),
            tags=[tag.slug for tag in tags],
        )
        for grant, dataset, profile, tags in rows
    ]


@router.post("/datasets/{dataset_id}/ask", response_model=ContentRagResponse)
async def ask_my_dataset_content(
    dataset_id: str,
    request: ContentRagRequest,
    current_user: UserAccount = Security(
        get_current_user,
        scopes=[
            ScopeType.CONSUMER.value,
            ScopeType.PROVIDER.value,
            ScopeType.ADMIN.value,
        ],
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await AuthorizedContentRagService().ask(
        db=db,
        dataset_id=dataset_id,
        question=request.question,
        user=current_user,
        limit=request.limit,
    )


@router.post("/datasets/{dataset_id}/exports", response_model=ExportJobRead)
async def request_dataset_export(
    dataset_id: str,
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    current_user: UserAccount = Security(
        get_current_user,
        scopes=[
            ScopeType.CONSUMER.value,
            ScopeType.PROVIDER.value,
            ScopeType.ADMIN.value,
        ],
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    job = await ExportService().create_export_job(
        db=db,
        dataset_id=dataset_id,
        target_format=request.target_format.value,
        user=current_user,
    )
    background_tasks.add_task(process_export_job_background, job.id)
    return job


@router.get("/exports", response_model=list[ExportJobRead])
async def my_export_jobs(
    dataset_id: str | None = None,
    current_user: UserAccount = Security(
        get_current_user,
        scopes=[
            ScopeType.CONSUMER.value,
            ScopeType.PROVIDER.value,
            ScopeType.ADMIN.value,
        ],
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await ExportService().list_my_export_jobs(
        db=db, user=current_user, dataset_id=dataset_id
    )


@router.get("/exports/{job_id}", response_model=ExportJobRead)
async def my_export_job_detail(
    job_id: str,
    current_user: UserAccount = Security(
        get_current_user,
        scopes=[
            ScopeType.CONSUMER.value,
            ScopeType.PROVIDER.value,
            ScopeType.ADMIN.value,
        ],
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await ExportService().get_my_export_job(
        db=db, job_id=job_id, user=current_user
    )


@router.post("/exports/{job_id}/retry", response_model=ExportJobRead)
async def retry_my_export(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user: UserAccount = Security(
        get_current_user,
        scopes=[
            ScopeType.CONSUMER.value,
            ScopeType.PROVIDER.value,
            ScopeType.ADMIN.value,
        ],
    ),
    db: AsyncSession = Depends(get_db),
) -> Any:
    job = await ExportService().retry_export_job(db=db, job_id=job_id, user=current_user)
    background_tasks.add_task(process_export_job_background, job.id)
    return job


@router.get("/exports/{job_id}/download", response_class=Response)
async def download_my_export(
    job_id: str,
    current_user: UserAccount = Security(
        get_current_user,
        scopes=[
            ScopeType.CONSUMER.value,
            ScopeType.PROVIDER.value,
            ScopeType.ADMIN.value,
        ],
    ),
    db: AsyncSession = Depends(get_db),
) -> Response:
    return await ExportService().download_export(db=db, job_id=job_id, user=current_user)
