import asyncio

import pytest
from fastapi import BackgroundTasks, UploadFile
from sqlmodel import Session

from axionara.app.api.endpoints.admin_dataset import (
    analyze_dataset,
    approve_dataset,
    latest_dataset_analysis,
    pending_datasets,
    publish_dataset,
)
from axionara.app.api.endpoints.catalog import (
    acquire_catalog_dataset,
    ask_catalog_dataset_profile,
    ask_catalog_dataset_profiles,
    catalog_dataset_detail,
    list_catalog_datasets,
    list_catalog_tags,
)
from axionara.app.api.endpoints.me import (
    download_my_export,
    my_datasets,
    my_export_job_detail,
    my_export_jobs,
    request_dataset_export,
)
from axionara.app.api.endpoints.provider_dataset import (
    my_uploaded_datasets,
    upload_dataset,
    uploaded_dataset_detail,
)
from axionara.app.services.export_service import ExportService
from axionara.common.config import settings
from axionara.core.db.crud import select_user_by_id, select_user_by_username
from axionara.core.db.models import DatasetAsset
from axionara.core.model.dataset import (
    CatalogRagRequest,
    ExportFormat,
    ExportRequest,
    ReviewRequest,
)
from axionara.core.processing.analyzers.simple import (
    StatisticsBuilder,
    SummaryTagGenerator,
)
from axionara.core.processing.cleaners.simple import RuleBasedCleaner
from axionara.core.processing.types import ParsedResult, SummaryTagResult
from tests.conftest import DataStore


@pytest.mark.run(order=7)
def test_provider_dataset_upload(
    db_session: Session, data_store: DataStore, csv_upload: UploadFile
):
    user = select_user_by_id(db=db_session, user_id=data_store.provider_user_id)
    if user is None:
        user = select_user_by_username(db=db_session, username="provider_user")
    assert user is not None

    response = asyncio.run(
        upload_dataset(
            title="Population Dataset",
            description="Demo csv upload",
            file=csv_upload,
            current_user=user,
            db=db_session,
        )
    )

    assert response.source_format == "csv"
    assert response.status == "uploaded"
    data_store.uploaded_dataset_id = response.id


@pytest.mark.run(order=8)
def test_provider_dataset_list(db_session: Session, data_store: DataStore):
    user = select_user_by_id(db=db_session, user_id=data_store.provider_user_id)
    if user is None:
        user = select_user_by_username(db=db_session, username="provider_user")
    assert user is not None

    response = asyncio.run(my_uploaded_datasets(current_user=user, db=db_session))
    assert len(response) == 1
    assert response[0].id == data_store.uploaded_dataset_id


@pytest.mark.run(order=9)
def test_provider_dataset_detail(db_session: Session, data_store: DataStore):
    user = select_user_by_id(db=db_session, user_id=data_store.provider_user_id)
    if user is None:
        user = select_user_by_username(db=db_session, username="provider_user")
    assert user is not None

    response = asyncio.run(
        uploaded_dataset_detail(
            dataset_id=data_store.uploaded_dataset_id,
            current_user=user,
            db=db_session,
        )
    )
    assert response.title == "Population Dataset"


@pytest.mark.run(order=10)
def test_admin_analyze_csv_dataset(db_session: Session, data_store: DataStore):
    admin = select_user_by_id(db=db_session, user_id=data_store.admin_user_id)
    assert admin is not None

    job = asyncio.run(
        analyze_dataset(
            dataset_id=data_store.uploaded_dataset_id,
            current_user=admin,
            db=db_session,
        )
    )
    analysis = asyncio.run(
        latest_dataset_analysis(
            dataset_id=data_store.uploaded_dataset_id,
            current_user=admin,
            db=db_session,
        )
    )

    assert job.job_status == "succeeded"
    assert analysis.representation_type == "tabular"
    assert analysis.cleaning_status == "completed"
    assert "sql" in analysis.export_capabilities["allowed_formats"]


