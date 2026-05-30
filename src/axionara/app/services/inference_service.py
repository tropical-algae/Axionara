import json
from collections.abc import AsyncIterator

from fastapi import HTTPException
from llama_index.core.memory import Memory

from axionara.app.utils.constant import CONSTANT
from axionara.common.logging import logger
from axionara.common.util import async_db_wrapper
from axionara.core.agent.agent import MyAgent
from axionara.core.agent.context import (
    DATASET_QA_TOOL_INFO_NAMES,
    DatasetQaToolContext,
    dataset_qa_tool_context,
)
from axionara.core.agent.factory import agent_factory
from axionara.core.agent.store import agent_store
from axionara.core.db.crud.session_crud import delete_session
from axionara.core.model.message import (
    AgentResponse,
    AgentResponseStream,
    ChatCompleteRequest,
)
from axionara.core.prompt import load_prompt


async def agent_stream_response(
    chat_request: ChatCompleteRequest,
) -> AsyncIterator[bytes]:
    try:
        memory: Memory | None = None
        if chat_request.use_memory:
            if not chat_request.session_id:
                logger.error("Session ID is required but was not provided.")
                raise HTTPException(**CONSTANT.RESP_USER_SESSION_NULL)
            memory = agent_store.get_memory(
                user_id=chat_request.user.id,
                session_id=chat_request.session_id,
            )

        tools: list = agent_store.get_tools(blocked_tools=chat_request.blocked_tools)
        agent: MyAgent = agent_factory.get_agent(agent=MyAgent, model=chat_request.model)
        logger.info(
            f"Agent run (stream) {'(new session)' if chat_request.is_new_session else ' '}{'without' if memory is None else 'with'} Memory, {len(tools)} Tools"
        )

        async for resp in agent.run_stream(
            message=chat_request.message, memory=memory, tools=tools
        ):
            yield (
                json.dumps(resp.model_dump(), ensure_ascii=False).encode("utf-8") + b"\n"
            )
    except Exception:
        if (
            chat_request.is_new_session
            and chat_request.use_memory
            and chat_request.session_id
        ):
            logger.error(
                f"New session {chat_request.session_id} failed to inference, rollback sql"
            )
            await async_db_wrapper(delete_session, session_id=chat_request.session_id)
            return


async def agent_response(
    chat_request: ChatCompleteRequest,
) -> AgentResponse:
    try:
        memory: Memory | None = None
        if chat_request.use_memory:
            if not chat_request.session_id:
                logger.error("Session ID is required but was not provided.")
                raise HTTPException(**CONSTANT.RESP_USER_SESSION_NULL)
            memory = agent_store.get_memory(
                user_id=chat_request.user.id,
                session_id=chat_request.session_id,
            )

        tools: list = agent_store.get_tools(blocked_tools=chat_request.blocked_tools)
        agent: MyAgent = agent_factory.get_agent(agent=MyAgent, model=chat_request.model)
        logger.info(
            f"Agent run {'(new session)' if chat_request.is_new_session else ' '}{'without' if memory is None else 'with'} Memory, {len(tools)} Tools"
        )
        return await agent.run(message=chat_request.message, memory=memory, tools=tools)
    except Exception:
        if (
            chat_request.is_new_session
            and chat_request.use_memory
            and chat_request.session_id
        ):
            logger.error(
                f"New session {chat_request.session_id} failed to inference, rollback sql"
            )
            await async_db_wrapper(delete_session, session_id=chat_request.session_id)
        raise


def _dataset_qa_agent_setup(model: str, system_prompt_path: str) -> tuple[list, MyAgent]:
    blocked_tools = [
        tool_name
        for tool_name in agent_store.get_tool_names()
        if tool_name not in DATASET_QA_TOOL_INFO_NAMES
    ]
    tools: list = agent_store.get_tools(blocked_tools=blocked_tools)
    agent: MyAgent = agent_factory.get_agent(
        agent=MyAgent,
        model=model,
        system_prompt=load_prompt(system_prompt_path),
        cache_key="dataset_qa",
    )
    return tools, agent


async def dataset_qa_agent_response(
    message: str,
    context: DatasetQaToolContext,
    model: str,
    system_prompt_path: str,
) -> AgentResponse:
    tools, agent = _dataset_qa_agent_setup(
        model=model, system_prompt_path=system_prompt_path
    )
    logger.info(f"Dataset QA agent run without Memory, {len(tools)} Tools")
    with dataset_qa_tool_context(context):
        return await agent.run(message=message, memory=None, tools=tools)


async def dataset_qa_agent_stream_response(
    message: str,
    context: DatasetQaToolContext,
    model: str,
    system_prompt_path: str,
) -> AsyncIterator[AgentResponseStream]:
    tools, agent = _dataset_qa_agent_setup(
        model=model, system_prompt_path=system_prompt_path
    )
    logger.info(f"Dataset QA agent stream run without Memory, {len(tools)} Tools")
    with dataset_qa_tool_context(context):
        async for response in agent.run_stream(message=message, memory=None, tools=tools):
            yield response
