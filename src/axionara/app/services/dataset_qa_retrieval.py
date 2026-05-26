import json
import re
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException
from llama_index.core.schema import Document
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.services.catalog_service import CatalogService
from axionara.app.services.storage_service import get_storage_service
from axionara.app.utils.constant import CONSTANT
from axionara.core.db.crud import select_active_access_grant, select_dataset_by_id
from axionara.core.db.models import DatasetAsset, DatasetProfile, Tag, UserAccount
from axionara.core.model.dataset import (
    CatalogRagMatch,
    ContentRagMatch,
    DatasetAssetStatus,
)
from axionara.core.processing.parsers.simple import get_parser
from axionara.core.processing.types import ParsedResult


@dataclass(frozen=True)
class PublicDatasetDocument:
    dataset: DatasetAsset
    profile: DatasetProfile
    tags: list[Tag]
    document: Document


@dataclass(frozen=True)
class ContentChunk:
    dataset: DatasetAsset
    chunk_id: str
    document: Document


class DatasetProfileRetrievalService:
    def __init__(self):
        self.catalog = CatalogService()

    async def search(
        self,
        db: AsyncSession,
        question: str,
        dataset_id: str | None = None,
        tag_slug: str | None = None,
        limit: int = 3,
    ) -> list[tuple[PublicDatasetDocument, float]]:
        documents = await self._load_public_documents(
            db=db, dataset_id=dataset_id, tag_slug=tag_slug
        )
        return self._retrieve(
            documents=documents,
            question=question,
            limit=max(1, min(limit, 10)),
        )

    def to_matches(
        self, matches: list[tuple[PublicDatasetDocument, float]]
    ) -> list[CatalogRagMatch]:
        return [
            CatalogRagMatch(
                dataset_id=item.dataset.id,
                title=item.dataset.title,
                score=score,
                tags=[tag.slug for tag in item.tags],
                snippet=self._snippet(item.document.text),
            )
            for item, score in matches
        ]

    def to_tool_payload(
        self, matches: list[tuple[PublicDatasetDocument, float]]
    ) -> dict[str, Any]:
        return {
            "source_scope": "public_dataset_profile",
            "raw_content_used": False,
            "matches": [
                {
                    "dataset_id": item.dataset.id,
                    "title": item.dataset.title,
                    "score": score,
                    "tags": [tag.slug for tag in item.tags],
                    "snippet": self._snippet(item.document.text),
                    "material": item.document.text,
                }
                for item, score in matches
            ],
        }

    async def _load_public_documents(
        self, db: AsyncSession, dataset_id: str | None, tag_slug: str | None
    ) -> list[PublicDatasetDocument]:
        if dataset_id:
            dataset, profile, tags = await self.catalog.get_published_dataset(
                db=db, dataset_id=dataset_id
            )
            if tag_slug and not any(tag.slug == tag_slug for tag in tags):
                return []
            rows = [(dataset, profile, tags)]
        else:
            rows = await self.catalog.list_published_datasets(db=db, tag_slug=tag_slug)
        return [
            PublicDatasetDocument(
                dataset=dataset,
                profile=profile,
                tags=tags,
                document=self._to_llama_document(
                    dataset=dataset, profile=profile, tags=tags
                ),
            )
            for dataset, profile, tags in rows
        ]

    def _to_llama_document(
        self, dataset: DatasetAsset, profile: DatasetProfile, tags: list[Tag]
    ) -> Document:
        tag_text = ", ".join(tag.slug for tag in tags)
        text = "\n".join(
            [
                f"数据名称：{dataset.title}",
                f"数据描述：{dataset.description or ''}",
                f"数据类别：{dataset.category or ''}",
                f"来源机构：{dataset.source_organization or ''}",
                f"覆盖时间：{dataset.coverage_start or ''} 至 {dataset.coverage_end or ''}",
                f"更新频率：{dataset.update_frequency or ''}",
                f"数据格式：{dataset.source_format}",
                f"数据标签：{tag_text}",
                f"公开摘要：{profile.public_summary}",
                f"处理说明：{profile.processing_summary}",
                f"清洗说明：{profile.cleaning_summary}",
                f"风险说明：{profile.risk_summary or ''}",
                f"支持导出格式：{', '.join(profile.allowed_export_formats)}",
                f"公开统计：{profile.public_statistics}",
                f"公开问答材料：{profile.public_rag_text}",
            ]
        )
        return Document(
            text=text,
            metadata={
                "dataset_id": dataset.id,
                "title": dataset.title,
                "source_scope": "public_dataset_profile",
            },
        )

    def _retrieve(
        self,
        documents: list[PublicDatasetDocument],
        question: str,
        limit: int,
    ) -> list[tuple[PublicDatasetDocument, float]]:
        query_terms = self._terms(question)
        scored = []
        for item in documents:
            text = item.document.text.lower()
            score = sum(1 for term in query_terms if term in text)
            if item.dataset.title.lower() in question.lower():
                score += 3
            if any(tag.slug.lower() in question.lower() for tag in item.tags):
                score += 2
            if not query_terms:
                score = 1
            if score > 0:
                scored.append((item, float(score)))
        if not scored:
            scored = [(item, 0.1) for item in documents]
        scored.sort(key=lambda row: row[1], reverse=True)
        return scored[:limit]

    def _terms(self, text: str) -> list[str]:
        ascii_terms = re.findall(r"[A-Za-z0-9_]+", text.lower())
        cjk_terms = re.findall(r"[\u4e00-\u9fff]{2,}", text)
        return ascii_terms + cjk_terms

    def _snippet(self, text: str) -> str:
        compact = " ".join(text.split())
        return compact[:240]


