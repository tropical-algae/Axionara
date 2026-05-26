from axionara.app.services.dataset_qa_retrieval import DatasetProfileRetrievalService
from axionara.common.logging import logger
from axionara.core.agent.base import ToolBase
from axionara.core.agent.context import (
    GET_PUBLIC_DATASET_PROFILE_TOOL,
    get_dataset_qa_context,
    to_json_payload,
)
from axionara.core.model.tool import AgentToolInfo


class GetPublicDatasetProfileTool(ToolBase):
    __tool_name__ = "get_public_dataset_profile"
    __tool_display_name__ = ""
    __tool_description__ = (
        "获取指定已发布数据资产的公开详情，包括公开摘要、处理说明、公开统计、"
        "标签、来源机构、覆盖时间和导出能力。不会读取原始数据内容。"
    )
    __tool_info__ = AgentToolInfo(
        name=GET_PUBLIC_DATASET_PROFILE_TOOL,
        invocation_message="Loading public dataset profile...",
    )
    __activate__ = True

    @staticmethod
    async def a_tool_function(
        dataset_id: str | None = None,
        question: str | None = None,
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
        resolved_dataset_id = dataset_id or context.dataset_id
        if not resolved_dataset_id:
            return to_json_payload(
                {
                    "source_scope": "public_dataset_profile",
                    "raw_content_used": False,
                    "matches": [],
                    "error": "dataset_id is required",
                }
            )
        normalized_question = (question or context.question).strip()
        service = DatasetProfileRetrievalService()
        matches = service.search(
            db=context.db,
            question=normalized_question,
            dataset_id=resolved_dataset_id,
            tag_slug=context.tag_slug,
            limit=limit or context.limit,
        )
        context.catalog_matches = service.to_matches(matches)
        payload = service.to_tool_payload(matches)
        logger.info(
            "Tool Call: Get public dataset profile "
            f"dataset_id={resolved_dataset_id} matches={len(context.catalog_matches)}"
        )
        return to_json_payload(payload)
