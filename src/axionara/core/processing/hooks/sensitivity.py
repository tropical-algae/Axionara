from axionara.core.db.models import DatasetAsset
from axionara.core.processing.types import ParsedResult


class SensitivityService:
    def scan_sensitive_content(self, dataset: DatasetAsset, parsed: ParsedResult) -> dict:
        _ = dataset, parsed
        return {
            "detected": False,
            "rules_triggered": [],
            "actions": [],
            "status": "skipped",
        }

    def apply_desensitization(self, dataset: DatasetAsset, report: dict) -> dict:
        _ = dataset, report
        return {"status": "skipped", "actions": []}
