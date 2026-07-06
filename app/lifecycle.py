"""Lifecycle utility helpers."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.application import SentinelScanApplication
from app.context import ApplicationContext


@contextmanager
def managed_application(root_path: Path) -> Iterator[ApplicationContext]:
    application = SentinelScanApplication(root_path)
    try:
        yield application.initialize()
    finally:
        application.shutdown()

