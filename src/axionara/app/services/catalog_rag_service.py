import re
from dataclasses import dataclass

from fastapi import HTTPException
from llama_index.core.schema import Document
from sqlmodel import Session

from axionara.app.services.catalog_service import CatalogService
from axionara.app.utils.constant import CONSTANT
from axionara.core.db.models import DatasetAsset, DatasetProfile, Tag
from axionara.core.model.dataset import (
    CatalogRagMatch,
    CatalogRagResponse,
)


@dataclass(frozen=True)
class PublicDatasetDocument:
    dataset: DatasetAsset
    profile: DatasetProfile
    tags: list[Tag]
    document: Document


class CatalogRagService:
    def __init__(self):
        self.catalog = CatalogService()

    def ask(
        self,
        db: Session,
        question: str,
        dataset_id: str | None = None,
        tag_slug: str | None = None,
        limit: int = 3,
    ) -> CatalogRagResponse:
        normalized_question = question.strip()
        if not normalized_question:
            raise HTTPException(status_code=400, detail="问题不能为空")

        documents = self._load_public_documents(
            db=db, dataset_id=dataset_id, tag_slug=tag_slug
        )
        matches = self._retrieve(
            documents=documents,
            question=normalized_question,
            limit=max(1, min(limit, 10)),
        )
        response_matches = [
            CatalogRagMatch(
                dataset_id=item.dataset.id,
                title=item.dataset.title,
                score=score,
                tags=[tag.slug for tag in item.tags],
                snippet=self._snippet(item.document.text),
            )
            for item, score in matches
        ]
        return CatalogRagResponse(
            question=normalized_question,
            answer=self._answer(question=normalized_question, matches=matches),
            matches=response_matches,
        )

    def _load_public_documents(
        self, db: Session, dataset_id: str | None, tag_slug: str | None
    ) -> list[PublicDatasetDocument]:
        if dataset_id:
            dataset, profile, tags = self.catalog.get_published_dataset(
                db=db, dataset_id=dataset_id
            )
            if tag_slug and not any(tag.slug == tag_slug for tag in tags):
                return []
            rows = [(dataset, profile, tags)]
        else:
            rows = self.catalog.list_published_datasets(db=db, tag_slug=tag_slug)
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

    def _answer(
        self,
        question: str,
        matches: list[tuple[PublicDatasetDocument, float]],
    ) -> str:
        if not matches:
            return "没有找到匹配的已发布数据资产。当前回答仅基于公开数据概况，不读取原始数据内容。"

        lines = [
            "以下回答仅基于已发布数据资产的公开概况、统计信息和标签，不读取原始数据内容。"
        ]
        for item, _ in matches:
            profile = item.profile
            parts = [
                f"{item.dataset.title}：{profile.public_summary}",
                profile.processing_summary,
                profile.cleaning_summary,
                f"支持导出格式：{', '.join(profile.allowed_export_formats)}。",
            ]
            if self._asks_statistics(question):
                parts.append(f"公开统计：{profile.public_statistics}")
            if profile.tag_summary:
                parts.append(f"标签：{profile.tag_summary}。")
            lines.append(" ".join(part for part in parts if part))
        return "\n".join(lines)

    def _terms(self, text: str) -> list[str]:
        ascii_terms = re.findall(r"[A-Za-z0-9_]+", text.lower())
        cjk_terms = re.findall(r"[\u4e00-\u9fff]{2,}", text)
        return ascii_terms + cjk_terms

    def _asks_statistics(self, question: str) -> bool:
        return any(
            keyword in question for keyword in ["统计", "数量", "大小", "字段", "记录"]
        )

    def _snippet(self, text: str) -> str:
        compact = " ".join(text.split())
        return compact[:240]
