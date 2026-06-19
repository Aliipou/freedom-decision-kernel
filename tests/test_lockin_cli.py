"""
Tests for the lockin-scan production CLI (fdk_research.lockin_cli).

Hermetic: each test writes its own knowledge base + manifest to a temp dir, so the
tests do not depend on the seed data's contents.
"""
from __future__ import annotations

import json
from pathlib import Path

from fdk_research.lockin_cli import load_kb, main, resolve, scan

_KB = {
    "records": [
        {"name": "DynamoDB", "switching_cost": 0.9, "portability": 0.1, "alternatives": 0},
        {"name": "PostgreSQL", "switching_cost": 0.2, "portability": 0.9, "alternatives": 5},
    ]
}
_MANIFEST = {
    "name": "demo",
    "stack": [
        {"service": "DynamoDB", "weight": 0.7},
        {"service": "PostgreSQL", "weight": 0.3},
        {"service": "MysteryService", "weight": 0.1},
    ],
}


def _write(tmp_path: Path) -> tuple[Path, Path]:
    kb = tmp_path / "kb.json"
    man = tmp_path / "stack.json"
    kb.write_text(json.dumps(_KB), encoding="utf-8")
    man.write_text(json.dumps(_MANIFEST), encoding="utf-8")
    return kb, man


def test_load_and_resolve(tmp_path):
    kb_path, _ = _write(tmp_path)
    kb = load_kb([kb_path])
    deps, unknown = resolve(_MANIFEST["stack"], kb)
    assert [d.name for d in deps] == ["DynamoDB", "PostgreSQL"]
    assert unknown == ["MysteryService"]  # not silently scored


def test_scan_result_shape(tmp_path):
    kb_path, _ = _write(tmp_path)
    result = scan(_MANIFEST, load_kb([kb_path]))
    assert result["name"] == "demo"
    assert 0.0 <= result["lockin_risk"] <= 1.0
    assert result["band"] in {"LOW", "MEDIUM", "HIGH"}
    assert result["unknown_services"] == ["MysteryService"]
    assert "# Lock-in report" in result["report"]


def test_cli_text_output_lists_unknown(tmp_path, capsys):
    kb_path, man_path = _write(tmp_path)
    code = main([str(man_path), "--kb", str(kb_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "Lock-in report" in out
    assert "UNKNOWN" in out and "MysteryService" in out


def test_cli_json_output(tmp_path, capsys):
    kb_path, man_path = _write(tmp_path)
    code = main([str(man_path), "--kb", str(kb_path), "--format", "json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["name"] == "demo"
    assert "lockin_risk" in payload


def test_cli_fail_over_gate_trips(tmp_path, capsys):
    kb_path, man_path = _write(tmp_path)
    # DynamoDB-heavy manifest -> high risk -> should exceed a low threshold.
    code = main([str(man_path), "--kb", str(kb_path), "--fail-over", "0.3"])
    err = capsys.readouterr().err
    assert code == 1
    assert "FAIL" in err


def test_cli_fail_over_gate_passes(tmp_path, capsys):
    kb_path, man_path = _write(tmp_path)
    code = main([str(man_path), "--kb", str(kb_path), "--fail-over", "0.99"])
    assert code == 0


def test_cli_text_output_all_known_no_unknown_section(tmp_path, capsys):
    kb_path = tmp_path / "kb.json"
    kb_path.write_text(json.dumps(_KB), encoding="utf-8")
    man_path = tmp_path / "stack.json"
    man_path.write_text(
        json.dumps({"name": "clean", "stack": [{"service": "PostgreSQL", "weight": 1.0}]}),
        encoding="utf-8",
    )
    code = main([str(man_path), "--kb", str(kb_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "UNKNOWN" not in out  # the all-known branch
