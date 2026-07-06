"""Terminal table formatting."""

from __future__ import annotations

from typing import Any, Iterable


def format_table(rows: Iterable[dict[str, Any]], columns: list[str]) -> str:
    items = list(rows)
    if not items:
        return "No records found."
    widths = {
        column: max(len(column), *(len(str(row.get(column, ""))) for row in items))
        for column in columns
    }
    header = " | ".join(column.ljust(widths[column]) for column in columns)
    separator = "-+-".join("-" * widths[column] for column in columns)
    body = [
        " | ".join(str(row.get(column, "")).ljust(widths[column]) for column in columns)
        for row in items
    ]
    return "\n".join([header, separator, *body])

