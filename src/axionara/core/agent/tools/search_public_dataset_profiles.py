from axionara.app.services.dataset_qa_retrieval import DatasetProfileRetrievalService
from axionara.common.logging import logger
from axionara.core.agent.base import ToolBase
from axionara.core.agent.context import (
    SEARCH_PUBLIC_DATASET_PROFILES_TOOL,
    get_dataset_qa_context,
    to_json_payload,
)
from axionara.core.model.tool import AgentToolInfo


class SearchPublicDatasetProfilesTool(ToolBase):
    __tool_name__ = "search_public_dataset_profiles"
    __tool_display_name__ = ""
    __tool_description__ = (
        "检索数据市场中已发布数据资产的公开概况、标签、公开统计和导出能力。"
        "适用于跨数据资产的问题，不会读取原始数据内容。"
    )
    __tool_info__ = AgentToolInfo(
        name=SEARCH_PUBLIC_DATASET_PROFILES_TOOL,
        invocation_message="Searching public dataset profiles...",
    )
    __activate__ = True

    @staticmethod
    async def a_tool_function(
        question: str | None = None,
        tag_slug: str | None = None,
        limit: int | None = None,
    ) -> str:
        context = get_dataset_qa_context()
        if context is None:
            return to_json_payload(
                {
                    "source_scope": "public_dataset_profile",
                    "raw_content_used": False,
                    "matches": [],
                    "error": "dataset QA request context is required",
                }
            )
        normalized_question = (question or context.question).strip()
        service = DatasetProfileRetrievalService()
        matches = await service.search(
            db=context.db,
            question=normalized_question,
            dataset_id=(
                context.dataset_id
                if context.request_scope == "public_dataset_profile"
                else None
            ),
            tag_slug=tag_slug or context.tag_slug,
            limit=limit or context.limit,
        )
        context.catalog_matches = service.to_matches(matches)
        payload = service.to_tool_payload(matches)
        logger.info(
            "Tool Call: Search public dataset profiles "
            f"matches={len(context.catalog_matches)}"
        )
        return to_json_payload(payload)
