"""Run a small local smoke check."""

from __future__ import annotations

import os
from pathlib import Path

from app.application import SentinelScanApplication


def main(root_path: Path | None = None) -> int:
    root = root_path or Path(os.environ.get("SENTINELSCAN_ROOT", Path(__file__).resolve().parents[1]))
    app = SentinelScanApplication(root)
    try:
        status = app.status()
        print(status)
        return 0
    finally:
        app.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
