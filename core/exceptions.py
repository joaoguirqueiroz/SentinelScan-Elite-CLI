"""Domain exceptions used across the application."""

from __future__ import annotations


class SentinelScanError(Exception):
    """Base exception for all expected application errors."""


class BootstrapError(SentinelScanError):
    """Raised when the application cannot initialize safely."""


class ConfigurationError(SentinelScanError):
    """Raised for invalid or unavailable configuration values."""


class ValidationError(SentinelScanError):
    """Raised when user or component input is invalid."""


class PermissionDeniedError(SentinelScanError):
    """Raised when the active profile cannot perform an operation."""


class ModuleError(SentinelScanError):
    """Raised for module discovery, validation, or execution failures."""


class PluginError(SentinelScanError):
    """Raised for plugin discovery, validation, or lifecycle failures."""


class ProjectError(SentinelScanError):
    """Raised for project catalog and project workspace failures."""


class SessionError(SentinelScanError):
    """Raised for session lifecycle failures."""


class ReportError(SentinelScanError):
    """Raised for report generation and catalog failures."""

