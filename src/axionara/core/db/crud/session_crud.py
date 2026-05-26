from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.core.db.models import ChatSession


async def insert_session(db: AsyncSession, session_id: str, user_id: str) -> ChatSession:
    chat_session = ChatSession(
        id=session_id,
        user_id=user_id,
        is_active=True,
    )

    db.add(chat_session)
    await db.commit()
    await db.refresh(chat_session)
    return chat_session


async def select_all_session_by_user(db: AsyncSession, user_id: str) -> list[ChatSession]:
    result = await db.exec(
        select(ChatSession).where(ChatSession.user_id == user_id, ChatSession.is_active)
    )
    return list(result.all())


async def select_session_by_id_and_user(
    db: AsyncSession, id: str, user_id: str
) -> ChatSession | None:
    result = await db.exec(
        select(ChatSession).where(
            ChatSession.id == id, ChatSession.user_id == user_id, ChatSession.is_active
        )
    )
    return result.first()


async def delete_session(db: AsyncSession, session_id: str) -> ChatSession | None:
    session = await db.get(ChatSession, ident=session_id)
    if session:
        session.is_active = False
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session
    return None
