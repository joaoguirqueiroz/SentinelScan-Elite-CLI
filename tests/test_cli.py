from __future__ import annotations

import json

import pytest

from cli.app import _parse_json, _parse_params, _parse_value, main
from core.exceptions import ValidationError


def run_cli(capsys, runtime_root, *args):
    exit_code = main(["--root", str(runtime_root), *args])
    captured = capsys.readouterr()
    return exit_code, captured


def test_cli_status_initializes_application(runtime_root, capsys):
    exit_code, captured = run_cli(capsys, runtime_root, "status")

    assert exit_code == 0
    assert "SentinelScan Elite CLI" in captured.out
    assert "Modules:" in captured.out


def test_cli_config_show_get_set_and_reset(runtime_root, capsys):
    assert run_cli(capsys, runtime_root, "config", "set", "ui.theme", '"light"')[0] == 0
    exit_code, captured = run_cli(capsys, runtime_root, "config", "get", "ui.theme")
    assert exit_code == 0
    assert "light" in captured.out

    assert run_cli(capsys, runtime_root, "config", "show")[0] == 0
    assert run_cli(capsys, runtime_root, "config", "reset")[0] == 0


def test_cli_project_and_session_flow(runtime_root, capsys):
    exit_code, captured = run_cli(
        capsys,
        runtime_root,
        "projects",
        "create",
        "Projeto CLI",
        "--description",
        "Fluxo funcional",
    )
    project = json.loads(captured.out)

    assert exit_code == 0
    assert run_cli(capsys, runtime_root, "projects", "show", project["id"])[0] == 0
    assert run_cli(capsys, runtime_root, "projects", "list")[0] == 0

    exit_code, captured = run_cli(capsys, runtime_root, "sessions", "start", project["id"])
    session = json.loads(captured.out)

    assert exit_code == 0
    assert run_cli(capsys, runtime_root, "sessions", "list", project["id"])[0] == 0
    assert run_cli(capsys, runtime_root, "sessions", "end", project["id"], session["id"])[0] == 0
    assert run_cli(capsys, runtime_root, "projects", "archive", project["id"])[0] == 0


def test_cli_module_run_and_report_generation(runtime_root, capsys):
    exit_code, captured = run_cli(
        capsys,
        runtime_root,
        "modules",
        "run",
        "asset_inventory",
        "--param",
        "assets=host-a,host-b",
        "--report",
    )

    assert exit_code == 0
    assert '"total_assets": 2' in captured.out
    assert "[OK] Report generated" in captured.out
    assert run_cli(capsys, runtime_root, "reports", "list")[0] == 0


def test_cli_reports_generate_json(runtime_root, capsys):
    exit_code, captured = run_cli(
        capsys,
        runtime_root,
        "reports",
        "generate",
        "--title",
        "Manual",
        "--format",
        "json",
        "--data",
        '{"status":"ok"}',
    )

    assert exit_code == 0
    assert json.loads(captured.out)["format"] == "json"


def test_cli_plugins_and_logs(runtime_root, capsys):
    assert run_cli(capsys, runtime_root, "plugins", "list")[0] == 0
    exit_code, captured = run_cli(capsys, runtime_root, "logs", "audit", "--limit", "5")

    assert exit_code == 0
    assert "application.initialized" in captured.out or "shutdown completed" in captured.out


def test_cli_invalid_module_returns_error(runtime_root, capsys):
    exit_code, captured = run_cli(capsys, runtime_root, "modules", "run", "missing")

    assert exit_code == 1
    assert "[ERROR]" in captured.err


def test_cli_invalid_param_returns_error(runtime_root, capsys):
    exit_code, captured = run_cli(
        capsys,
        runtime_root,
        "modules",
        "run",
        "asset_inventory",
        "--param",
        "invalid",
    )

    assert exit_code == 1
    assert "key=value" in captured.err


def test_cli_permission_failure_is_safe(runtime_root, capsys):
    run_cli(capsys, runtime_root, "config", "set", "security.active_profile", '"viewer"')

    exit_code, captured = run_cli(capsys, runtime_root, "projects", "create", "Nao Pode")

    assert exit_code == 1
    assert "cannot perform" in captured.err


def test_cli_uses_environment_root(runtime_root, capsys, monkeypatch):
    monkeypatch.setenv("SENTINELSCAN_ROOT", str(runtime_root))

    exit_code = main(["status"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(runtime_root) in captured.out


def test_cli_interactive_smoke(runtime_root, capsys, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "0")

    exit_code = main(["--root", str(runtime_root), "interactive"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Modo interativo" in captured.out


def test_cli_parse_helpers():
    assert _parse_value("true") is True
    assert _parse_value("plain") == "plain"
    assert _parse_params(["a=1", "b=true"]) == {"a": 1, "b": True}
    assert _parse_json('{"a":1}') == {"a": 1}

    with pytest.raises(ValidationError):
        _parse_params(["bad"])
    with pytest.raises(ValidationError):
        _parse_json("[1,2]")