@pytest.mark.run(order=11)
def test_admin_approve_and_publish_dataset(db_session: Session, data_store: DataStore):
    admin = select_user_by_id(db=db_session, user_id=data_store.admin_user_id)
    assert admin is not None

    pending = asyncio.run(pending_datasets(current_user=admin, db=db_session))
    assert any(dataset.id == data_store.uploaded_dataset_id for dataset in pending)

    approved = asyncio.run(
        approve_dataset(
            dataset_id=data_store.uploaded_dataset_id,
            request=ReviewRequest(comment="analysis looks good"),
            current_user=admin,
            db=db_session,
        )
    )
    approved_status = approved.review_status
    published = asyncio.run(
        publish_dataset(
            dataset_id=data_store.uploaded_dataset_id,
            request=ReviewRequest(comment="publish for catalog"),
            current_user=admin,
            db=db_session,
        )
    )

    assert approved_status == "approved"
    assert published.review_status == "published"


@pytest.mark.run(order=12)
def test_catalog_lists_published_dataset(db_session: Session, data_store: DataStore):
    rows = asyncio.run(list_catalog_datasets(db=db_session))
    detail = asyncio.run(
        catalog_dataset_detail(dataset_id=data_store.uploaded_dataset_id, db=db_session)
    )
    tags = asyncio.run(list_catalog_tags(db=db_session))

    assert any(row.dataset.id == data_store.uploaded_dataset_id for row in rows)
    assert detail.dataset.id == data_store.uploaded_dataset_id
    assert "csv" in detail.tags
    assert any(tag.slug == "csv" for tag in tags)


@pytest.mark.run(order=13)
def test_catalog_tag_filter(db_session: Session, data_store: DataStore):
    rows = asyncio.run(list_catalog_datasets(tag_slug="csv", db=db_session))
    assert any(row.dataset.id == data_store.uploaded_dataset_id for row in rows)


@pytest.mark.run(order=14)
def test_catalog_public_profile_rag_answer(db_session: Session, data_store: DataStore):
    response = asyncio.run(
        ask_catalog_dataset_profiles(
            request=CatalogRagRequest(question="这个人口数据支持什么导出格式？"),
            db=db_session,
        )
    )
    scoped = asyncio.run(
        ask_catalog_dataset_profile(
            dataset_id=data_store.uploaded_dataset_id,
            request=CatalogRagRequest(question="这个数据有哪些统计信息？"),
            db=db_session,
        )
    )

    assert response.raw_content_used is False
    assert response.source_scope == "public_dataset_profile"
    assert any(
        match.dataset_id == data_store.uploaded_dataset_id for match in response.matches
    )
    assert "支持导出格式" in response.answer
    assert "sql" in response.answer
    assert scoped.matches[0].dataset_id == data_store.uploaded_dataset_id
    assert "公开统计" in scoped.answer


@pytest.mark.run(order=15)
def test_consumer_acquires_dataset(db_session: Session, data_store: DataStore):
    consumer = select_user_by_id(db=db_session, user_id=data_store.consumer_user_id)
    assert consumer is not None

    grant = asyncio.run(
        acquire_catalog_dataset(
            dataset_id=data_store.uploaded_dataset_id,
            current_user=consumer,
            db=db_session,
        )
    )
    duplicate = asyncio.run(
        acquire_catalog_dataset(
            dataset_id=data_store.uploaded_dataset_id,
            current_user=consumer,
            db=db_session,
        )
    )

    assert grant.grant_status == "granted"
    assert grant.grant_method == "demo_click"
    assert duplicate.id == grant.id


@pytest.mark.run(order=16)
def test_my_datasets_lists_acquired_dataset(db_session: Session, data_store: DataStore):
    consumer = select_user_by_id(db=db_session, user_id=data_store.consumer_user_id)
    assert consumer is not None

    rows = asyncio.run(my_datasets(current_user=consumer, db=db_session))

    assert len(rows) == 1
    assert rows[0].dataset.id == data_store.uploaded_dataset_id
    assert rows[0].grant.grant_status == "granted"
    assert "csv" in rows[0].tags


