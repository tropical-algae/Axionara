from fastapi import APIRouter, Depends, Security
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.core.agent.store import agent_store

router = APIRouter()


@router.get("/list")
async def get_session_list() -> list[str]:
    tools: list = agent_store.get_tool_names()
    return tools
