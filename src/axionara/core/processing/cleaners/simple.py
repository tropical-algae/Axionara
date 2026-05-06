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

        rows = self._tabular_rows(parsed=parsed)
        columns = parsed.schema_snapshot.get("columns", [])
        column_names = [column.get("name") for column in columns if column.get("name")]
        normalized_rows = [
            {
                self._normalize_column_name(str(column)): self._normalize_value(
                    row.get(column)
                )
                for column in column_names
            }
            for row in rows
            if isinstance(row, dict)
        ]
        duplicate_count = self._duplicate_count(normalized_rows)
        missing_count = self._missing_value_count(normalized_rows)
        cell_count = len(normalized_rows) * len(column_names)
        column_profiles = [
            self._profile_column(
                source_name=str(column),
                normalized_name=self._normalize_column_name(str(column)),
                rows=rows,
            )
            for column in column_names
        ]
        return CleaningResult(
            cleaning_status="completed",
            normalized_data={
                "columns": [
                    {
                        "name": profile["name"],
                        "normalized_name": profile["normalized_name"],
                        "inferred_type": profile["inferred_type"],
                    }
                    for profile in column_profiles
                ],
                "preview_rows": normalized_rows[:10],
                "record_count": len(normalized_rows),
                "duplicate_row_count": duplicate_count,
                "duplicate_row_ratio": self._ratio(duplicate_count, len(normalized_rows)),
                "missing_value_count": missing_count,
                "missing_value_ratio": self._ratio(missing_count, cell_count),
                "column_profiles": column_profiles,
            },
            cleaning_actions={
                "status": "completed",
                "items": [
                    {
                        "action_code": "schema_inspection",
                        "stage": "cleaning",
                        "target": "dataset",
                        "status": "executed",
                        "changed_count": 0,
                        "summary_public": "完成字段结构检查和字段名规范化建议",
                    },
                    {
                        "action_code": "quality_profile",
                        "stage": "cleaning",
                        "target": "dataset",
                        "status": "executed",
                        "changed_count": duplicate_count + missing_count,
                        "summary_public": "完成重复行、缺失值和字段类型统计",
                    },
                ],
            },
            issues=self._build_issues(
                duplicate_count=duplicate_count,
                missing_count=missing_count,
            ),
            skipped_steps={"items": []},
        )

    def _tabular_rows(self, parsed: ParsedResult) -> list[dict]:
        if isinstance(parsed.data, list):
            return [row for row in parsed.data if isinstance(row, dict)]
        if isinstance(parsed.preview_data, list):
            return [row for row in parsed.preview_data if isinstance(row, dict)]
        return []

    def _normalize_column_name(self, name: str) -> str:
        normalized = "_".join(name.strip().lower().split())
        return normalized or "value"

    def _normalize_value(self, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return None if value == "" else value
        return value

    def _duplicate_count(self, rows: list[dict]) -> int:
        seen = set()
        duplicates = 0
        for row in rows:
            marker = tuple(sorted(row.items()))
            if marker in seen:
                duplicates += 1
            else:
                seen.add(marker)
        return duplicates

    def _missing_value_count(self, rows: list[dict]) -> int:
        return sum(
            1
            for row in rows
            for value in row.values()
            if value is None or (isinstance(value, str) and value.strip() == "")
        )

    def _profile_column(
        self, source_name: str, normalized_name: str, rows: list[dict]
    ) -> dict:
        values = [self._normalize_value(row.get(source_name)) for row in rows]
        non_null_values = [value for value in values if value is not None]
        null_count = len(values) - len(non_null_values)
        return {
            "name": source_name,
            "normalized_name": normalized_name,
            "inferred_type": self._infer_type(non_null_values),
            "nullable": null_count > 0,
            "null_count": null_count,
            "null_ratio": self._ratio(null_count, len(values)),
            "unique_count": len({str(value) for value in non_null_values}),
        }

    def _infer_type(self, values: list[object]) -> str:
        if not values:
            return "unknown"
        if all(self._is_int(value) for value in values):
            return "integer"
        if all(self._is_float(value) for value in values):
            return "number"
        if all(str(value).lower() in {"true", "false", "0", "1"} for value in values):
            return "boolean"
        return "string"

    def _is_int(self, value: object) -> bool:
        try:
            return str(int(str(value))) == str(value)
        except (TypeError, ValueError):
            return False

    def _is_float(self, value: object) -> bool:
        try:
            float(str(value))
            return True
        except (TypeError, ValueError):
            return False

    def _build_issues(self, duplicate_count: int, missing_count: int) -> dict:
        items = []
        if duplicate_count:
            items.append(
                {
                    "issue_code": "duplicate_rows_detected",
                    "severity": "warning",
                    "count": duplicate_count,
                    "summary_public": "发现重复行，未展示具体行内容",
                }
            )
        if missing_count:
            items.append(
                {
                    "issue_code": "missing_values_detected",
                    "severity": "warning",
                    "count": missing_count,
                    "summary_public": "发现缺失值，未展示具体字段值",
                }
            )
        return {"total_count": len(items), "items": items}

    def _ratio(self, numerator: int, denominator: int) -> float:
        return round(numerator / denominator, 4) if denominator else 0
