from typing import TypeVar, cast

from fastapi import HTTPException

from axionara.app.utils.constant import CONSTANT
from axionara.common.config import settings
from axionara.common.logging import logger
from axionara.core.agent.base import AgentBase
from axionara.core.prompt import load_agent_system_prompt

T = TypeVar("T", bound=AgentBase)


class AgentFactory:
    def __init__(self):
        self.agents: dict[str, AgentBase] = {}

    def get_supported_models(self) -> list[str]:
        return list(
            dict.fromkeys([settings.GPT_DEFAULT_MODEL, *settings.AGENT_OPTIONAL_MODELS])
        )

    def get_agent(
        self,
        agent: type[T],
        model: str,
        system_prompt: str | None = None,
        cache_key: str | None = None,
    ) -> T:
        if model not in self.get_supported_models():
            logger.error(f"The model {model} is not supported.")
            raise HTTPException(**CONSTANT.RESP_INVALID_MODEL)
        resolved_cache_key = cache_key or "default"
        agent_key = f"{agent.__module__}.{agent.__name__}:{model}:{resolved_cache_key}"
        if agent_key not in self.agents:
            self.agents[agent_key] = agent(
                api_key=settings.GPT_API_KEY,
                api_base=settings.GPT_BASE_URL,
                default_model=model,
                system_prompt=system_prompt or load_agent_system_prompt(),
            )

        return cast(T, self.agents[agent_key])


agent_factory = AgentFactory()
