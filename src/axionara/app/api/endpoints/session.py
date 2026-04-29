from fastapi import APIRouter, Depends, Security
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.api.deps import get_current_user, get_db, get_session_id
from axionara.app.services.session_service import (
    collect_session_memory,
    collect_sessions,
)
from axionara.core.db.models import UserAccount
from axionara.core.model.message import ChatSessionCompleteRequest, MemoryResponse
from axionara.core.model.user import ScopeType

router = APIRouter()


@router.get("/list")
async def get_session_list(
    db: AsyncSession = Depends(get_db),
    current_user: UserAccount = Security(get_current_user),
) -> list[str]:
    return await collect_sessions(db=db, user_id=current_user.id)


@router.post("/messages", response_model=MemoryResponse)
async def get_session_messages(
    session_request: ChatSessionCompleteRequest = Depends(
        get_session_id(scopes=[ScopeType.ADMIN, ScopeType.USER])
    ),
) -> MemoryResponse:
    return await collect_session_memory(
        user_id=session_request.user.id, session_id=session_request.session_id
    )
