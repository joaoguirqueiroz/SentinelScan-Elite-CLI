"""Resource and health snapshots."""

from __future__ import annotations

import platform
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ResourceMonitor:
    """Collects lightweight runtime health indicators."""

    root_path: Path
    started_at: float = field(default_factory=time.perf_counter)

    def snapshot(self, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        uptime = time.perf_counter() - self.started_at
        payload: dict[str, Any] = {
            "uptime_seconds": round(uptime, 4),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "root_path": str(self.root_path),
        }
        if extra:
            payload.update(extra)
        return payload

