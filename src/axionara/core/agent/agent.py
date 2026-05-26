import inspect
from collections.abc import AsyncIterator
from typing import TypeVar, cast

from llama_index.core.agent.workflow import (
    AgentOutput,
    AgentStream,
    FunctionAgent,
    ReActAgent,
)
from llama_index.core.memory import Memory
from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI

from axionara.common.config import settings
from axionara.common.decorator import exception_handling
from axionara.common.logging import logger
from axionara.core.agent.base import AgentBase, ToolBase
from axionara.core.model.message import AgentResponse, AgentResponseStream

T = TypeVar("T", bound=ToolBase)


class MyAgent(AgentBase):
    def __init__(
        self,
        api_key: str,
        api_base: str,
        default_model: str,
        max_retries: int = 3,
        timeout: int = 30,
        system_prompt: str = "You are a helpful assistant",
        **kwargs,
    ):
        self.client = OpenAI(
            api_key=api_key,
            api_base=api_base,
            model=default_model,
            max_retries=max_retries,
            timeout=timeout,
            **kwargs,
        )
        self.context: dict[str, Context] = {}
        self.system_prompt = system_prompt

    @exception_handling
    async def run(
        self,
        message: str,
        tools: list[type[ToolBase]],
        memory: Memory | None = None,
        **kwargs,
    ) -> AgentResponse:
        fn_tools = [t.get_tool() for t in tools]
        tools_map = {t.__tool_name__: t for t in tools}

        session_id: str | None = memory.session_id if memory else None
        agent = FunctionAgent(
            system_prompt=self.system_prompt,
            tools=fn_tools,
            llm=self.client,
        )
        response: AgentOutput = await agent.run(user_msg=message, memory=memory, **kwargs)
        # 封装结果
        result = AgentResponse.from_llm(
            session_id=session_id, output=response, tools_map=tools_map
        )
        await result.tool_post_process()
        return result

    async def run_stream(
        self,
        message: str,
        tools: list[type[ToolBase]],
        memory: Memory | None = None,
        **kwargs,
    ) -> AsyncIterator[AgentResponseStream]:
        steps = 0
        try:
            fn_tools = [t.get_tool() for t in tools]
            tools_map = {t.__tool_name__: t for t in tools}
            session_id: str | None = memory.session_id if memory else None
            agent = FunctionAgent(
                system_prompt=self.system_prompt,
                tools=fn_tools,
                llm=self.client,
            )
            handler = agent.run(user_msg=message, memory=memory, **kwargs)
            async for event in handler.stream_events():
                if isinstance(event, AgentStream):
                    steps += 1
                    yield AgentResponseStream.from_llm(
                        session_id=session_id, output=event, tools_map=tools_map
                    )
        finally:
            if steps == 0:
                error_msg = "Agent failed to perform streaming inference."
                logger.error(error_msg)
                raise RuntimeError(error_msg)
