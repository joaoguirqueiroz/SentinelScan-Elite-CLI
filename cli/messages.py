"""CLI message helpers."""

from __future__ import annotations


def success(message: str) -> str:
    return f"[OK] {message}"


def warning(message: str) -> str:
    return f"[WARN] {message}"


def error(message: str) -> str:
    return f"[ERROR] {message}"

