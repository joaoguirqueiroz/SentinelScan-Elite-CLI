"""Presentation helpers for the terminal interface."""

from __future__ import annotations

import json
from typing import Any

from core.constants import APP_NAME, APP_VERSION
from cli.tables import format_table


class TerminalRenderer:
    """Renders consistent CLI output."""

    def banner(self) -> str:
        return f"{APP_NAME} v{APP_VERSION}"

    def print_banner(self) -> None:
        print(self.banner())

    def print_json(self, payload: Any) -> None:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))

    def print_table(self, rows: list[dict[str, Any]], columns: list[str]) -> None:
        print(format_table(rows, columns))

    def print_status(self, status: dict[str, Any]) -> None:
        self.print_banner()
        print(f"Root: {status['root_path']}")
        print(f"Modules: {status['modules']} | Plugins: {status['plugins']} | Projects: {status['projects']}")
        health = status.get("health", {})
        if health:
            print(f"Uptime: {health.get('uptime_seconds')}s | Python: {health.get('python_version')}")

