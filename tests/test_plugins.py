from __future__ import annotations

from pathlib import Path

from core.events import EventBus
from core.plugin_manager import PluginManager


VALID_PLUGIN_CODE = """
from core.plugin import BasePlugin, PluginContext, PluginMetadata

class ValidPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="valid_plugin",
        name="Valid Plugin",
        version="1.0.0",
        author="Tester",
        description="Valid",
        category="tests",
    )
    def initialize(self, context: PluginContext) -> None:
        context.application.history_service.append("plugin", "valid.initialized")

PLUGIN_CLASS = ValidPlugin
"""


def write_plugin(root: Path, plugin_id: str, manifest: dict, code: str | None = None) -> Path:
    plugin_dir = root / "plugins" / plugin_id
    plugin_dir.mkdir(parents=True, exist_ok=True)
    import json

    (plugin_dir / "plugin.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if code is not None:
        (plugin_dir / manifest.get("entrypoint", "plugin.py")).write_text(
            code,
            encoding="utf-8",
        )
    return plugin_dir


def plugin_manifest(plugin_id: str, **overrides):
    metadata = {
        "id": plugin_id,
        "name": plugin_id.replace("_", " ").title(),
        "version": "1.0.0",
        "author": "Tester",
        "description": "Test plugin",
        "category": "tests",
        "min_app_version": "1.0.0",
        "dependencies": [],
        "components": [],
    }
    metadata.update(overrides.pop("metadata", {}))
    manifest = {
        "enabled": True,
        "entrypoint": "plugin.py",
        "class_name": "PLUGIN_CLASS",
        "metadata": metadata,
    }
    manifest.update(overrides)
    return manifest


def test_plugin_manager_loads_example_plugin(context):
    plugins = context.plugin_manager.list_plugins()

    assert any(plugin["id"] == "example_plugin" and plugin["state"] == "initialized" for plugin in plugins)


def test_plugin_manager_discovers_valid_dynamic_plugin(context, runtime_root):
    write_plugin(runtime_root, "valid_plugin", plugin_manifest("valid_plugin"), VALID_PLUGIN_CODE)
    manager = PluginManager(context, EventBus())

    entries = manager.discover(runtime_root / "plugins")
    manager.initialize_all()

    assert any(entry.metadata.id == "valid_plugin" for entry in entries)
    assert manager.registry["valid_plugin"].state.value == "initialized"


def test_plugin_without_entrypoint_registers_as_loaded(context, runtime_root):
    manifest = plugin_manifest("manifest_only")
    manifest.pop("entrypoint")
    write_plugin(runtime_root, "manifest_only", manifest)
    manager = PluginManager(context, EventBus())

    manager.discover(runtime_root / "plugins")
    manager.initialize_all()

    assert manager.registry["manifest_only"].state.value == "loaded"


def test_disabled_plugin_is_not_initialized(context, runtime_root):
    manifest = plugin_manifest("disabled_plugin", enabled=False)
    write_plugin(runtime_root, "disabled_plugin", manifest, VALID_PLUGIN_CODE)
    manager = PluginManager(context, EventBus())

    manager.discover(runtime_root / "plugins")
    manager.initialize_all()

    assert manager.registry["disabled_plugin"].state.value == "disabled"


def test_invalid_plugin_manifest_is_skipped(context, runtime_root):
    write_plugin(runtime_root, "invalid_plugin", {"metadata": {"id": "invalid_plugin"}})
    manager = PluginManager(context, EventBus())

    entries = manager.discover(runtime_root / "plugins")

    assert not any(entry.metadata.id == "invalid_plugin" for entry in entries)


def test_incompatible_plugin_is_skipped(context, runtime_root):
    manifest = plugin_manifest(
        "future_plugin",
        metadata={"min_app_version": "99.0.0"},
    )
    write_plugin(runtime_root, "future_plugin", manifest, VALID_PLUGIN_CODE)
    manager = PluginManager(context, EventBus())

    manager.discover(runtime_root / "plugins")

    assert "future_plugin" not in manager.registry


def test_plugin_missing_entrypoint_file_is_skipped(context, runtime_root):
    write_plugin(runtime_root, "missing_entry", plugin_manifest("missing_entry"))
    manager = PluginManager(context, EventBus())

    manager.discover(runtime_root / "plugins")

    assert "missing_entry" not in manager.registry


def test_plugin_class_must_inherit_base_plugin(context, runtime_root):
    code = "class NotAPlugin:\n    pass\nPLUGIN_CLASS = NotAPlugin\n"
    write_plugin(runtime_root, "bad_class", plugin_manifest("bad_class"), code)
    manager = PluginManager(context, EventBus())

    manager.discover(runtime_root / "plugins")

    assert "bad_class" not in manager.registry


def test_plugin_initialize_and_shutdown_failures_are_isolated(context, runtime_root):
    code = """
from core.plugin import BasePlugin, PluginContext, PluginMetadata
class FailingPlugin(BasePlugin):
    metadata = PluginMetadata(id="failing_plugin", name="Failing", version="1.0.0", author="Tester", description="Fails", category="tests")
    def initialize(self, context: PluginContext) -> None:
        raise RuntimeError("init failed")
    def shutdown(self) -> None:
        raise RuntimeError("shutdown failed")
PLUGIN_CLASS = FailingPlugin
"""
    write_plugin(runtime_root, "failing_plugin", plugin_manifest("failing_plugin"), code)
    manager = PluginManager(context, EventBus())

    manager.discover(runtime_root / "plugins")
    manager.initialize_all()
    manager.shutdown_all()

    assert manager.registry["failing_plugin"].state.value == "error"
    assert manager.registry["failing_plugin"].last_error in {"init failed", "shutdown failed"}


def test_plugin_discovery_missing_directory_returns_empty(context, tmp_path):
    assert PluginManager(context, EventBus()).discover(Path(tmp_path) / "missing") == []
