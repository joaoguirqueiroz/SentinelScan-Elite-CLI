"""Report generation and report catalog service."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from core.constants import APP_NAME, APP_VERSION
from core.exceptions import ReportError
from services.audit_service import AuditService
from services.storage import ensure_dir, read_json, write_json


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ReportRecord:
    id: str
    title: str
    format: str
    path: str
    project_id: str | None = None
    session_id: str | None = None
    generated_at: str = field(default_factory=utc_now)
    template: str = "technical"
    version: str = APP_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ReportService:
    """Turns module and project results into structured documents."""

    def __init__(
        self,
        root_path: Path,
        reports_dir: Path,
        audit: AuditService | None = None,
    ) -> None:
        self.root_path = root_path
        self.reports_dir = reports_dir
        self.audit = audit
        self.index_path = reports_dir / "reports_index.json"
        ensure_dir(reports_dir)

    def generate_report(
        self,
        title: str,
        results: dict[str, Any],
        project_id: str | None = None,
        session_id: str | None = None,
        report_format: str = "markdown",
        template: str = "technical",
    ) -> ReportRecord:
        if report_format not in {"markdown", "json"}:
            raise ReportError(f"Unsupported report format '{report_format}'.")
        report_id = f"report-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:8]}"
        report_dir = self._target_dir(project_id)
        extension = "md" if report_format == "markdown" else "json"
        report_path = report_dir / f"{report_id}.{extension}"
        payload = self._payload(report_id, title, results, project_id, session_id, template)
        if report_format == "markdown":
            report_path.write_text(self._render_markdown(payload), encoding="utf-8")
        else:
            report_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        record = ReportRecord(
            id=report_id,
            title=title,
            format=report_format,
            path=str(report_path.relative_to(self.root_path)),
            project_id=project_id,
            session_id=session_id,
            template=template,
        )
        self._register(record)
        self._audit(
            "report.generated",
            report_id,
            {"project_id": project_id, "session_id": session_id, "format": report_format},
        )
        return record

    def list_reports(self) -> list[ReportRecord]:
        index = read_json(self.index_path, default=[]) or []
        return [ReportRecord(**payload) for payload in index]

    def _target_dir(self, project_id: str | None) -> Path:
        date_path = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        root = self.reports_dir / (project_id or "global") / date_path
        return ensure_dir(root)

    def _payload(
        self,
        report_id: str,
        title: str,
        results: dict[str, Any],
        project_id: str | None,
        session_id: str | None,
        template: str,
    ) -> dict[str, Any]:
        return {
            "metadata": {
                "id": report_id,
                "title": title,
                "application": APP_NAME,
                "version": APP_VERSION,
                "template": template,
                "generated_at": utc_now(),
                "project_id": project_id,
                "session_id": session_id,
            },
            "executive_summary": {
                "status": results.get("status", "completed"),
                "success": results.get("success", True),
                "items": len(results.get("data", {})) if isinstance(results.get("data"), dict) else 0,
            },
            "results": results,
        }

    def _render_markdown(self, payload: dict[str, Any]) -> str:
        metadata = payload["metadata"]
        summary = payload["executive_summary"]
        result_json = json.dumps(payload["results"], ensure_ascii=False, indent=2, sort_keys=True)
        return (
            f"# {metadata['title']}\n\n"
            f"## Metadados\n\n"
            f"- Aplicacao: {metadata['application']}\n"
            f"- Versao: {metadata['version']}\n"
            f"- Identificador: {metadata['id']}\n"
            f"- Projeto: {metadata.get('project_id') or 'global'}\n"
            f"- Sessao: {metadata.get('session_id') or 'nao vinculada'}\n"
            f"- Gerado em: {metadata['generated_at']}\n\n"
            f"## Resumo Executivo\n\n"
            f"- Status: {summary['status']}\n"
            f"- Sucesso: {summary['success']}\n"
            f"- Itens principais: {summary['items']}\n\n"
            f"## Resultados\n\n"
            f"```json\n{result_json}\n```\n"
        )

    def _register(self, record: ReportRecord) -> None:
        index = read_json(self.index_path, default=[]) or []
        index.append(record.to_dict())
        write_json(self.index_path, index)

    def _audit(
        self, action: str, target: str, details: dict[str, Any] | None = None
    ) -> None:
        if self.audit:
            self.audit.record(action=action, target=target, details=details)

