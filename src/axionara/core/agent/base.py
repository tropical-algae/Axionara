from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from llama_index.core.memory import Memory
from llama_index.core.tools import FunctionTool

from axionara.core.model.tool import AgentToolInfo


class ToolBase(ABC):
    __tool_name__: str = ""
    __tool_description__: str = ""
    __tool_info__: AgentToolInfo = AgentToolInfo()
    __activate__: bool = True

    @staticmethod
    @abstractmethod
    async def a_tool_function(*args, **kwargs) -> Any:
        raise NotImplementedError

    @staticmethod
    async def a_tool_post_processing_function(agent_message: str) -> str:
        return agent_message

    @classmethod
    def get_tool(cls) -> Any:
        return FunctionTool.from_defaults(
            name=cls.__tool_name__,
            description=cls.__tool_description__,
            async_fn=cls.a_tool_function,
        )


class AgentBase(ABC):
    def __init__(
        self,
        api_key: str,
        api_base: str,
        default_model: str,
        system_prompt: str,
    ):
        self.api_key = api_key
        self.api_base = api_base
        self.default_model = default_model
        self.system_prompt = system_prompt

        super().__init__()

    @abstractmethod
    async def run(
        self,
        message: str,
        tools: list[type[ToolBase]],
        memory: Memory | None = None,
        **kwargs,  # type: ignore
    ) -> Any:
        raise NotImplementedError

    @abstractmethod
    def run_stream(
        self,
        message: str,
        tools: list[type[ToolBase]],
        memory: Memory | None = None,
        **kwargs,  # type: ignore
    ) -> AsyncIterator[Any]:
        raise NotImplementedError
