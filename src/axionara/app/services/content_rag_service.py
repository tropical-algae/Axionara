import json
import re
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException
from llama_index.core.schema import Document
from sqlmodel import Session

from axionara.app.services.storage_service import get_storage_service
from axionara.app.utils.constant import CONSTANT
from axionara.core.db.crud import select_active_access_grant, select_dataset_by_id
from axionara.core.db.models import DatasetAsset, UserAccount
from axionara.core.model.dataset import (
    ContentRagMatch,
    ContentRagResponse,
    DatasetAssetStatus,
)
from axionara.core.processing.parsers.simple import get_parser
from axionara.core.processing.types import ParsedResult


@dataclass(frozen=True)
class ContentChunk:
    chunk_id: str
    document: Document


class AuthorizedContentRagService:
    def __init__(self):
        self.storage = get_storage_service()

    def ask(
        self,
        db: Session,
        dataset_id: str,
        question: str,
        user: UserAccount,
        limit: int = 5,
    ) -> ContentRagResponse:
        normalized_question = question.strip()
        if not normalized_question:
            raise HTTPException(status_code=400, detail="问题不能为空")

        dataset = self._get_authorized_dataset(
            db=db,
            dataset_id=dataset_id,
            user=user,
        )
        parsed = self._parse_dataset(dataset=dataset)
        chunks = self._build_chunks(dataset=dataset, parsed=parsed)
        matches = self._retrieve(
            chunks=chunks,
            question=normalized_question,
            limit=max(1, min(limit, 10)),
        )
        return ContentRagResponse(
            question=normalized_question,
            answer=self._answer(question=normalized_question, matches=matches),
            matches=[
                ContentRagMatch(
                    dataset_id=dataset.id,
                    chunk_id=chunk.chunk_id,
                    score=score,
                    snippet=self._snippet(chunk.document.text),
                )
                for chunk, score in matches
            ],
        )

    def _get_authorized_dataset(
        self, db: Session, dataset_id: str, user: UserAccount
    ) -> DatasetAsset:
        dataset = select_dataset_by_id(db=db, dataset_id=dataset_id)
        if dataset is None or dataset.status != DatasetAssetStatus.PUBLISHED.value:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)
        grant = select_active_access_grant(
            db=db,
            dataset_id=dataset_id,
            user_id=user.id,
        )
        if grant is None:
            raise HTTPException(**CONSTANT.RESP_ACCESS_GRANT_NOT_EXISTS)
        return dataset

    def _parse_dataset(self, dataset: DatasetAsset) -> ParsedResult:
        content = self.storage.get_bytes(
            bucket=dataset.raw_bucket or "",
            object_key=dataset.raw_object_key or "",
        )
        return get_parser(dataset.source_format).parse(dataset=dataset, content=content)

    def _build_chunks(
        self, dataset: DatasetAsset, parsed: ParsedResult
    ) -> list[ContentChunk]:
        if parsed.representation_type == "tabular":
            rows = parsed.data if isinstance(parsed.data, list) else []
            return [
                self._chunk(
                    dataset=dataset,
                    chunk_id=f"row-{index + 1}",
                    text=self._row_text(index=index, row=row),
                )
                for index, row in enumerate(rows)
                if isinstance(row, dict)
            ]
        if parsed.representation_type == "hierarchical":
            return [
                self._chunk(
                    dataset=dataset,
                    chunk_id="json-root",
                    text=json.dumps(parsed.data, ensure_ascii=False, default=str),
                )
            ]
        text = parsed.extracted_text or ""
        return [
            self._chunk(dataset=dataset, chunk_id=f"text-{index + 1}", text=chunk)
            for index, chunk in enumerate(self._split_text(text))
        ]

    def _chunk(self, dataset: DatasetAsset, chunk_id: str, text: str) -> ContentChunk:
        return ContentChunk(
            chunk_id=chunk_id,
            document=Document(
                text=text,
                metadata={
                    "dataset_id": dataset.id,
                    "source_scope": "authorized_dataset_content",
                },
            ),
        )

    def _row_text(self, index: int, row: dict[str, Any]) -> str:
        values = ", ".join(f"{key}={value}" for key, value in row.items())
        return f"第 {index + 1} 行：{values}"

    def _split_text(self, text: str, chunk_size: int = 800) -> list[str]:
        compact = text.strip()
        if not compact:
            return []
        return [
            compact[index : index + chunk_size]
            for index in range(0, len(compact), chunk_size)
        ]

    def _retrieve(
        self,
        chunks: list[ContentChunk],
        question: str,
        limit: int,
    ) -> list[tuple[ContentChunk, float]]:
        query_terms = self._terms(question)
        scored = []
        for chunk in chunks:
            text = chunk.document.text.lower()
            score = sum(1 for term in query_terms if term in text)
            if not query_terms:
                score = 1
            if score > 0:
                scored.append((chunk, float(score)))
        if not scored:
            scored = [(chunk, 0.1) for chunk in chunks[:limit]]
        scored.sort(key=lambda row: row[1], reverse=True)
        return scored[:limit]

    def _answer(
        self,
        question: str,
        matches: list[tuple[ContentChunk, float]],
    ) -> str:
        _ = question
        if not matches:
            return "该数据资产未提取到可用于内容问答的文本或结构化内容。"
        lines = ["以下回答基于你已获取的数据资产原始内容生成。"]
        for chunk, _ in matches:
            lines.append(self._snippet(chunk.document.text))
        return "\n".join(lines)

    def _terms(self, text: str) -> list[str]:
        ascii_terms = re.findall(r"[A-Za-z0-9_]+", text.lower())
        cjk_terms = re.findall(r"[\u4e00-\u9fff]{2,}", text)
        return ascii_terms + cjk_terms

    def _snippet(self, text: str) -> str:
        compact = " ".join(text.split())
        return compact[:300]
