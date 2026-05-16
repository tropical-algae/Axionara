from sqlmodel import Session

from axionara.app.services.dataset_qa_agent_service import DatasetQaAgentService
from axionara.core.db.models import UserAccount
from axionara.core.model.dataset import ContentRagResponse


class AuthorizedContentRagService:
    def __init__(self):
        self.agent_service = DatasetQaAgentService()

    async def ask(
        self,
        db: Session,
        dataset_id: str,
        question: str,
        user: UserAccount,
        limit: int = 5,
    ) -> ContentRagResponse:
        return await self.agent_service.ask_authorized_content(
            db=db,
            dataset_id=dataset_id,
            question=question,
            user=user,
            limit=limit,
        )