@pytest.mark.run(order=17)
def test_consumer_exports_acquired_dataset_as_sql(
    db_session: Session, data_store: DataStore
):
    consumer = select_user_by_id(db=db_session, user_id=data_store.consumer_user_id)
    assert consumer is not None

    job = asyncio.run(
        request_dataset_export(
            dataset_id=data_store.uploaded_dataset_id,
            request=ExportRequest(target_format=ExportFormat.SQL),
            background_tasks=BackgroundTasks(),
            current_user=consumer,
            db=db_session,
        )
    )
    processed = ExportService().process_export_job(db=db_session, job_id=job.id)
    detail = asyncio.run(
        my_export_job_detail(job_id=job.id, current_user=consumer, db=db_session)
    )
    jobs = asyncio.run(
        my_export_jobs(
            dataset_id=data_store.uploaded_dataset_id,
            current_user=consumer,
            db=db_session,
        )
    )
    download = asyncio.run(
        download_my_export(job_id=job.id, current_user=consumer, db=db_session)
    )

    assert processed.job_status == "succeeded"
    assert detail.id == job.id
    assert any(row.id == job.id for row in jobs)
    assert processed.output_filename == "population.sql"
    assert b"CREATE TABLE `population`" in download.body
    assert b"INSERT INTO `population`" in download.body


@pytest.mark.run(order=18)
def test_pdf_analysis_skips_cleaning(
    db_session: Session, data_store: DataStore, pdf_upload: UploadFile
):
    provider = select_user_by_username(db=db_session, username="provider_user")
    admin = select_user_by_id(db=db_session, user_id=data_store.admin_user_id)
    assert provider is not None
    assert admin is not None

    uploaded = asyncio.run(
        upload_dataset(
            title="PDF Report",
            description="Demo pdf upload",
            file=pdf_upload,
            current_user=provider,
            db=db_session,
        )
    )
    data_store.uploaded_pdf_dataset_id = uploaded.id

    job = asyncio.run(
        analyze_dataset(dataset_id=uploaded.id, current_user=admin, db=db_session)
    )
    analysis = asyncio.run(
        latest_dataset_analysis(dataset_id=uploaded.id, current_user=admin, db=db_session)
    )

    assert job.job_status == "succeeded"
    assert analysis.representation_type == "document"
    assert analysis.cleaning_status == "skipped"
    assert analysis.export_capabilities["allowed_formats"] == ["raw"]


@pytest.mark.run(order=19)
def test_xlsx_analysis_and_export(
    db_session: Session, data_store: DataStore, xlsx_upload: UploadFile
):
    provider = select_user_by_username(db=db_session, username="provider_user")
    admin = select_user_by_id(db=db_session, user_id=data_store.admin_user_id)
    consumer = select_user_by_id(db=db_session, user_id=data_store.consumer_user_id)
    assert provider is not None
    assert admin is not None
    assert consumer is not None

    uploaded = asyncio.run(
        upload_dataset(
            title="XLSX Population Dataset",
            description="Demo xlsx upload",
            file=xlsx_upload,
            current_user=provider,
            db=db_session,
        )
    )
    data_store.uploaded_xlsx_dataset_id = uploaded.id
    job = asyncio.run(
        analyze_dataset(dataset_id=uploaded.id, current_user=admin, db=db_session)
    )
    analysis = asyncio.run(
        latest_dataset_analysis(dataset_id=uploaded.id, current_user=admin, db=db_session)
    )
    asyncio.run(
        approve_dataset(
            dataset_id=uploaded.id,
            request=ReviewRequest(comment="xlsx analysis looks good"),
            current_user=admin,
            db=db_session,
        )
    )
    asyncio.run(
        publish_dataset(
            dataset_id=uploaded.id,
            request=ReviewRequest(comment="publish xlsx"),
            current_user=admin,
            db=db_session,
        )
    )
    asyncio.run(
        acquire_catalog_dataset(
            dataset_id=uploaded.id,
            current_user=consumer,
            db=db_session,
        )
    )
    export_job = asyncio.run(
        request_dataset_export(
            dataset_id=uploaded.id,
            request=ExportRequest(target_format=ExportFormat.JSON),
            background_tasks=BackgroundTasks(),
            current_user=consumer,
            db=db_session,
        )
    )
    processed = ExportService().process_export_job(db=db_session, job_id=export_job.id)
    download = asyncio.run(
        download_my_export(job_id=export_job.id, current_user=consumer, db=db_session)
    )

    assert job.job_status == "succeeded"
    assert analysis.parser_status == "completed"
    assert analysis.schema_snapshot["sheet_name"] == "population"
    assert "json" in analysis.export_capabilities["allowed_formats"]
    assert processed.job_status == "succeeded"
    assert processed.output_filename == "population.json"
    assert b'"region": "A"' in download.body


