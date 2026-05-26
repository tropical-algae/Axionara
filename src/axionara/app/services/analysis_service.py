from datetime import datetime

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.services.storage_service import get_storage_service
from axionara.app.utils.constant import CONSTANT
from axionara.common.util import generate_random_token
from axionara.core.db.crud import (
    insert_analysis_job,
    insert_dataset_analysis,
    insert_dataset_tag,
    insert_tag,
    select_analysis_job_by_id,
    select_analysis_jobs,
    select_dataset_by_id,
    select_latest_dataset_analysis,
    select_tag_by_slug_category,
    update_analysis_job,
    update_dataset_asset,
    upsert_dataset_profile,
)
from axionara.core.db.models import (
    AnalysisJob,
    DatasetAnalysis,
    DatasetAsset,
    DatasetProfile,
    DatasetTag,
    Tag,
    UserAccount,
)
from axionara.core.model.dataset import DatasetAssetStatus
from axionara.core.processing.analyzers.simple import (
    ExportCapabilityEvaluator,
    StatisticsBuilder,
    SummaryTagGenerator,
)
from axionara.core.processing.cleaners.simple import RuleBasedCleaner
from axionara.core.processing.hooks.sensitivity import SensitivityService
from axionara.core.processing.parsers.simple import get_parser


class AnalysisOrchestrator:
    def __init__(self):
        self.storage = get_storage_service()
        self.cleaner = RuleBasedCleaner()
        self.sensitivity = SensitivityService()
        self.statistics = StatisticsBuilder()
        self.capabilities = ExportCapabilityEvaluator()
        self.summary_tags = SummaryTagGenerator()

    async def run_dataset_analysis(
        self,
        db: AsyncSession,
        dataset_id: str,
        triggered_by: UserAccount,
        use_llm: bool = False,
    ) -> AnalysisJob:
        dataset = await self._get_dataset(db=db, dataset_id=dataset_id)
        job = await insert_analysis_job(
            db=db,
            job=AnalysisJob(
                id=generate_random_token(prefix="JOB", length=24),
                dataset_id=dataset_id,
                triggered_by=triggered_by.id,
                job_status="running",
                current_stage="parse",
                started_at=datetime.now(),
            ),
        )

        try:
            dataset.status = DatasetAssetStatus.PROCESSING_REVIEW.value
            await update_dataset_asset(db=db, dataset=dataset)

            content = self.storage.get_bytes(
                bucket=dataset.raw_bucket or "",
                object_key=dataset.raw_object_key or "",
            )
            parsed = get_parser(dataset.source_format).parse(
                dataset=dataset, content=content
            )

            job.current_stage = "cleaning"
            await update_analysis_job(db=db, job=job)
            cleaned = self.cleaner.clean(parsed=parsed)

            job.current_stage = "sensitivity"
            await update_analysis_job(db=db, job=job)
            sensitivity_report = self.sensitivity.scan_sensitive_content(
                dataset=dataset, parsed=parsed
            )

            job.current_stage = "statistics"
            await update_analysis_job(db=db, job=job)
            statistics = self.statistics.build(
                dataset=dataset, parsed=parsed, cleaned=cleaned
            )

            job.current_stage = "capability"
            await update_analysis_job(db=db, job=job)
            export_capabilities = self.capabilities.evaluate(
                dataset=dataset, parsed=parsed, cleaned=cleaned
            )

            job.current_stage = "summary"
            await update_analysis_job(db=db, job=job)
            summary_result = await self.summary_tags.generate(
                dataset=dataset,
                statistics=statistics,
                cleaning_actions=cleaned.cleaning_actions,
                issues=cleaned.issues,
                export_capabilities=export_capabilities,
                use_llm=use_llm,
            )

            job.current_stage = "persist"
            await update_analysis_job(db=db, job=job)
            analysis = await insert_dataset_analysis(
                db=db,
                analysis=DatasetAnalysis(
                    id=generate_random_token(prefix="ANA", length=24),
                    dataset_id=dataset.id,
                    job_id=job.id,
                    analysis_status="succeeded",
                    representation_type=parsed.representation_type,
                    parser_status=parsed.parser_status,
                    cleaning_status=cleaned.cleaning_status,
                    sensitivity_status=sensitivity_report.get("status", "skipped"),
                    summary_status="completed",
                    tag_status="completed",
                    schema_snapshot=parsed.schema_snapshot,
                    statistics=statistics,
                    issues=cleaned.issues,
                    cleaning_actions=cleaned.cleaning_actions,
                    skipped_steps=cleaned.skipped_steps,
                    export_capabilities=export_capabilities,
                    sensitivity_report=sensitivity_report,
                    suggested_tags=summary_result.suggested_tags,
                    internal_summary=summary_result.public_summary,
                    llm_output_json=summary_result.llm_output_json,
                ),
            )
            await upsert_dataset_profile(
                db=db,
                profile=DatasetProfile(
                    id=generate_random_token(prefix="PRO", length=24),
                    dataset_id=dataset.id,
                    analysis_id=analysis.id,
                    public_summary=summary_result.public_summary,
                    processing_summary=summary_result.processing_summary,
                    cleaning_summary=summary_result.cleaning_summary,
                    risk_summary=summary_result.risk_summary,
                    public_statistics=statistics,
                    allowed_export_formats=export_capabilities.get("allowed_formats", []),
                    public_rag_text=summary_result.public_rag_text,
                    tag_summary=", ".join(
                        item["name"]
                        for item in summary_result.suggested_tags.get("items", [])
                    ),
                ),
            )
            await self._persist_tags(
                db=db,
                dataset=dataset,
                analysis=analysis,
                suggested_tags=summary_result.suggested_tags,
            )

            dataset.status = DatasetAssetStatus.REVIEWED.value
            dataset.representation_hint = parsed.representation_type
            await update_dataset_asset(db=db, dataset=dataset)
            job.job_status = "succeeded"
            job.current_stage = "done"
            job.finished_at = datetime.now()
            return await update_analysis_job(db=db, job=job)
        except Exception as err:
            job.job_status = "failed"
            job.error_message = str(err)
            job.finished_at = datetime.now()
            await update_analysis_job(db=db, job=job)
            raise

    async def get_latest_analysis(
        self, db: AsyncSession, dataset_id: str
    ) -> DatasetAnalysis:
        analysis = await select_latest_dataset_analysis(db=db, dataset_id=dataset_id)
        if analysis is None:
            raise HTTPException(**CONSTANT.RESP_ANALYSIS_NOT_EXISTS)
        return analysis

    async def list_analysis_jobs(
        self,
        db: AsyncSession,
        dataset_id: str | None = None,
        job_status: str | None = None,
    ) -> list[AnalysisJob]:
        return await select_analysis_jobs(
            db=db, dataset_id=dataset_id, job_status=job_status
        )

    async def get_analysis_job(self, db: AsyncSession, job_id: str) -> AnalysisJob:
        job = await select_analysis_job_by_id(db=db, job_id=job_id)
        if job is None:
            raise HTTPException(**CONSTANT.RESP_ANALYSIS_JOB_NOT_EXISTS)
        return job

    async def retry_analysis_job(
        self,
        db: AsyncSession,
        job_id: str,
        triggered_by: UserAccount,
        use_llm: bool = False,
    ) -> AnalysisJob:
        job = await self.get_analysis_job(db=db, job_id=job_id)
        if job.job_status != "failed":
            raise HTTPException(**CONSTANT.RESP_ANALYSIS_JOB_NOT_RETRYABLE)
        return await self.run_dataset_analysis(
            db=db,
            dataset_id=job.dataset_id,
            triggered_by=triggered_by,
            use_llm=use_llm,
        )

    async def _get_dataset(self, db: AsyncSession, dataset_id: str) -> DatasetAsset:
        dataset = await select_dataset_by_id(db=db, dataset_id=dataset_id)
        if dataset is None:
            raise HTTPException(**CONSTANT.RESP_DATASET_NOT_EXISTS)
        return dataset

    async def _persist_tags(
        self,
        db: AsyncSession,
        dataset: DatasetAsset,
        analysis: DatasetAnalysis,
        suggested_tags: dict,
    ) -> None:
        for item in suggested_tags.get("items", []):
            tag = await select_tag_by_slug_category(
                db=db, slug=item["slug"], category=item["category"]
            )
            if tag is None:
                tag = await insert_tag(
                    db=db,
                    tag=Tag(
                        id=generate_random_token(prefix="TAG", length=24),
                        name=item["name"],
                        slug=item["slug"],
                        category=item["category"],
                        source=item.get("source", "system"),
                    ),
                )
            await insert_dataset_tag(
                db=db,
                dataset_tag=DatasetTag(
                    id=generate_random_token(prefix="DTA", length=24),
                    dataset_id=dataset.id,
                    tag_id=tag.id,
                    analysis_id=analysis.id,
                    confidence=item.get("confidence"),
                    generated_by=item.get("source", "system"),
                    is_primary=item.get("category") == "data_type",
                ),
            )
