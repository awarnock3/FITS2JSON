#!/usr/bin/env python3

"""Phase 4 smoke checks for CLI failure semantics and repeatability.

The locked Phase 4 contract distinguishes between:
- failures detected before emission begins, which must keep stdout empty, and
- detectable stdout write failures after emission begins, which must still
  return exit 1 and write a short stderr diagnostic, but cannot retroactively
  guarantee zero-byte stdout once downstream consumers have already read bytes.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BINARY = REPO_ROOT / "src" / "fits2json"
EDGE_FIXTURE = REPO_ROOT / "testdata" / "phase2-edge.fits"


def run(cmd: list[str], *, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=text,
        capture_output=True,
        check=False,
    )


def assert_failure(args: list[str], expected_rc: int, required_substrings: list[str]) -> None:
    proc = run(args)
    if proc.returncode != expected_rc:
        raise AssertionError(
            f"expected rc={expected_rc} for {args}, got {proc.returncode}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    if proc.stdout != "":
        raise AssertionError(f"expected empty stdout for {args}, got:\n{proc.stdout}")
    for text in required_substrings:
        if text not in proc.stderr:
            raise AssertionError(f"missing stderr text {text!r} for {args}\nstderr:\n{proc.stderr}")


def assert_repeatable(arg: str) -> None:
    first = run([str(BINARY), arg])
    second = run([str(BINARY), arg])
    if (first.returncode, first.stdout, first.stderr) != (
        second.returncode,
        second.stdout,
        second.stderr,
    ):
        raise AssertionError(
            f"repeatability mismatch for {arg}\n"
            f"first rc={first.returncode}\nstdout:\n{first.stdout}\nstderr:\n{first.stderr}\n\n"
            f"second rc={second.returncode}\nstdout:\n{second.stdout}\nstderr:\n{second.stderr}"
        )


def assert_usage_failure() -> None:
    assert_failure([str(BINARY)], 2, ["fits2json:", "Usage:"])


def assert_missing_file_failure() -> None:
    assert_failure(
        [str(BINARY), "testdata/does-not-exist.fits"],
        1,
        ["fits2json:", "FITSIO status ="],
    )


def assert_invalid_selector_failure() -> None:
    assert_failure(
        [str(BINARY), "testdata/IRPH0189.HDR[NOPE]"],
        1,
        ["fits2json:", "FITSIO status ="],
    )


def assert_repeatability() -> None:
    if not EDGE_FIXTURE.exists():
        raise AssertionError(
            f"missing generated fixture at {EDGE_FIXTURE}; create it before running repeatability checks"
        )

    assert_repeatable("testdata/IRPH0189.HDR[0]")
    assert_repeatable("testdata/IRPH0189.HDR")
    assert_repeatable(str(EDGE_FIXTURE) + "[0]")
    assert_repeatable("testdata/does-not-exist.fits")
    assert_repeatable("testdata/IRPH0189.HDR[NOPE]")


def assert_broken_pipe_behavior() -> None:
    read_fd, write_fd = os.pipe()
    os.close(read_fd)

    proc = subprocess.Popen(
        [str(BINARY), "testdata/IRPH0189.HDR"],
        cwd=REPO_ROOT,
        stdout=write_fd,
        stderr=subprocess.PIPE,
        text=False,
    )
    os.close(write_fd)

    if proc.stderr is None:
        raise AssertionError("failed to capture stderr for broken-pipe probe")

    stderr = proc.stderr.read().decode("utf-8", errors="replace")
    proc.stderr.close()
    rc = proc.wait()

    if rc != 1:
        raise AssertionError(f"broken-pipe probe should exit 1, got {rc}\nstderr:\n{stderr}")
    if "fits2json:" not in stderr:
        raise AssertionError(f"broken-pipe probe missing fits2json stderr prefix:\n{stderr}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices={"all", "errors", "repeatability", "broken-pipe"},
        default="all",
    )
    args = parser.parse_args()

    if args.mode in {"all", "errors"}:
        assert_usage_failure()
        assert_missing_file_failure()
        assert_invalid_selector_failure()

    if args.mode in {"all", "repeatability"}:
        assert_repeatability()

    if args.mode in {"all", "broken-pipe"}:
        assert_broken_pipe_behavior()

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
