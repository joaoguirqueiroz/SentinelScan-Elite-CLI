"""Run a small local smoke check."""

from __future__ import annotations

from pathlib import Path

from app.application import SentinelScanApplication


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    app = SentinelScanApplication(root)
    try:
        status = app.status()
        print(status)
        return 0
    finally:
        app.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())

