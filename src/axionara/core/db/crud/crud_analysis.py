from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.core.db.models import (
    AnalysisJob,
    DatasetAnalysis,
    DatasetAsset,
    DatasetProfile,
    DatasetReview,
    DatasetTag,
    Tag,
)


async def insert_analysis_job(db: AsyncSession, job: AnalysisJob) -> AnalysisJob:
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def update_analysis_job(db: AsyncSession, job: AnalysisJob) -> AnalysisJob:
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def select_analysis_job_by_id(db: AsyncSession, job_id: str) -> AnalysisJob | None:
    result = await db.exec(select(AnalysisJob).where(AnalysisJob.id == job_id))
    return result.first()


async def select_analysis_jobs(
    db: AsyncSession,
    dataset_id: str | None = None,
    job_status: str | None = None,
) -> list[AnalysisJob]:
    statement = select(AnalysisJob)
    if dataset_id is not None:
        statement = statement.where(AnalysisJob.dataset_id == dataset_id)
    if job_status is not None:
        statement = statement.where(AnalysisJob.job_status == job_status)
    result = await db.exec(statement.order_by(AnalysisJob.create_date.desc()))  # type: ignore
    return list(result.all())


async def insert_dataset_analysis(
    db: AsyncSession, analysis: DatasetAnalysis
) -> DatasetAnalysis:
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis


async def insert_dataset_review(db: AsyncSession, review: DatasetReview) -> DatasetReview:
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


async def update_dataset_review(db: AsyncSession, review: DatasetReview) -> DatasetReview:
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


async def select_dataset_review_by_id(
    db: AsyncSession, review_id: str
) -> DatasetReview | None:
    result = await db.exec(select(DatasetReview).where(DatasetReview.id == review_id))
    return result.first()


async def select_dataset_reviews(
    db: AsyncSession,
    dataset_id: str | None = None,
    review_status: str | None = None,
) -> list[DatasetReview]:
    statement = select(DatasetReview)
    if dataset_id is not None:
        statement = statement.where(DatasetReview.dataset_id == dataset_id)
    if review_status is not None:
        statement = statement.where(DatasetReview.review_status == review_status)
    result = await db.exec(statement.order_by(DatasetReview.create_date.desc()))  # type: ignore
    return list(result.all())


async def select_latest_dataset_review(
    db: AsyncSession, dataset_id: str
) -> DatasetReview | None:
    result = await db.exec(
        select(DatasetReview)
        .where(DatasetReview.dataset_id == dataset_id)
        .order_by(DatasetReview.create_date.desc())  # type: ignore
    )
    return result.first()


async def upsert_dataset_profile(
    db: AsyncSession, profile: DatasetProfile
) -> DatasetProfile:
    existing = await select_dataset_profile_by_dataset_id(
        db=db, dataset_id=profile.dataset_id
    )
    if existing is not None:
        profile.id = existing.id
        await db.merge(profile)
        await db.commit()
        refreshed = await db.get(DatasetProfile, profile.id)
        if refreshed is not None:
            return refreshed
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def select_dataset_profile_by_dataset_id(
    db: AsyncSession, dataset_id: str
) -> DatasetProfile | None:
    result = await db.exec(
        select(DatasetProfile).where(DatasetProfile.dataset_id == dataset_id)
    )
    return result.first()


async def select_latest_dataset_analysis(
    db: AsyncSession, dataset_id: str
) -> DatasetAnalysis | None:
    result = await db.exec(
        select(DatasetAnalysis)
        .where(DatasetAnalysis.dataset_id == dataset_id)
        .order_by(DatasetAnalysis.create_date.desc())  # type: ignore
    )
    return result.first()


async def update_dataset_asset(db: AsyncSession, dataset: DatasetAsset) -> DatasetAsset:
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    return dataset


async def select_tag_by_slug_category(
    db: AsyncSession, slug: str, category: str
) -> Tag | None:
    result = await db.exec(select(Tag).where(Tag.slug == slug, Tag.category == category))
    return result.first()


async def insert_tag(db: AsyncSession, tag: Tag) -> Tag:
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def insert_dataset_tag(db: AsyncSession, dataset_tag: DatasetTag) -> DatasetTag:
    db.add(dataset_tag)
    await db.commit()
    await db.refresh(dataset_tag)
    return dataset_tag


async def select_all_active_tags(db: AsyncSession) -> list[Tag]:
    result = await db.exec(
        select(Tag).where(Tag.is_active == True).order_by(Tag.category, Tag.name)  # noqa: E712
    )
    return list(result.all())


async def select_dataset_tags(db: AsyncSession, dataset_id: str) -> list[DatasetTag]:
    result = await db.exec(select(DatasetTag).where(DatasetTag.dataset_id == dataset_id))
    return list(result.all())
