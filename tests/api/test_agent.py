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
from axionara.core.db.crud import select_user_by_id, select_user_by_username
from axionara.core.model.dataset import ExportFormat, ExportRequest, ReviewRequest
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


@pytest.mark.run(order=15)
def test_my_datasets_lists_acquired_dataset(db_session: Session, data_store: DataStore):
    consumer = select_user_by_id(db=db_session, user_id=data_store.consumer_user_id)
    assert consumer is not None

    rows = asyncio.run(my_datasets(current_user=consumer, db=db_session))

    assert len(rows) == 1
    assert rows[0].dataset.id == data_store.uploaded_dataset_id
    assert rows[0].grant.grant_status == "granted"
    assert "csv" in rows[0].tags


@pytest.mark.run(order=16)
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


@pytest.mark.run(order=17)
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
