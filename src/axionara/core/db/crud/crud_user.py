from sqlmodel import Session, select

from axionara.app.utils.security import get_password_hash
from axionara.core.db.models import UserAccount


def select_all_user(db: Session) -> list[UserAccount]:
    users = db.exec(select(UserAccount))
    return list(users.all())


def select_user_by_id(db: Session, user_id: str | None) -> UserAccount | None:
    if user_id:
        user_result = db.exec(
            select(UserAccount).where(
                UserAccount.id == user_id,
                UserAccount.is_active == True,  # noqa: E712
            )
        )
        return user_result.first()
    return None


def select_user_by_username(db: Session, username: str | None) -> UserAccount | None:
    if username:
        user_result = db.exec(
            select(UserAccount).where(
                UserAccount.username == username,
                UserAccount.is_active == True,  # noqa: E712
            )
        )
        return user_result.first()
    return None


def select_user_by_email(db: Session, email: str | None) -> UserAccount | None:
    if email:
        user_result = db.exec(
            select(UserAccount).where(
                UserAccount.email == email,
                UserAccount.is_active == True,  # noqa: E712
            )
        )
        return user_result.first()
    return None


def select_user_by_login_name(db: Session, login_name: str | None) -> UserAccount | None:
    if not login_name:
        return None
    user = select_user_by_username(db=db, username=login_name)
    if user is not None:
        return user
    return select_user_by_email(db=db, email=login_name)


def insert_user(db: Session, user: UserAccount) -> UserAccount:
    user.password = get_password_hash(user.password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# async def update_user(db: AsyncSession, user_id: str, update_attr: dict) -> User | None:
#     user = await db.get(User, ident=user_id)
#     if user:
#         user.email = update_attr.get("email", user.email)
#         user.password = (
#             get_password_hash(update_attr["password"])
#             if update_attr.get("passwd")
#             else user.password
#         )
#         user.full_name = update_attr.get("full_name", user.full_name)

#         db.add(user)
#         await db.commit()
#         await db.refresh(user)
#         return user
#     return None
