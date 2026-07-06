"""General activity history storage."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from services.storage import append_jsonl, ensure_dir


class HistoryService:
    def __init__(self, history_dir: Path) -> None:
        self.history_dir = ensure_dir(history_dir)
        self.history_file = self.history_dir / "activity.jsonl"

    def append(self, component: str, action: str, details: dict[str, Any] | None = None) -> None:
        append_jsonl(
            self.history_file,
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "component": component,
                "action": action,
                "details": details or {},
            },
        )

