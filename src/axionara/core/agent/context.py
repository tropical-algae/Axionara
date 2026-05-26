import json
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any

from sqlmodel import Session

from axionara.core.db.models import UserAccount
from axionara.core.model.dataset import CatalogRagMatch, ContentRagMatch

SEARCH_PUBLIC_DATASET_PROFILES_TOOL = "Search Public Dataset Profiles"
GET_PUBLIC_DATASET_PROFILE_TOOL = "Get Public Dataset Profile"
SEARCH_AUTHORIZED_DATASET_CONTENT_TOOL = "Search Authorized Dataset Content"

DATASET_QA_TOOL_INFO_NAMES = [
    SEARCH_PUBLIC_DATASET_PROFILES_TOOL,
    GET_PUBLIC_DATASET_PROFILE_TOOL,
    SEARCH_AUTHORIZED_DATASET_CONTENT_TOOL,
]


@dataclass
class DatasetQaToolContext:
    request_scope: str
    db: Session
    question: str
    limit: int
    dataset_id: str | None = None
    tag_slug: str | None = None
    user: UserAccount | None = None
    catalog_matches: list[CatalogRagMatch] = field(default_factory=list)
    content_matches: list[ContentRagMatch] = field(default_factory=list)


_dataset_qa_context: ContextVar[DatasetQaToolContext | None] = ContextVar(
    "dataset_qa_context", default=None
)


@contextmanager
def dataset_qa_tool_context(context: DatasetQaToolContext):
    token = _dataset_qa_context.set(context)
    try:
        yield context
    finally:
        _dataset_qa_context.reset(token)


def require_dataset_qa_context() -> DatasetQaToolContext:
    context = _dataset_qa_context.get()
    if context is None:
        raise RuntimeError("Dataset QA tools require a request context.")
    return context


def get_dataset_qa_context() -> DatasetQaToolContext | None:
    return _dataset_qa_context.get()


def to_json_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str)
