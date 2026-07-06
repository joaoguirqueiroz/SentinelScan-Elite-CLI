"""Authorized Nuclei integration module."""

from __future__ import annotations

from typing import Any

from core.exceptions import ValidationError
from core.module import BaseModule, ModuleExecutionContext, ModuleMetadata, ModuleResult
from services.scanner_service import (
    AUTHORIZED_USE_NOTICE,
    ETHICAL_NOTICE,
    ScannerError,
    ScannerExecutionError,
    ScannerParseError,
    ScannerTimeoutError,
    ScannerToolUnavailable,
)


class NucleiScanModule(BaseModule):
    metadata = ModuleMetadata(
        id="nuclei_scan",
        name="Nuclei Authorized Audit",
        version="1.0.0",
        author="Joao Guilherme",
        description="Runs controlled Nuclei audits for owned, lab, or explicitly authorized targets.",
        category="authorized-scanning",
    )

    def validate(self, parameters: dict[str, Any]) -> None:
        scanner = parameters.get("_scanner_service")
        if scanner is None:
            return
        targets = _targets(parameters)
        max_targets = _optional_int(parameters.get("max_targets"))
        scanner.validate_nuclei_targets(targets, max_targets)
        profile = scanner.normalize_nuclei_profile(parameters.get("profile") or "basic")
        if profile == "custom":
            templates = _list_value(parameters.get("templates"))
            if not templates:
                raise ValidationError("Custom Nuclei profile requires at least one template.")
            scanner.validate_nuclei_templates(templates)

    def execute(self, context: ModuleExecutionContext) -> ModuleResult:
        app = context.application
        scanner = app.scanner_service
        parameters = dict(context.parameters)
        parameters["_scanner_service"] = scanner
        self.validate(parameters)

        targets = _targets(parameters)
        profile = scanner.normalize_nuclei_profile(parameters.get("profile") or "basic")
        if not _truthy(parameters.get("authorized")):
            return self._cancelled(app, targets, profile, "Authorization was not confirmed.")
        if profile in {"high", "custom"} and not _truthy(parameters.get("extra_confirmed")):
            return self._cancelled(app, targets, profile, "Advanced or custom profile requires extra confirmation.")

        output_dir = app.report_service.tool_output_dir(context.project_id, context.session_id, "nuclei")
        try:
            command = scanner.build_nuclei_command(
                targets=targets,
                output_dir=output_dir,
                profile=profile,
                templates=_list_value(parameters.get("templates")),
                timeout=parameters.get("timeout"),
                concurrency=parameters.get("concurrency"),
                rate_limit=parameters.get("rate_limit"),
                max_targets=_optional_int(parameters.get("max_targets")),
            )
            execution = scanner.run_nuclei(command, output_dir)
            payload = self._payload(targets, profile, command.to_dict(), execution.to_dict())
            reports = self._generate_reports(app, payload, context)
            payload["reports"] = reports
            self._history(app, "success", payload)
            return self.result(
                success=True,
                status="completed",
                data=payload,
                messages=["Nuclei analysis completed.", f"Reports generated: {len(reports)}"],
            )
        except ScannerToolUnavailable as exc:
            return self._failure(app, "tool_missing", targets, profile, exc)
        except ScannerTimeoutError as exc:
            return self._failure(app, "timeout", targets, profile, exc)
        except ScannerParseError as exc:
            return self._failure(app, "parse_error", targets, profile, exc)
        except ScannerExecutionError as exc:
            return self._failure(app, "execution_error", targets, profile, exc)
        except ScannerError as exc:
            return self._failure(app, "scanner_error", targets, profile, exc)

    def _payload(
        self,
        targets: list[str],
        profile: str,
        command: dict[str, Any],
        execution: dict[str, Any],
    ) -> dict[str, Any]:
        findings = execution.get("parsed", {}).get("findings", [])
        severities: dict[str, int] = {}
        for finding in findings:
            severity = finding.get("severity", "unknown")
            severities[severity] = severities.get(severity, 0) + 1
        return {
            "tool": "nuclei",
            "targets": targets,
            "profile": profile,
            "authorized_notice": AUTHORIZED_USE_NOTICE,
            "ethical_notice": ETHICAL_NOTICE,
            "command": command,
            "execution": execution,
            "summary": {
                "targets": len(targets),
                "findings": len(findings),
                "severities": severities,
            },
        }

    def _generate_reports(
        self, app: Any, payload: dict[str, Any], context: ModuleExecutionContext
    ) -> list[dict[str, Any]]:
        reports: list[dict[str, Any]] = []
        for report_format in _report_formats(context.parameters.get("report_formats")):
            record = app.report_service.generate_report(
                title="Nuclei Authorized Audit",
                results={"success": True, "status": "completed", "data": payload},
                project_id=context.project_id,
                session_id=context.session_id,
                report_format=report_format,
                tool="nuclei",
            )
            reports.append(record.to_dict())
        return reports

    def _cancelled(self, app: Any, targets: list[str], profile: str, reason: str) -> ModuleResult:
        payload = {
            "tool": "nuclei",
            "targets": targets,
            "profile": profile,
            "authorized": False,
            "ethical_notice": ETHICAL_NOTICE,
            "reason": reason,
        }
        self._history(app, "cancelled", payload)
        return self.result(True, "cancelled", payload, [reason, "Nuclei was not executed."])

    def _failure(
        self, app: Any, status: str, targets: list[str], profile: str, exc: Exception
    ) -> ModuleResult:
        payload = {"tool": "nuclei", "targets": targets, "profile": profile, "error": str(exc)}
        if app.log_service:
            app.log_service.record_event(
                component="nuclei_scan",
                level="ERROR",
                message=f"Nuclei scan failed: {status}",
                details=payload,
            )
        self._history(app, "error", payload, str(exc))
        return self.result(False, status, payload, [str(exc), "Technical details were saved to logs."])

    def _history(
        self, app: Any, result: str, details: dict[str, Any], error: str | None = None
    ) -> None:
        if app.history_service:
            app.history_service.record_action(
                "scanner.nuclei",
                result=result,
                details=details,
                error=error,
            )


def _targets(parameters: dict[str, Any]) -> list[str]:
    raw = parameters.get("targets", parameters.get("target"))
    values = _list_value(raw)
    if not values:
        raise ValidationError("Nuclei target list cannot be empty.")
    return values


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "sim", "s", "confirmo"}


def _list_value(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _report_formats(value: Any) -> list[str]:
    formats = _list_value(value) or ["txt", "json", "csv", "html"]
    allowed = {"txt", "json", "csv", "html", "markdown"}
    invalid = [item for item in formats if item not in allowed]
    if invalid:
        raise ValidationError(f"Unsupported report format: {invalid[0]}")
    return formats


MODULE_CLASS = NucleiScanModule
