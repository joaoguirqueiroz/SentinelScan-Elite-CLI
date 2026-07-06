"""High-level application lifecycle."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.bootstrap import Bootstrapper
from app.context import ApplicationContext
from core.constants import APP_NAME, APP_VERSION


class SentinelScanApplication:
    """Coordinates startup, status reporting, and shutdown."""

    def __init__(self, root_path: Path) -> None:
        self.root_path = root_path
        self.context: ApplicationContext | None = None

    def initialize(self) -> ApplicationContext:
        if self.context is None:
            self.context = Bootstrapper(self.root_path).bootstrap()
        return self.context

    def status(self) -> dict[str, Any]:
        context = self.initialize()
        modules = context.module_manager.list_modules() if context.module_manager else []
        plugins = context.plugin_manager.list_plugins() if context.plugin_manager else []
        projects = context.project_service.list_projects() if context.project_service else []
        health = (
            context.resource_monitor.snapshot(
                {
                    "modules": len(modules),
                    "plugins": len(plugins),
                    "projects": len(projects),
                }
            )
            if context.resource_monitor
            else {}
        )
        return {
            "application": APP_NAME,
            "version": APP_VERSION,
            "root_path": str(context.root_path),
            "modules": len(modules),
            "plugins": len(plugins),
            "projects": len(projects),
            "health": health,
        }

    def shutdown(self) -> None:
        if self.context is None:
            return
        if self.context.module_manager:
            self.context.module_manager.shutdown_all()
        if self.context.plugin_manager:
            self.context.plugin_manager.shutdown_all()
        if self.context.log_service:
            self.context.log_service.record_event(
                component="application",
                level="INFO",
                message=f"{APP_NAME} shutdown completed.",
            )

