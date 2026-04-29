import inspect
from typing import Any, cast

from llama_index.core.memory import (
    BaseMemoryBlock,
    FactExtractionMemoryBlock,
    InsertMethod,
    Memory,
    StaticMemoryBlock,
    VectorMemoryBlock,
)
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI

import axionara.core.agent.tools as agent_tools
from axionara.common.config import settings
from axionara.common.logging import logger
from axionara.common.util import import_all_modules_from_package
from axionara.core.agent.base import ToolBase
from axionara.core.db.session import local_engine


class AgentStore:
    def __init__(
        self,
        api_key: str,
        api_base: str,
        default_model: str,
    ):
        self.llm = OpenAI(
            api_key=api_key,
            api_base=api_base,
            model=default_model,
            max_retries=3,
            timeout=20,
        )
        self.emb = None
        self.memories: dict[str, Memory] = {}
        self.tools: dict[str, type[ToolBase]] = {}
        self._register_tools()

    def _register_tools(self) -> None:
        # import all tool modules
        import_all_modules_from_package(agent_tools)

        tools: dict[str, type[ToolBase]] = {}
        unactivated_tools: list[str] = []
        # collect tools
        for tool in ToolBase.__subclasses__():
            if tool.__activate__ and not inspect.isabstract(tool):
                tools[tool.__tool_info__.name] = cast(type[ToolBase], tool)
            else:
                unactivated_tools.append(tool.__tool_info__.name)
        self.tools = tools
        logger.info(f"Loaded tools: {list(self.tools.keys())}")
        logger.info(f"Unloaded tools: {unactivated_tools}")

    def _gen_memory_blocks(self, static_content: str) -> list[BaseMemoryBlock]:
        return [
            StaticMemoryBlock(
                name="UserProfile",
                static_content=static_content,
                priority=0,
            ),
            FactExtractionMemoryBlock(
                name="ExtractedFacts",
                llm=self.llm,
                max_facts=200,
                priority=1,
            ),
        ]

    def _get_user_profile(self, user_id: str) -> str:
        _ = user_id
        return ""

    def get_tools(
        self, blocked_tools: list[str] | None = None, is_tool_base: bool = True
    ) -> list[Any]:
        _blocked_tools: list[str] = blocked_tools or []
        return [
            tool if is_tool_base else tool.get_tool()
            for n, tool in self.tools.items()
            if n not in _blocked_tools
        ]

    def get_tool_names(self, blocked_tools: list[str] | None = None) -> list[str]:
        tools = list(self.tools.keys())
        return list(set(tools) - set(blocked_tools)) if blocked_tools else tools

    def get_memory(self, user_id: str, session_id: str) -> Memory:
        return self.memories.setdefault(
            session_id,
            Memory.from_defaults(
                session_id=session_id,
                async_database_uri=settings.SQL_DATABASE_URI,
                table_name=settings.AGENT_MEMORY_SQL_TABLE,
                async_engine=local_engine,
                token_limit=1200,
                chat_history_token_ratio=0.7,
                token_flush_size=800,
                memory_blocks=self._gen_memory_blocks(
                    static_content=self._get_user_profile(user_id=user_id)
                ),
                insert_method=InsertMethod.USER,
            ),
        )


agent_store = AgentStore(
    api_key=settings.GPT_API_KEY,
    api_base=settings.GPT_BASE_URL,
    default_model=settings.GPT_DEFAULT_MODEL,
)
