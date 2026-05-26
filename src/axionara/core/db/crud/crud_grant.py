from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.core.db.models import AccessGrant, ExportJob


async def insert_access_grant(db: AsyncSession, grant: AccessGrant) -> AccessGrant:
    db.add(grant)
    await db.commit()
    await db.refresh(grant)
    return grant


async def select_active_access_grant(
    db: AsyncSession, dataset_id: str, user_id: str
) -> AccessGrant | None:
    result = await db.exec(
        select(AccessGrant).where(
            AccessGrant.dataset_id == dataset_id,
            AccessGrant.user_id == user_id,
            AccessGrant.grant_status == "granted",
        )
    )
    return result.first()


async def select_access_grants_by_user(
    db: AsyncSession, user_id: str
) -> list[AccessGrant]:
    result = await db.exec(
        select(AccessGrant)
        .where(AccessGrant.user_id == user_id, AccessGrant.grant_status == "granted")
        .order_by(AccessGrant.granted_at.desc())  # type: ignore
    )
    return list(result.all())


async def insert_export_job(db: AsyncSession, job: ExportJob) -> ExportJob:
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def update_export_job(db: AsyncSession, job: ExportJob) -> ExportJob:
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def select_export_job_by_id(db: AsyncSession, job_id: str) -> ExportJob | None:
    result = await db.exec(select(ExportJob).where(ExportJob.id == job_id))
    return result.first()


async def select_export_jobs_by_user(db: AsyncSession, user_id: str) -> list[ExportJob]:
    result = await db.exec(
        select(ExportJob)
        .where(ExportJob.user_id == user_id)
        .order_by(ExportJob.create_date.desc())  # type: ignore
    )
    return list(result.all())


async def select_export_jobs_by_user_dataset(
    db: AsyncSession, user_id: str, dataset_id: str
) -> list[ExportJob]:
    result = await db.exec(
        select(ExportJob)
        .where(ExportJob.user_id == user_id, ExportJob.dataset_id == dataset_id)
        .order_by(ExportJob.create_date.desc())  # type: ignore
    )
    return list(result.all())
