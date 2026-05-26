from datetime import datetime

from axionara.common.logging import logger
from axionara.core.agent.base import ToolBase
from axionara.core.model.tool import AgentToolInfo


class LocaltimeTool(ToolBase):
    __tool_name__ = "check_time"
    __tool_display_name__ = ""
    __tool_description__ = "获取当前时间"
    __tool_info__ = AgentToolInfo(
        name="Local Time", invocation_message="Checking current date..."
    )
    __activate__ = True

    @staticmethod
    async def a_tool_function() -> str:
        localtime = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {datetime.now().strftime('%A')}"
        logger.info(f"Tool Call: Check local time {localtime}")
        return localtime
