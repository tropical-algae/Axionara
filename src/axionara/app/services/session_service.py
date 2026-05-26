from fastapi import HTTPException
from llama_index.core.memory import Memory
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.utils.constant import CONSTANT
from axionara.common.logging import logger
from axionara.common.util import generate_random_token
from axionara.core.agent.store import agent_store
from axionara.core.db.crud.session_crud import insert_session, select_all_session_by_user
from axionara.core.db.models import UserAccount
from axionara.core.model.message import MemoryResponse


async def create_session(db: AsyncSession, user: UserAccount) -> str:
    session_id: str = generate_random_token(prefix="SESS", length=24)
    # 插入session id和user的映射
    await insert_session(db=db, session_id=session_id, user_id=user.id)
    logger.info(f"Create new session {session_id} for user {user.id}")
    return session_id


async def collect_sessions(db: AsyncSession, user_id: str) -> list[str]:
    results = await select_all_session_by_user(db=db, user_id=user_id)
    logger.info(f"Collect {len(results)} sessions for user {user_id}")
    return [r.id for r in results]


async def collect_session_memory(user_id: str, session_id: str | None) -> MemoryResponse:
    if session_id is None:
        logger.error("Provided an empty session when check memory")
        raise HTTPException(**CONSTANT.RESP_USER_SESSION_NULL)

    memory: Memory = agent_store.get_memory(
        user_id=user_id,
        session_id=session_id,
    )
    messages = await memory.aget_all()
    return MemoryResponse(session_id=session_id, messages=messages)
