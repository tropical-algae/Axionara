import json

import json_repair

from axionara.common.config import settings
from axionara.core.agent.agent import MyAgent
from axionara.core.agent.factory import agent_factory
from axionara.core.db.models import DatasetAsset
from axionara.core.processing.types import CleaningResult, ParsedResult, SummaryTagResult
from axionara.core.prompt import load_prompt


class StatisticsBuilder:
    def build(
        self, dataset: DatasetAsset, parsed: ParsedResult, cleaned: CleaningResult
    ) -> dict:
        common = {
            "source_format": dataset.source_format,
            "representation_type": parsed.representation_type,
            "file_size_bytes": dataset.file_size_bytes,
            "content_type": dataset.content_type,
            "etag": dataset.etag,
        }
        if parsed.representation_type == "tabular":
            normalized = (
                cleaned.normalized_data
                if isinstance(cleaned.normalized_data, dict)
                else {}
            )
            columns = normalized.get("columns") or parsed.schema_snapshot.get(
                "columns", []
            )
            return {
                "common": common,
                "tabular": {
                    "record_count": normalized.get(
                        "record_count", self._extract_record_count(parsed)
                    ),
                    "column_count": len(columns),
                    "duplicate_row_count": normalized.get("duplicate_row_count", 0),
                    "duplicate_row_ratio": normalized.get("duplicate_row_ratio", 0),
                    "missing_value_count": normalized.get("missing_value_count", 0),
                    "missing_value_ratio": normalized.get("missing_value_ratio", 0),
                    "column_profiles": normalized.get("column_profiles", []),
                },
                "hierarchical": None,
                "document": None,
            }
        if parsed.representation_type == "hierarchical":
            return {
                "common": common,
                "tabular": None,
                "hierarchical": {"root_type": parsed.schema_snapshot.get("root_type")},
                "document": None,
            }
        text_chars = len(parsed.extracted_text or "")
        extraction = parsed.schema_snapshot.get("text_extraction", {})
        return {
            "common": common,
            "tabular": None,
            "hierarchical": None,
            "document": {
                "extractable_text_chars": text_chars,
                "extractable_text_ratio": 1.0 if text_chars else 0.0,
                "text_extraction_status": extraction.get(
                    "status", "completed" if text_chars else "skipped"
                ),
                "text_extraction_engine": extraction.get("engine"),
                "text_extraction_truncated": extraction.get("truncated", False),
            },
        }

    def _extract_record_count(self, parsed: ParsedResult) -> int:
        for note in parsed.parser_notes:
            if note.startswith("parsed_rows="):
                return int(note.split("=", 1)[1])
        return len(parsed.preview_data) if isinstance(parsed.preview_data, list) else 0

    def _normalize_column_name(self, name: str) -> str:
        return "_".join(name.strip().lower().split())


class ExportCapabilityEvaluator:
    def evaluate(
        self, dataset: DatasetAsset, parsed: ParsedResult, cleaned: CleaningResult
    ) -> dict:
        _ = dataset, cleaned
        items = [
            {
                "target_format": "raw",
                "supported": True,
                "confidence": 1.0,
                "reason": "原始文件始终可导出",
                "validation_checks": ["object_exists"],
            }
        ]
        if parsed.representation_type == "tabular":
            items.extend(
                [
                    {
                        "target_format": "csv",
                        "supported": True,
                        "confidence": 0.95,
                        "reason": "数据可稳定表示为二维表",
                        "validation_checks": ["tabular_representation_ready"],
                    },
                    {
                        "target_format": "json",
                        "supported": True,
                        "confidence": 0.95,
                        "reason": "字段结构明确，可序列化为对象列表",
                        "validation_checks": ["schema_serializable"],
                    },
                    {
                        "target_format": "sql",
                        "supported": True,
                        "confidence": 0.9,
                        "reason": "字段结构可用于生成 SQL 文件",
                        "validation_checks": ["schema_inferred", "ddl_buildable"],
                    },
                ]
            )
        elif parsed.representation_type == "hierarchical":
            items.append(
                {
                    "target_format": "json",
                    "supported": True,
                    "confidence": 0.9,
                    "reason": "层级结构可保留为 JSON 文件",
                    "validation_checks": ["json_serializable"],
                }
            )
        return {
            "items": items,
            "allowed_formats": [
                item["target_format"] for item in items if item["supported"]
            ],
        }


