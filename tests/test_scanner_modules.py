from __future__ import annotations

from core.module import ModuleExecutionContext
from services.scanner_service import ScannerExecution


def test_scanner_modules_are_discovered(context):
    module_ids = {module["id"] for module in context.module_manager.list_modules()}

    assert {"nmap_scan", "nuclei_scan"} <= module_ids


def test_nmap_module_cancelled_without_authorization(context):
    result = context.module_manager.execute(
        "nmap_scan",
        ModuleExecutionContext(
            application=context,
            parameters={"target": "127.0.0.1", "profile": "basic"},
        ),
    )

    assert result.success is True
    assert result.status == "cancelled"
    assert result.data["tool"] == "nmap"


def test_nmap_module_reports_missing_tool(context, monkeypatch):
    monkeypatch.setattr(context.scanner_service, "is_installed", lambda binary: False)

    result = context.module_manager.execute(
        "nmap_scan",
        ModuleExecutionContext(
            application=context,
            parameters={"target": "127.0.0.1", "authorized": True},
        ),
    )

    assert result.success is False
    assert result.status == "tool_missing"
    assert "Nmap" in result.messages[0]


def test_nmap_module_success_generates_reports_and_history(context, monkeypatch):
    def fake_run(command, output_dir):
        return ScannerExecution(
            tool="nmap",
            profile=command.profile,
            command=command.args,
            return_code=0,
            output_files=command.output_files,
            parsed={
                "hosts": [
                    {
                        "host": "127.0.0.1",
                        "status": "up",
                        "ports": [{"port": "80", "protocol": "tcp", "state": "open"}],
                    }
                ]
            },
        )

    monkeypatch.setattr(context.scanner_service, "run_nmap", fake_run)

    result = context.module_manager.execute(
        "nmap_scan",
        ModuleExecutionContext(
            application=context,
            parameters={"target": "127.0.0.1", "authorized": True},
        ),
    )

    assert result.success is True
    assert result.data["summary"]["open_ports"] == 1
    assert len(result.data["reports"]) == 4
    assert all("\\nmap\\" in report["path"] or "/nmap/" in report["path"] for report in result.data["reports"])
    assert any(record["function"] == "scanner.nmap" for record in context.history_service.read_recent(10))


def test_nuclei_module_requires_extra_confirmation_for_high_profile(context):
    result = context.module_manager.execute(
        "nuclei_scan",
        ModuleExecutionContext(
            application=context,
            parameters={"target": "http://localhost", "profile": "high", "authorized": True},
        ),
    )

    assert result.success is True
    assert result.status == "cancelled"
    assert "extra confirmation" in result.messages[0].lower()


def test_nuclei_module_success_generates_reports_and_history(context, monkeypatch):
    def fake_run(command, output_dir):
        return ScannerExecution(
            tool="nuclei",
            profile=command.profile,
            command=command.args,
            return_code=0,
            output_files=command.output_files,
            parsed={
                "findings": [
                    {
                        "target": "http://localhost",
                        "template": "test-template",
                        "name": "Test Finding",
                        "severity": "medium",
                        "endpoint": "http://localhost/login",
                        "timestamp": "2026-07-06T10:00:00Z",
                    }
                ]
            },
        )

    monkeypatch.setattr(context.scanner_service, "run_nuclei", fake_run)

    result = context.module_manager.execute(
        "nuclei_scan",
        ModuleExecutionContext(
            application=context,
            parameters={"target": "http://localhost", "authorized": True},
        ),
    )

    assert result.success is True
    assert result.data["summary"]["findings"] == 1
    assert result.data["summary"]["severities"] == {"medium": 1}
    assert len(result.data["reports"]) == 4
    assert all(
        "\\nuclei\\" in report["path"] or "/nuclei/" in report["path"]
        for report in result.data["reports"]
    )
    assert any(record["function"] == "scanner.nuclei" for record in context.history_service.read_recent(10))
