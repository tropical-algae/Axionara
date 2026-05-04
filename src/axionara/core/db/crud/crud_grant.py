from sqlmodel import Session, select

from axionara.core.db.models import AccessGrant


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
