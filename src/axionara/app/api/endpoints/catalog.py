from typing import Any

from fastapi import APIRouter, Depends, Security
from fastapi.responses import StreamingResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.api.deps import get_current_user, get_db
from axionara.app.services.access_service import AccessService
from axionara.app.services.catalog_rag_service import CatalogRagService
from axionara.app.services.catalog_service import CatalogService
from axionara.core.db.models import UserAccount
from axionara.core.model.dataset import (
    AccessGrantRead,
    CatalogDatasetRead,
    CatalogRagRequest,
    CatalogRagResponse,
    DatasetAssetRead,
    DatasetProfileRead,
    TagRead,
)
from axionara.core.model.user import ScopeType

router = APIRouter()


@router.get("/datasets", response_model=list[CatalogDatasetRead])
async def list_catalog_datasets(
    tag_slug: str | None = None,
    category: str | None = None,
    source_format: str | None = None,
    keyword: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    rows = await CatalogService().list_published_datasets(
        db=db,
        tag_slug=tag_slug,
        category=category,
        source_format=source_format,
        keyword=keyword,
    )
    return [
        CatalogDatasetRead(
            dataset=DatasetAssetRead.model_validate(dataset),
            profile=DatasetProfileRead.model_validate(profile),
            tags=[tag.slug for tag in tags],
        )
        for dataset, profile, tags in rows
    ]


@router.get("/datasets/{dataset_id}", response_model=CatalogDatasetRead)
async def catalog_dataset_detail(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    dataset, profile, tags = await CatalogService().get_published_dataset(
        db=db, dataset_id=dataset_id
    )
    return CatalogDatasetRead(
        dataset=DatasetAssetRead.model_validate(dataset),
        profile=DatasetProfileRead.model_validate(profile),
        tags=[tag.slug for tag in tags],
    )


@router.get("/tags", response_model=list[TagRead])
async def list_catalog_tags(db: AsyncSession = Depends(get_db)) -> Any:
    return await CatalogService().list_tags(db=db)


@router.post("/ask", response_model=CatalogRagResponse)
async def ask_catalog_dataset_profiles(
    request: CatalogRagRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await CatalogRagService().ask(
        db=db,
        question=request.question,
        dataset_id=request.dataset_id,
        tag_slug=request.tag_slug,
        limit=request.limit,
    )


@router.post("/ask/stream")
async def stream_catalog_dataset_profiles(
    request: CatalogRagRequest,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    return StreamingResponse(
        CatalogRagService().stream(
            db=db,
            question=request.question,
            dataset_id=request.dataset_id,
            tag_slug=request.tag_slug,
            limit=request.limit,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/datasets/{dataset_id}/ask", response_model=CatalogRagResponse)
async def ask_catalog_dataset_profile(
    dataset_id: str,
    request: CatalogRagRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await CatalogRagService().ask(
        db=db,
        question=request.question,
        dataset_id=dataset_id,
        tag_slug=request.tag_slug,
        limit=request.limit,
    )


@router.post("/datasets/{dataset_id}/ask/stream")
async def stream_catalog_dataset_profile(
    dataset_id: str,
    request: CatalogRagRequest,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    return StreamingResponse(
        CatalogRagService().stream(
            db=db,
            question=request.question,
            dataset_id=dataset_id,
            tag_slug=request.tag_slug,
            limit=request.limit,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/datasets/{dataset_id}/acquire", response_model=AccessGrantRead)
async def acquire_catalog_dataset(
    dataset_id: str,
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
    return await AccessService().acquire_dataset(
        db=db, dataset_id=dataset_id, user=current_user
    )
