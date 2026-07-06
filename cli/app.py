"""CLI command dispatcher."""

from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any

from app.application import SentinelScanApplication
from cli.interface import TerminalRenderer
from cli.messages import error, success, warning
from cli.parser import build_parser
from core.exceptions import SentinelScanError, ValidationError
from core.module import ModuleExecutionContext


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root_path = _resolve_root(args.root)
    renderer = TerminalRenderer()
    application = SentinelScanApplication(root_path)
    context: Any | None = None
    command_name = _command_name(args)

    try:
        context = application.initialize()
        command = args.command or "interactive"
        if command == "interactive":
            _interactive(application, context, renderer)
        elif command == "status":
            renderer.print_status(application.status())
        elif command == "help":
            renderer.print_help()
        elif command == "config":
            _handle_config(args, context, renderer)
        elif command == "projects":
            _handle_projects(args, context, renderer)
        elif command == "sessions":
            _handle_sessions(args, context, renderer)
        elif command == "modules":
            _handle_modules(args, context, renderer)
        elif command == "reports":
            _handle_reports(args, context, renderer)
        elif command == "plugins":
            _handle_plugins(args, context, renderer)
        elif command == "logs":
            _handle_logs(args, context)
        elif command == "maintenance":
            _handle_maintenance(args, context, renderer)
        else:
            parser.print_help()
            return 2
        _record_history(context, command_name, result="success")
        return 0
    except SentinelScanError as exc:
        _record_cli_error(context, command_name, exc)
        print(error(f"Nao foi possivel concluir a operacao: {exc}"), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        _record_cli_error(context, command_name, KeyboardInterrupt("interrupted"))
        print(error("Operacao cancelada pelo usuario."), file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001 - CLI boundary converts faults into safe output.
        _record_cli_error(context, command_name, exc, details={"traceback": traceback.format_exc()})
        print(
            error("Ocorreu um erro inesperado. Detalhes tecnicos foram salvos nos logs."),
            file=sys.stderr,
        )
        return 1
    finally:
        application.shutdown()


def _resolve_root(root_arg: str | None) -> Path:
    if root_arg:
        return Path(root_arg)
    if os.environ.get("SENTINELSCAN_ROOT"):
        return Path(os.environ["SENTINELSCAN_ROOT"])
    return Path(__file__).resolve().parents[1]


def _handle_config(args: Any, context: Any, renderer: TerminalRenderer) -> None:
    if args.config_command == "show":
        renderer.print_json(context.config_service.get())
    elif args.config_command == "get":
        renderer.print_json(context.config_service.get(args.key))
    elif args.config_command == "set":
        context.permission_manager.require("config:write")
        value = _parse_value(args.value)
        context.config_service.set(args.key, value)
        context.audit_service.record("config.updated", target=args.key, details={"value": value})
        print(success(f"Configuration '{args.key}' updated."))
    elif args.config_command == "reset":
        context.permission_manager.require("config:write")
        context.config_service.reset()
        context.audit_service.record("config.reset", target="settings")
        print(success("Configuration restored to defaults."))


def _handle_projects(args: Any, context: Any, renderer: TerminalRenderer) -> None:
    if args.projects_command == "create":
        context.permission_manager.require("projects:write")
        project = context.project_service.create_project(
            args.name, description=args.description, owner=args.owner
        )
        renderer.print_json(project.to_dict())
    elif args.projects_command == "list":
        projects = [project.to_dict() for project in context.project_service.list_projects()]
        renderer.print_table(projects, ["id", "name", "status", "updated_at", "owner"])
    elif args.projects_command == "show":
        renderer.print_json(context.project_service.get_project(args.project_id).to_dict())
    elif args.projects_command == "archive":
        context.permission_manager.require("projects:write")
        project = context.project_service.archive_project(args.project_id)
        print(success(f"Project '{project.id}' archived."))


def _handle_sessions(args: Any, context: Any, renderer: TerminalRenderer) -> None:
    if args.sessions_command == "start":
        context.permission_manager.require("sessions:write")
        session = context.session_service.start_session(
            args.project_id, settings_snapshot=context.config_service.get()
        )
        renderer.print_json(session.to_dict())
    elif args.sessions_command == "end":
        context.permission_manager.require("sessions:write")
        session = context.session_service.end_session(args.project_id, args.session_id, args.state)
        renderer.print_json(session.to_dict())
    elif args.sessions_command == "list":
        sessions = [record.to_dict() for record in context.session_service.list_sessions(args.project_id)]
        renderer.print_table(sessions, ["id", "project_id", "state", "started_at", "ended_at"])


def _handle_modules(args: Any, context: Any, renderer: TerminalRenderer) -> None:
    if args.modules_command == "list":
        renderer.print_table(
            context.module_manager.list_modules(),
            ["id", "name", "category", "version", "state", "description"],
        )
    elif args.modules_command == "run":
        context.permission_manager.require("modules:run")
        parameters = _parse_params(args.param)
        execution_context = ModuleExecutionContext(
            application=context,
            parameters=parameters,
            project_id=args.project,
            session_id=args.session,
        )
        result = context.module_manager.execute(args.module_id, execution_context)
        if args.project and args.session:
            context.session_service.append_event(
                args.project,
                args.session,
                {"type": "module_execution", "module_id": args.module_id, "success": result.success},
            )
        renderer.print_json(result.to_dict())
        if args.report:
            record = context.report_service.generate_report(
                title=f"Module result: {args.module_id}",
                results=result.to_dict(),
                project_id=args.project,
                session_id=args.session,
                report_format=args.report_format
                or context.config_service.get("reports.default_format", "markdown"),
            )
            print(success(f"Report generated: {record.path}"))


def _handle_reports(args: Any, context: Any, renderer: TerminalRenderer) -> None:
    if args.reports_command == "list":
        reports = [report.to_dict() for report in context.report_service.list_reports()]
        renderer.print_table(reports, ["id", "title", "format", "project_id", "generated_at", "path"])
    elif args.reports_command == "generate":
        context.permission_manager.require("reports:write")
        payload = _parse_json(args.data)
        record = context.report_service.generate_report(
            title=args.title,
            results={"success": True, "status": "manual", "data": payload},
            project_id=args.project,
            session_id=args.session,
            report_format=args.format,
        )
        renderer.print_json(record.to_dict())


def _handle_plugins(args: Any, context: Any, renderer: TerminalRenderer) -> None:
    if args.plugins_command == "list":
        renderer.print_table(
            context.plugin_manager.list_plugins(),
            ["id", "name", "category", "version", "enabled", "state", "description"],
        )


def _handle_logs(args: Any, context: Any) -> None:
    if args.logs_command == "audit":
        context.permission_manager.require("logs:read")
        for line in context.log_service.tail_audit(args.limit):
            print(line)


def _handle_maintenance(args: Any, context: Any, renderer: TerminalRenderer) -> None:
    if args.maintenance_command == "clean-temp":
        context.permission_manager.require("maintenance:clean")
        result = context.cleanup_service.clean(dry_run=not args.yes)
        renderer.print_clean_result(result.to_dict())
        if args.yes:
            print(success("Temporary files cleaned safely."))
        else:
            print(warning("Preview only. Run again with --yes to confirm cleanup."))


def _interactive(
    application: SentinelScanApplication, context: Any, renderer: TerminalRenderer
) -> None:
    renderer.print_banner()
    print("Modo interativo")
    while True:
        print(
            renderer.panel(
                "Menu principal",
                [
                    "1. Status",
                    "2. Listar modulos",
                    "3. Listar projetos",
                    "4. Ajuda e navegacao",
                    "5. Simular limpeza de temporarios",
                    "0. Sair corretamente",
                ],
            )
        )
        choice = input("> ").strip()
        if choice == "0":
            renderer.print_final_session_report(application.session_summary())
            print("Encerrando.")
            return
        if choice == "1":
            renderer.print_json(context.resource_monitor.snapshot())
        elif choice == "2":
            renderer.print_table(
                context.module_manager.list_modules(),
                ["id", "name", "category", "version", "state"],
            )
        elif choice == "3":
            renderer.print_table(
                [project.to_dict() for project in context.project_service.list_projects()],
                ["id", "name", "status", "updated_at"],
            )
        elif choice == "4":
            renderer.print_help()
        elif choice == "5":
            renderer.print_clean_result(context.cleanup_service.preview().to_dict())
        else:
            print("Opcao invalida.")


def _command_name(args: Any) -> str:
    parts = [args.command or "interactive"]
    for attribute in (
        "config_command",
        "projects_command",
        "sessions_command",
        "modules_command",
        "reports_command",
        "plugins_command",
        "logs_command",
        "maintenance_command",
    ):
        value = getattr(args, attribute, None)
        if value:
            parts.append(value)
    return "cli." + ".".join(parts)


def _record_history(
    context: Any | None,
    function_name: str,
    result: str,
    details: dict[str, Any] | None = None,
    error_message: str | None = None,
) -> None:
    if context and context.history_service:
        context.history_service.record_action(
            function_name=function_name,
            result=result,
            details=details,
            error=error_message,
        )


def _record_cli_error(
    context: Any | None,
    command_name: str,
    exc: BaseException,
    details: dict[str, Any] | None = None,
) -> None:
    payload = {
        "command": command_name,
        "error_type": type(exc).__name__,
        "error": str(exc),
    }
    if details:
        payload.update(details)
    if context and context.log_service:
        context.log_service.record_event(
            component="cli",
            level="ERROR",
            message=f"Command failed: {command_name}",
            details=payload,
        )
    _record_history(
        context,
        command_name,
        result="error",
        details={"command": command_name},
        error_message=str(exc),
    )


def _parse_params(values: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for item in values:
        if "=" not in item:
            raise ValidationError(f"Invalid parameter '{item}'. Use key=value.")
        key, value = item.split("=", 1)
        parsed[key] = _parse_value(value)
    return parsed


def _parse_value(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _parse_json(value: str) -> dict[str, Any]:
    parsed = _parse_value(value)
    if not isinstance(parsed, dict):
        raise ValidationError("Report data must be a JSON object.")
    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
