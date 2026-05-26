import json_repair
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.services.inference_service import dataset_qa_agent_response
from axionara.common.config import settings
from axionara.common.logging import logger
from axionara.core.agent.context import (
    DatasetQaToolContext,
)
from axionara.core.db.models import UserAccount
from axionara.core.model.dataset import (
    CatalogRagResponse,
    ContentRagResponse,
)
from axionara.core.prompt import load_prompt


class DatasetQaAgentService:
    async def ask_public_profiles(
        self,
        db: AsyncSession,
        question: str,
        dataset_id: str | None = None,
        tag_slug: str | None = None,
        limit: int = 3,
    ) -> CatalogRagResponse:
        normalized_question = self._normalize_question(question)
        request_scope = (
            "public_dataset_profile" if dataset_id else "public_catalog_profiles"
        )
        context = DatasetQaToolContext(
            request_scope=request_scope,
            db=db,
            question=normalized_question,
            dataset_id=dataset_id,
            tag_slug=tag_slug,
            limit=max(1, min(limit, 10)),
        )
        answer = await self._run_agent(context=context)
        if not context.catalog_matches:
            logger.warning("Dataset QA agent did not call a public profile tool.")
        return CatalogRagResponse(
            question=normalized_question,
            answer=answer,
            matches=context.catalog_matches,
        )

    async def ask_authorized_content(
        self,
        db: AsyncSession,
        dataset_id: str,
        question: str,
        user: UserAccount,
        limit: int = 5,
    ) -> ContentRagResponse:
        normalized_question = self._normalize_question(question)
        context = DatasetQaToolContext(
            request_scope="authorized_dataset_content",
            db=db,
            question=normalized_question,
            dataset_id=dataset_id,
            user=user,
            limit=max(1, min(limit, 10)),
        )
        answer = await self._run_agent(context=context)
        if not context.content_matches:
            logger.warning("Dataset QA agent did not call an authorized content tool.")
        return ContentRagResponse(
            question=normalized_question,
            answer=answer,
            matches=context.content_matches,
        )

    async def _run_agent(self, context: DatasetQaToolContext) -> str:
        response = await dataset_qa_agent_response(
            message=self._build_message(context=context),
            context=context,
            model=settings.GPT_DEFAULT_MODEL,
            system_prompt_path=settings.AGENT_DATA_QA_PROMPT_PATH,
        )
        return self._extract_answer(response.content)

    def _build_message(self, context: DatasetQaToolContext) -> str:
        template = load_prompt(settings.AGENT_DATA_QA_REQUEST_PROMPT_PATH)
        return template.format(
            request_scope=context.request_scope,
            dataset_id=context.dataset_id or "not specified",
            tag_slug=context.tag_slug or "not specified",
            result_limit=context.limit,
            user_question=context.question,
        )

    def _normalize_question(self, question: str) -> str:
        normalized_question = question.strip()
        if not normalized_question:
            raise HTTPException(status_code=400, detail="问题不能为空")
        return normalized_question

    def _extract_answer(self, content: str) -> str:
        stripped = content.strip()
        if not stripped:
            return "没有生成可用回答。"
        try:
            parsed = json_repair.loads(stripped)
        except Exception:
            return stripped
        if isinstance(parsed, dict) and isinstance(parsed.get("answer"), str):
            return parsed["answer"].strip() or stripped
        return stripped
