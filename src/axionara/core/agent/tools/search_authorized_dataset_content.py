from axionara.app.services.dataset_qa_retrieval import DatasetContentRetrievalService
from axionara.common.logging import logger
from axionara.core.agent.base import ToolBase
from axionara.core.agent.context import (
    SEARCH_AUTHORIZED_DATASET_CONTENT_TOOL,
    get_dataset_qa_context,
    to_json_payload,
)
from axionara.core.model.tool import AgentToolInfo


class SearchAuthorizedDatasetContentTool(ToolBase):
    __tool_name__ = "search_authorized_dataset_content"
    __tool_display_name__ = ""
    __tool_description__ = (
        "在当前用户已授权访问的指定数据资产原始内容中检索相关片段。"
        "适用于我的数据详情页内容问答。"
    )
    __tool_info__ = AgentToolInfo(
        name=SEARCH_AUTHORIZED_DATASET_CONTENT_TOOL,
        invocation_message="Searching authorized dataset content...",
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
                    "source_scope": "authorized_dataset_content",
                    "raw_content_used": True,
                    "matches": [],
                    "error": "dataset QA request context is required",
                }
            )
        resolved_dataset_id = dataset_id or context.dataset_id
        if not resolved_dataset_id or context.user is None:
            return to_json_payload(
                {
                    "source_scope": "authorized_dataset_content",
                    "raw_content_used": True,
                    "matches": [],
                    "error": "dataset_id and user are required",
                }
            )
        normalized_question = (question or context.question).strip()
        service = DatasetContentRetrievalService()
        matches = service.search(
            db=context.db,
            dataset_id=resolved_dataset_id,
            question=normalized_question,
            user=context.user,
            limit=limit or context.limit,
        )
        context.content_matches = service.to_matches(matches)
        payload = service.to_tool_payload(matches)
        logger.info(
            "Tool Call: Search authorized dataset content "
            f"dataset_id={resolved_dataset_id} matches={len(context.content_matches)}"
        )
        return to_json_payload(payload)
