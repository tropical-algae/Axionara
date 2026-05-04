from sqlmodel import Session, select

from axionara.core.db.models import AccessGrant, ExportJob


def insert_access_grant(db: Session, grant: AccessGrant) -> AccessGrant:
    db.add(grant)
    db.commit()
    db.refresh(grant)
    return grant


def select_active_access_grant(
    db: Session, dataset_id: str, user_id: str
) -> AccessGrant | None:
    result = db.exec(
        select(AccessGrant).where(
            AccessGrant.dataset_id == dataset_id,
            AccessGrant.user_id == user_id,
            AccessGrant.grant_status == "granted",
        )
    )
    return result.first()


def select_access_grants_by_user(db: Session, user_id: str) -> list[AccessGrant]:
    result = db.exec(
        select(AccessGrant)
        .where(AccessGrant.user_id == user_id, AccessGrant.grant_status == "granted")
        .order_by(AccessGrant.granted_at.desc())
    )
    return list(result.all())


def insert_export_job(db: Session, job: ExportJob) -> ExportJob:
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_export_job(db: Session, job: ExportJob) -> ExportJob:
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def select_export_job_by_id(db: Session, job_id: str) -> ExportJob | None:
    result = db.exec(select(ExportJob).where(ExportJob.id == job_id))
    return result.first()


def select_export_jobs_by_user(db: Session, user_id: str) -> list[ExportJob]:
    result = db.exec(
        select(ExportJob)
        .where(ExportJob.user_id == user_id)
        .order_by(ExportJob.create_date.desc())
    )
    return list(result.all())


def select_export_jobs_by_user_dataset(
    db: Session, user_id: str, dataset_id: str
) -> list[ExportJob]:
    result = db.exec(
        select(ExportJob)
        .where(ExportJob.user_id == user_id, ExportJob.dataset_id == dataset_id)
        .order_by(ExportJob.create_date.desc())
    )
    return list(result.all())
