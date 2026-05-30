from collections.abc import AsyncIterator

from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.services.dataset_qa_agent_service import DatasetQaAgentService
from axionara.core.model.dataset import CatalogRagResponse


class CatalogRagService:
    def __init__(self):
        self.agent_service = DatasetQaAgentService()

    async def ask(
        self,
        db: AsyncSession,
        question: str,
        dataset_id: str | None = None,
        tag_slug: str | None = None,
        limit: int = 3,
    ) -> CatalogRagResponse:
        return await self.agent_service.ask_public_profiles(
            db=db,
            question=question,
            dataset_id=dataset_id,
            tag_slug=tag_slug,
            limit=limit,
        )

    def stream(
        self,
        db: AsyncSession,
        question: str,
        dataset_id: str | None = None,
        tag_slug: str | None = None,
        limit: int = 3,
    ) -> AsyncIterator[bytes]:
        return self.agent_service.stream_public_profiles(
            db=db,
            question=question,
            dataset_id=dataset_id,
            tag_slug=tag_slug,
            limit=limit,
        )
