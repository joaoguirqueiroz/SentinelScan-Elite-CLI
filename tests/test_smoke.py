from __future__ import annotations

from cli.app import main


def test_smoke_status_modules_plugins_and_reports(runtime_root, capsys):
    assert main(["--root", str(runtime_root), "status"]) == 0
    assert main(["--root", str(runtime_root), "modules", "list"]) == 0
    assert main(["--root", str(runtime_root), "plugins", "list"]) == 0
    assert main(["--root", str(runtime_root), "reports", "list"]) == 0
    captured = capsys.readouterr()

    assert "SentinelScan Elite CLI" in captured.out
    assert "asset_inventory" in captured.out
    assert "example_plugin" in captured.out