def test_summary_tag_generator_uses_llm_when_enabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "GPT_API_KEY", "fake-key")

    def fake_generate_with_llm(self, **kwargs):
        _ = self, kwargs
        return SummaryTagResult(
            public_summary="LLM 生成的公开摘要",
            processing_summary="LLM 生成的处理说明",
            cleaning_summary="LLM 生成的清洗说明",
            risk_summary="LLM 生成的风险说明",
            public_rag_text="LLM 生成的公开问答材料",
            suggested_tags={
                "items": [
                    {
                        "name": "人口",
                        "slug": "population",
                        "category": "domain",
                        "source": "llm",
                        "confidence": 0.9,
                    }
                ]
            },
            llm_output_json={"status": "completed"},
        )

    monkeypatch.setattr(SummaryTagGenerator, "_generate_with_llm", fake_generate_with_llm)
    result = SummaryTagGenerator().generate(
        dataset=DatasetAsset(
            id="DATTEST",
            title="Population Dataset",
            owner_id="USRTEST",
            source_format="csv",
            original_filename="population.csv",
            storage_uri="raw/population.csv",
        ),
        statistics={"common": {"representation_type": "tabular"}},
        cleaning_actions={"items": []},
        issues={"total_count": 0},
        export_capabilities={"allowed_formats": ["raw", "csv", "json", "sql"]},
        use_llm=True,
    )

    assert result.public_summary == "LLM 生成的公开摘要"
    assert result.llm_output_json == {"status": "completed"}
    assert result.suggested_tags["items"][0]["slug"] == "population"


def test_rule_based_cleaner_profiles_tabular_quality():
    parsed = ParsedResult(
        representation_type="tabular",
        schema_snapshot={"columns": [{"name": "Region Name"}, {"name": "Population"}]},
        data=[
            {"Region Name": " A ", "Population": "10"},
            {"Region Name": "A", "Population": "10"},
            {"Region Name": "B", "Population": ""},
        ],
    )
    cleaned = RuleBasedCleaner().clean(parsed=parsed)
    statistics = StatisticsBuilder().build(
        dataset=DatasetAsset(
            id="DATQUALITY",
            title="Quality Dataset",
            owner_id="USRTEST",
            source_format="csv",
            original_filename="quality.csv",
            storage_uri="raw/quality.csv",
        ),
        parsed=parsed,
        cleaned=cleaned,
    )

    assert cleaned.cleaning_status == "completed"
    assert cleaned.normalized_data["record_count"] == 3
    assert cleaned.normalized_data["duplicate_row_count"] == 1
    assert cleaned.normalized_data["missing_value_count"] == 1
    assert cleaned.normalized_data["columns"][0]["normalized_name"] == "region_name"
    assert statistics["tabular"]["duplicate_row_count"] == 1
    assert statistics["tabular"]["column_profiles"][1]["inferred_type"] == "integer"
