from __future__ import annotations

import json

import pytest

from core.exceptions import ReportError
from services.report_service import ReportRecord, ReportService


def test_report_service_generates_markdown(runtime_root, context):
    record = context.report_service.generate_report(
        "Markdown Report",
        {"success": True, "status": "ok", "data": {"items": 2}},
    )

    path = runtime_root / record.path
    assert path.exists()
    assert "# Markdown Report" in path.read_text(encoding="utf-8")
    assert record.format == "markdown"


def test_report_service_generates_json(runtime_root, context):
    record = context.report_service.generate_report(
        "JSON Report",
        {"success": True, "status": "ok", "data": {"items": 2}},
        report_format="json",
    )

    payload = json.loads((runtime_root / record.path).read_text(encoding="utf-8"))
    assert payload["metadata"]["title"] == "JSON Report"
    assert payload["executive_summary"]["items"] == 1


def test_report_service_rejects_unsupported_format(context):
    with pytest.raises(ReportError):
        context.report_service.generate_report("Bad", {}, report_format="pdf")


def test_report_service_lists_persisted_reports(context):
    first = context.report_service.generate_report("A", {"data": {}})
    second = context.report_service.generate_report("B", {"data": {}})

    report_ids = [report.id for report in context.report_service.list_reports()]

    assert first.id in report_ids
    assert second.id in report_ids


def test_report_record_to_dict():
    record = ReportRecord(id="r1", title="Title", format="json", path="reports/r1.json")

    assert record.to_dict()["id"] == "r1"


def test_report_service_can_be_constructed_directly(runtime_root):
    service = ReportService(runtime_root, runtime_root / "custom_reports")

    record = service.generate_report("Direct", {"success": True, "data": {}})

    assert (runtime_root / record.path).exists()

