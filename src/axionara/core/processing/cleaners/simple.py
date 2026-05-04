from axionara.core.processing.types import CleaningResult, ParsedResult


class RuleBasedCleaner:
    def clean(self, parsed: ParsedResult) -> CleaningResult:
        if parsed.representation_type == "document":
            return CleaningResult(
                cleaning_status="skipped",
                cleaning_actions={
                    "status": "skipped",
                    "items": [
                        {
                            "action_code": "document_cleaning_skipped",
                            "stage": "cleaning",
                            "target": "dataset",
                            "status": "skipped",
                            "changed_count": 0,
                            "summary_public": "文档类文件未执行结构化数据清洗",
                        }
                    ],
                },
                issues={"total_count": 0, "items": []},
                skipped_steps={"items": ["data_cleaning"]},
            )

        preview_rows = (
            parsed.preview_data if isinstance(parsed.preview_data, list) else []
        )
        columns = parsed.schema_snapshot.get("columns", [])
        return CleaningResult(
            cleaning_status="completed",
            normalized_data={"columns": columns, "preview_rows": preview_rows[:10]},
            cleaning_actions={
                "status": "completed",
                "items": [
                    {
                        "action_code": "schema_inspection",
                        "stage": "cleaning",
                        "target": "dataset",
                        "status": "executed",
                        "changed_count": 0,
                        "summary_public": "完成字段结构检查，暂未修改原始数据",
                    }
                ],
            },
            issues={"total_count": 0, "items": []},
            skipped_steps={"items": []},
        )