class SummaryTagGenerator:
    async def generate(
        self,
        dataset: DatasetAsset,
        statistics: dict,
        cleaning_actions: dict,
        issues: dict,
        export_capabilities: dict,
        use_llm: bool = False,
    ) -> SummaryTagResult:
        fallback = self._generate_rule_based(
            dataset=dataset,
            statistics=statistics,
            cleaning_actions=cleaning_actions,
            issues=issues,
            export_capabilities=export_capabilities,
        )
        if not use_llm or not settings.GPT_API_KEY:
            return fallback

        try:
            return await self._generate_with_llm(
                dataset=dataset,
                statistics=statistics,
                cleaning_actions=cleaning_actions,
                issues=issues,
                export_capabilities=export_capabilities,
                fallback=fallback,
            )
        except Exception as err:
            fallback.llm_output_json = {
                "status": "fallback",
                "reason": "llm_generation_failed",
                "error": str(err),
            }
            return fallback

    def _generate_rule_based(
        self,
        dataset: DatasetAsset,
        statistics: dict,
        cleaning_actions: dict,
        issues: dict,
        export_capabilities: dict,
    ) -> SummaryTagResult:
        representation_type = statistics.get("common", {}).get(
            "representation_type", "unknown"
        )
        allowed_formats = export_capabilities.get("allowed_formats", ["raw"])
        public_summary = f"{dataset.title} 是一个 {dataset.source_format} 类型数据资产，系统识别为 {representation_type} 数据。"
        processing_summary = "系统已完成格式识别、结构分析、脱敏钩子检查和导出能力评估。"
        action_items = cleaning_actions.get("items", [])
        cleaning_summary = (
            "；".join(item.get("summary_public", "") for item in action_items)
            or "未执行数据清洗。"
        )
        risk_summary = (
            "暂未发现公开展示层面的风险。"
            if issues.get("total_count", 0) == 0
            else "存在需管理员关注的数据质量问题。"
        )
        suggested_tags = {
            "items": [
                {
                    "name": dataset.source_format,
                    "slug": dataset.source_format,
                    "category": "format",
                    "source": "system",
                    "confidence": 1.0,
                },
                {
                    "name": representation_type,
                    "slug": representation_type,
                    "category": "data_type",
                    "source": "system",
                    "confidence": 1.0,
                },
            ]
        }
        public_rag_text = "\n".join(
            [
                public_summary,
                processing_summary,
                cleaning_summary,
                self._document_extraction_summary(statistics),
                f"支持导出格式：{', '.join(allowed_formats)}",
            ]
        )
        return SummaryTagResult(
            public_summary=public_summary,
            processing_summary=processing_summary,
            cleaning_summary=cleaning_summary,
            risk_summary=risk_summary,
            public_rag_text=public_rag_text,
            suggested_tags=suggested_tags,
            llm_output_json=None,
        )

    def _document_extraction_summary(self, statistics: dict) -> str:
        document = statistics.get("document")
        if not isinstance(document, dict):
            return ""
        status = document.get("text_extraction_status", "skipped")
        chars = document.get("extractable_text_chars", 0)
        if status == "completed":
            return f"文档文本提取状态：已完成，可提取字符数 {chars}。"
        if status == "failed":
            return "文档文本提取状态：失败，公开概况不包含原文内容。"
        return "文档文本提取状态：未提取到可用文本。"

    async def _generate_with_llm(
        self,
        dataset: DatasetAsset,
        statistics: dict,
        cleaning_actions: dict,
        issues: dict,
        export_capabilities: dict,
        fallback: SummaryTagResult,
    ) -> SummaryTagResult:
        agent: MyAgent = agent_factory.get_agent(
            agent=MyAgent,
            model=settings.GPT_DEFAULT_MODEL,
        )
        response = await agent.run(
            message=self._build_llm_prompt(
                dataset=dataset,
                statistics=statistics,
                cleaning_actions=cleaning_actions,
                issues=issues,
                export_capabilities=export_capabilities,
            ),
            tools=[],
        )
        payload = json_repair.loads(response.content)
        if not isinstance(payload, dict):
            return fallback

        return SummaryTagResult(
            public_summary=payload.get("public_summary") or fallback.public_summary,
            processing_summary=payload.get("processing_summary")
            or fallback.processing_summary,
            cleaning_summary=payload.get("cleaning_summary") or fallback.cleaning_summary,
            risk_summary=payload.get("risk_summary") or fallback.risk_summary,
            public_rag_text=payload.get("public_rag_text") or fallback.public_rag_text,
            suggested_tags=self._merge_suggested_tags(
                fallback=fallback.suggested_tags,
                llm_tags=payload.get("suggested_tags"),
            ),
            llm_output_json={"status": "completed", "payload": payload},
        )

    def _build_llm_prompt(
        self,
        dataset: DatasetAsset,
        statistics: dict,
        cleaning_actions: dict,
        issues: dict,
        export_capabilities: dict,
    ) -> str:
        template = load_prompt(settings.AGENT_DATASET_SUMMARY_PROMPT_PATH)
        return template.format(
            dataset_title=dataset.title,
            dataset_description=dataset.description or "",
            source_format=dataset.source_format,
            statistics=json.dumps(statistics, ensure_ascii=False, default=str),
            cleaning_actions=json.dumps(
                cleaning_actions, ensure_ascii=False, default=str
            ),
            issues=json.dumps(issues, ensure_ascii=False, default=str),
            export_capabilities=json.dumps(
                export_capabilities, ensure_ascii=False, default=str
            ),
        )

    def _merge_suggested_tags(self, fallback: dict, llm_tags: object) -> dict:
        fallback_items = fallback.get("items", [])
        llm_items = llm_tags.get("items", []) if isinstance(llm_tags, dict) else []
        merged = []
        seen = set()
        for item in [*fallback_items, *llm_items]:
            if not isinstance(item, dict):
                continue
            key = (item.get("slug"), item.get("category"))
            if key in seen or not key[0] or not key[1]:
                continue
            seen.add(key)
            merged.append(item)
        return {"items": merged}
