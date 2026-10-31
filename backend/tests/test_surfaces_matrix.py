"""The generated model matrix cannot drift from the code (rule R15).

`docs/spec/models-matrix.md` is written by `scripts/surfaces.py --write`. Before this
check, nothing compared the committed file with what the code generates, so adding a
model without regenerating it left the spec silently wrong. `--check`, which CI runs,
now fails when the file is missing or stale.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_script():
    spec = importlib.util.spec_from_file_location("surfaces_script", ROOT / "scripts" / "surfaces.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


surfaces = _load_script()


def test_committed_matrix_matches_the_code():
    expected = surfaces._markdown(surfaces._rows())
    assert surfaces.MATRIX_PATH.read_text(encoding="utf-8") == expected, (
        "docs/spec/models-matrix.md is stale: run "
        "python scripts/surfaces.py --write docs/spec/models-matrix.md"
    )


def test_check_passes_when_the_matrix_is_current(tmp_path):
    rows = surfaces._rows()
    matrix = tmp_path / "models-matrix.md"
    matrix.write_text(surfaces._markdown(rows), encoding="utf-8")
    assert surfaces._check(rows, matrix=matrix) == 0


def test_check_fails_when_the_matrix_is_stale(tmp_path, capsys):
    rows = surfaces._rows()
    matrix = tmp_path / "models-matrix.md"
    matrix.write_text(surfaces._markdown(rows).replace("✓", "✗", 1), encoding="utf-8")
    assert surfaces._check(rows, matrix=matrix) == 1
    err = capsys.readouterr().err
    assert "out of date" in err
    assert "--write" in err


def test_check_fails_when_the_matrix_is_missing(tmp_path, capsys):
    rows = surfaces._rows()
    assert surfaces._check(rows, matrix=tmp_path / "absent.md") == 1
    assert "missing" in capsys.readouterr().err
