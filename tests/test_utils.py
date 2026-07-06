from __future__ import annotations

import json

from cli.messages import error, success, warning
from cli.tables import format_table
from services.storage import append_jsonl, ensure_dir, read_json, write_json


def test_storage_helpers_write_read_and_append(tmp_path):
    directory = ensure_dir(tmp_path / "nested")
    json_path = directory / "payload.json"
    jsonl_path = directory / "events.jsonl"

    write_json(json_path, {"b": 2, "a": 1})
    append_jsonl(jsonl_path, {"event": "ok"})

    assert read_json(json_path) == {"a": 1, "b": 2}
    assert json.loads(jsonl_path.read_text(encoding="utf-8").strip()) == {"event": "ok"}
    assert read_json(directory / "missing.json", default={"fallback": True}) == {"fallback": True}


def test_format_table_empty_and_populated():
    assert format_table([], ["id"]) == "No records found."

    table = format_table([{"id": "a", "name": "Alpha"}], ["id", "name"])

    assert "id" in table
    assert "Alpha" in table
    assert "-+-" in table


def test_cli_message_helpers():
    assert success("done") == "[OK] done"
    assert warning("check") == "[WARN] check"
    assert error("bad") == "[ERROR] bad"

