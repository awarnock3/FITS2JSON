#!/usr/bin/env python3

"""Phase 3 smoke checks for selectorless whole-file JSON output.

Existing repo fixtures cover whole-file array parity for multi-HDU and single-HDU
files. Current repo-local smoke does not exercise BINARY_TBL; keep that gap
explicit instead of pretending it is covered.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BINARY = REPO_ROOT / "src" / "fits2json"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def load_json(arg: str):
    proc = run([str(BINARY), arg])
    if proc.returncode != 0:
        raise AssertionError(
            f"fits2json failed for {arg}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    if proc.stderr.strip():
        raise AssertionError(f"expected empty stderr on success for {arg}, got:\n{proc.stderr}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"invalid JSON for {arg}: {exc}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        ) from exc


def assert_irph0189_whole_file() -> None:
    selectorless = load_json(str(REPO_ROOT / "testdata" / "IRPH0189.HDR"))
    explicit0 = load_json(str(REPO_ROOT / "testdata" / "IRPH0189.HDR[0]"))
    explicit1 = load_json(str(REPO_ROOT / "testdata" / "IRPH0189.HDR[1]"))

    if not isinstance(selectorless, list):
        raise AssertionError(f"selectorless IRPH0189 should return a list, got {type(selectorless)!r}")
    if len(selectorless) != 2:
        raise AssertionError(f"selectorless IRPH0189 should expose 2 HDUs, got {len(selectorless)}")
    if selectorless[0] != explicit0:
        raise AssertionError("selectorless HDU 0 does not exactly match explicit [0] output")
    if selectorless[1] != explicit1:
        raise AssertionError("selectorless HDU 1 does not exactly match explicit [1] output")

    indices = [item.get("index") for item in selectorless]
    if indices != [1, 2]:
        raise AssertionError(f"unexpected IRPH0189 HDU order/indexes: {indices!r}")


def assert_lspn2790_whole_file() -> None:
    selectorless = load_json(str(REPO_ROOT / "testdata" / "LSPN2790.HDR"))
    explicit0 = load_json(str(REPO_ROOT / "testdata" / "LSPN2790.HDR[0]"))

    if not isinstance(selectorless, list):
        raise AssertionError(f"selectorless LSPN2790 should return a list, got {type(selectorless)!r}")
    if len(selectorless) != 1:
        raise AssertionError(f"selectorless LSPN2790 should expose 1 HDU, got {len(selectorless)}")
    if selectorless[0] != explicit0:
        raise AssertionError("selectorless LSPN2790 element does not exactly match explicit [0] output")


def main() -> int:
    assert_irph0189_whole_file()
    assert_lspn2790_whole_file()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
