from sqlmodel import Session, select

from axionara.core.db.models import (
    AnalysisJob,
    DatasetAnalysis,
    DatasetAsset,
    DatasetProfile,
    DatasetReview,
    DatasetTag,
    Tag,
)


def insert_analysis_job(db: Session, job: AnalysisJob) -> AnalysisJob:
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_analysis_job(db: Session, job: AnalysisJob) -> AnalysisJob:
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def insert_dataset_analysis(db: Session, analysis: DatasetAnalysis) -> DatasetAnalysis:
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def insert_dataset_review(db: Session, review: DatasetReview) -> DatasetReview:
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def update_dataset_review(db: Session, review: DatasetReview) -> DatasetReview:
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def select_latest_dataset_review(db: Session, dataset_id: str) -> DatasetReview | None:
    result = db.exec(
        select(DatasetReview)
        .where(DatasetReview.dataset_id == dataset_id)
        .order_by(DatasetReview.create_date.desc())
    )
    return result.first()


def upsert_dataset_profile(db: Session, profile: DatasetProfile) -> DatasetProfile:
    existing = select_dataset_profile_by_dataset_id(db=db, dataset_id=profile.dataset_id)
    if existing is not None:
        profile.id = existing.id
        db.merge(profile)
        db.commit()
        refreshed = db.get(DatasetProfile, profile.id)
        if refreshed is not None:
            return refreshed
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def select_dataset_profile_by_dataset_id(
    db: Session, dataset_id: str
) -> DatasetProfile | None:
    result = db.exec(
        select(DatasetProfile).where(DatasetProfile.dataset_id == dataset_id)
    )
    return result.first()


def select_latest_dataset_analysis(
    db: Session, dataset_id: str
) -> DatasetAnalysis | None:
    result = db.exec(
        select(DatasetAnalysis)
        .where(DatasetAnalysis.dataset_id == dataset_id)
        .order_by(DatasetAnalysis.create_date.desc())
    )
    return result.first()


def update_dataset_asset(db: Session, dataset: DatasetAsset) -> DatasetAsset:
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def select_tag_by_slug_category(db: Session, slug: str, category: str) -> Tag | None:
    result = db.exec(select(Tag).where(Tag.slug == slug, Tag.category == category))
    return result.first()


def insert_tag(db: Session, tag: Tag) -> Tag:
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def insert_dataset_tag(db: Session, dataset_tag: DatasetTag) -> DatasetTag:
    db.add(dataset_tag)
    db.commit()
    db.refresh(dataset_tag)
    return dataset_tag


def select_all_active_tags(db: Session) -> list[Tag]:
    result = db.exec(
        select(Tag).where(Tag.is_active == True).order_by(Tag.category, Tag.name)  # noqa: E712
    )
    return list(result.all())


def select_dataset_tags(db: Session, dataset_id: str) -> list[DatasetTag]:
    result = db.exec(select(DatasetTag).where(DatasetTag.dataset_id == dataset_id))
    return list(result.all())
