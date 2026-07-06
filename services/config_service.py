"""Centralized configuration management."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.constants import DEFAULT_CONFIG_FILE, RUNTIME_CONFIG_FILE
from core.exceptions import ConfigurationError
from core.validators import ensure_relative_path
from services.storage import ensure_dir, read_json, write_json


FALLBACK_CONFIG: dict[str, Any] = {
    "app": {"language": "pt-BR", "timezone": "America/Fortaleza"},
    "ui": {"theme": "dark", "table_style": "compact", "progress": True},
    "paths": {
        "workdir": "data/projects",
        "reports": "reports",
        "logs": "logs",
        "cache": "cache",
        "backups": "backups",
    },
    "logging": {
        "level": "INFO",
        "max_bytes": 1048576,
        "backup_count": 5,
        "retention_days": 30,
    },
    "reports": {"default_format": "markdown", "template": "technical"},
    "security": {"active_profile": "administrator"},
    "performance": {"max_tasks": 4, "cache_enabled": True},
    "modules": {},
    "plugins": {},
}


class ConfigService:
    """Loads, validates, persists, and exposes application settings."""

    VALID_THEMES = {"dark", "light", "high-contrast"}
    VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    VALID_REPORT_FORMATS = {"markdown", "txt", "json", "csv", "html"}

    def __init__(self, root_path: Path) -> None:
        self.root_path = root_path
        self.default_config_path = root_path / DEFAULT_CONFIG_FILE
        self.runtime_config_path = root_path / RUNTIME_CONFIG_FILE
        self.settings: dict[str, Any] = {}

    def load(self) -> dict[str, Any]:
        try:
            default_config = read_json(self.default_config_path, default=None)
        except json.JSONDecodeError:
            default_config = None
        if default_config is None:
            default_config = deepcopy(FALLBACK_CONFIG)
        try:
            runtime_config = read_json(self.runtime_config_path, default={})
        except json.JSONDecodeError:
            runtime_config = {}
        merged = self._deep_merge(deepcopy(default_config), runtime_config)
        self.settings = self.validate(merged)
        return deepcopy(self.settings)

    def validate(self, settings: dict[str, Any]) -> dict[str, Any]:
        config = self._deep_merge(deepcopy(FALLBACK_CONFIG), settings)
        theme = config["ui"].get("theme")
        if theme not in self.VALID_THEMES:
            config["ui"]["theme"] = FALLBACK_CONFIG["ui"]["theme"]
        log_level = str(config["logging"].get("level", "INFO")).upper()
        if log_level not in self.VALID_LOG_LEVELS:
            log_level = "INFO"
        config["logging"]["level"] = log_level
        report_format = config["reports"].get("default_format")
        if report_format not in self.VALID_REPORT_FORMATS:
            config["reports"]["default_format"] = "markdown"
        for key, value in config.get("paths", {}).items():
            ensure_relative_path(str(value), f"paths.{key}")
        return config

    def save(self) -> None:
        if not self.settings:
            raise ConfigurationError("Configuration has not been loaded.")
        write_json(self.runtime_config_path, self.settings)

    def reset(self) -> dict[str, Any]:
        self.settings = self.validate(deepcopy(FALLBACK_CONFIG))
        write_json(self.runtime_config_path, self.settings)
        return deepcopy(self.settings)

    def get(self, key: str | None = None, default: Any | None = None) -> Any:
        if not self.settings:
            self.load()
        if key is None:
            return deepcopy(self.settings)
        current: Any = self.settings
        for part in key.split("."):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return deepcopy(current)

    def set(self, key: str, value: Any) -> dict[str, Any]:
        if not key:
            raise ConfigurationError("Configuration key cannot be empty.")
        if not self.settings:
            self.load()
        current = self.settings
        parts = key.split(".")
        for part in parts[:-1]:
            node = current.setdefault(part, {})
            if not isinstance(node, dict):
                raise ConfigurationError(f"Cannot set nested key below '{part}'.")
            current = node
        current[parts[-1]] = value
        self.settings = self.validate(self.settings)
        self.save()
        return deepcopy(self.settings)

    def resolve_path(self, path_key: str) -> Path:
        path_value = self.get(f"paths.{path_key}")
        if path_value is None:
            raise ConfigurationError(f"Path configuration '{path_key}' does not exist.")
        return self.root_path / ensure_relative_path(str(path_value), f"paths.{path_key}")

    def ensure_directories(self) -> None:
        for value in self.get("paths", default={}).values():
            ensure_dir(self.root_path / ensure_relative_path(str(value), "paths"))
        ensure_dir(self.runtime_config_path.parent)

    def _deep_merge(self, base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
        for key, value in overlay.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                base[key] = self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base