class DatasetContentRetrievalService:
    def __init__(self):
        self.storage = get_storage_service()

    async def search(
        self,
        db: AsyncSession,
        dataset_id: str,
        question: str,
        user: UserAccount,
        limit: int = 5,
    ) -> list[tuple[ContentChunk, float]]:
        dataset = await self._get_authorized_dataset(
            db=db,
            dataset_id=dataset_id,
            user=user,
        )
        parsed = self._parse_dataset(dataset=dataset)
        chunks = self._build_chunks(dataset=dataset, parsed=parsed)
        return self._retrieve(
            chunks=chunks,
            question=question,
            limit=max(1, min(limit, 10)),
        )

    def to_matches(
        self, matches: list[tuple[ContentChunk, float]]
    ) -> list[ContentRagMatch]:
        return [
            ContentRagMatch(
                dataset_id=chunk.dataset.id,
                chunk_id=chunk.chunk_id,
                score=score,
                snippet=self._snippet(chunk.document.text),
            )
            for chunk, score in matches
        ]

    def to_tool_payload(
        self, matches: list[tuple[ContentChunk, float]]
    ) -> dict[str, Any]:
        return {
            "source_scope": "authorized_dataset_content",
            "raw_content_used": True,
            "matches": [
                {
                    "dataset_id": chunk.dataset.id,
                    "chunk_id": chunk.chunk_id,
                    "score": score,
                    "snippet": self._snippet(chunk.document.text),
                    "material": chunk.document.text,
                }
                for chunk, score in matches
            ],
        }

    async def _get_authorized_dataset(
        self, db: AsyncSession, dataset_id: str, user: UserAccount
    ) -> DatasetAsset:
        dataset = await select_dataset_by_id(db=db, dataset_id=dataset_id)
        if dataset is None or dataset.status != DatasetAssetStatus.PUBLISHED.value:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)
        grant = await select_active_access_grant(
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
            dataset=dataset,
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

    def _terms(self, text: str) -> list[str]:
        ascii_terms = re.findall(r"[A-Za-z0-9_]+", text.lower())
        cjk_terms = re.findall(r"[\u4e00-\u9fff]{2,}", text)
        return ascii_terms + cjk_terms

    def _snippet(self, text: str) -> str:
        compact = " ".join(text.split())
        return compact[:300]
