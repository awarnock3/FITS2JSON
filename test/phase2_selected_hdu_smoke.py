#!/usr/bin/env python3

"""Phase 2 smoke checks for selected-HDU JSON output.

Repo fixtures cover ordered cards plus repeated COMMENT/HISTORY behavior.
The synthetic edge fixture closes the otherwise-missing long-string /
CONTINUE / HIERARCH coverage gap for FITS-04.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BINARY = REPO_ROOT / "src" / "fits2json"
EDGE_FIXTURE = REPO_ROOT / "testdata" / "phase2-edge.fits"


def run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_fits2json(selector: str) -> dict:
    proc = run([str(BINARY), selector])
    if proc.returncode != 0:
        raise AssertionError(
            f"fits2json failed for {selector}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    if proc.stderr.strip():
        raise AssertionError(f"expected no stderr on success for {selector}, got:\n{proc.stderr}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"invalid JSON for {selector}: {exc}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        ) from exc


def assert_selectorless_rejected() -> None:
    proc = run([str(BINARY), str(REPO_ROOT / "testdata" / "IRPH0189.HDR")])
    if proc.returncode == 0:
        raise AssertionError("selectorless invocation should fail during Phase 2")
    if proc.stdout.strip():
        raise AssertionError(f"selectorless failure should not write stdout, got:\n{proc.stdout}")
    if "explicit HDU selector required" not in proc.stderr:
        raise AssertionError(f"missing selectorless guidance on stderr:\n{proc.stderr}")


def assert_card_shape(card: dict) -> None:
    if set(card) - {"keyword", "value", "comment"}:
        raise AssertionError(f"unexpected card fields: {card}")
    if "keyword" not in card or not isinstance(card["keyword"], str) or not card["keyword"]:
        raise AssertionError(f"card missing keyword: {card}")
    if "comment" in card and not isinstance(card["comment"], str):
        raise AssertionError(f"card comment must be a string: {card}")
    if "value" in card and not isinstance(card["value"], (bool, str)):
        raise AssertionError(f"card value must be bool or string: {card}")


def assert_hdu_shape(doc: dict) -> None:
    if set(doc) != {"index", "type", "cards"}:
        raise AssertionError(f"unexpected top-level keys: {sorted(doc.keys())}")
    if not isinstance(doc["index"], int) or doc["index"] < 1:
        raise AssertionError(f"invalid HDU index: {doc['index']!r}")
    if doc["type"] not in {"IMAGE_HDU", "ASCII_TBL", "BINARY_TBL"}:
        raise AssertionError(f"unexpected HDU type: {doc['type']!r}")
    if not isinstance(doc["cards"], list) or not doc["cards"]:
        raise AssertionError("cards must be a non-empty list")
    for card in doc["cards"]:
        if not isinstance(card, dict):
            raise AssertionError(f"card must be an object: {card!r}")
        assert_card_shape(card)


def assert_no_continue_cards(cards: list[dict]) -> None:
    if any(card["keyword"] == "CONTINUE" for card in cards):
        raise AssertionError("physical CONTINUE cards leaked into JSON output")


def find_first(cards: list[dict], keyword: str) -> dict:
    for card in cards:
        if card["keyword"] == keyword:
            return card
    raise AssertionError(f"missing keyword {keyword}")


def assert_irph0189() -> None:
    doc = run_fits2json(str(REPO_ROOT / "testdata" / "IRPH0189.HDR[0]"))
    assert_hdu_shape(doc)
    cards = doc["cards"]
    assert_no_continue_cards(cards)

    if doc["index"] != 1 or doc["type"] != "IMAGE_HDU":
        raise AssertionError(f"unexpected selected HDU metadata: {doc['index']}, {doc['type']}")

    expected_prefix = ["SIMPLE", "BITPIX", "NAXIS", "EXTEND", "OBJECT"]
    prefix = [card["keyword"] for card in cards[: len(expected_prefix)]]
    if prefix != expected_prefix:
        raise AssertionError(f"unexpected keyword prefix: {prefix!r}")

    simple = find_first(cards, "SIMPLE")
    if simple.get("value") is not True:
        raise AssertionError(f"SIMPLE should map to true, got: {simple}")

    object_card = find_first(cards, "OBJECT")
    if object_card.get("value") != "P/HALLEY":
        raise AssertionError(f"OBJECT string mismatch: {object_card}")


def assert_lspn2790() -> None:
    doc = run_fits2json(str(REPO_ROOT / "testdata" / "LSPN2790.HDR[0]"))
    assert_hdu_shape(doc)
    cards = doc["cards"]
    assert_no_continue_cards(cards)

    comment_cards = [card for card in cards if card["keyword"] == "COMMENT"]
    history_cards = [card for card in cards if card["keyword"] == "HISTORY"]

    if len(comment_cards) < 10:
        raise AssertionError(f"expected many COMMENT cards, saw {len(comment_cards)}")
    if len(history_cards) < 10:
        raise AssertionError(f"expected many HISTORY cards, saw {len(history_cards)}")
    if any("value" in card for card in comment_cards + history_cards):
        raise AssertionError("COMMENT/HISTORY cards must not expose value fields")

    comment_texts = [card.get("comment", "") for card in comment_cards]
    history_texts = [card.get("comment", "") for card in history_cards]

    if not any("SUBMITTING STATION" in text for text in comment_texts):
        raise AssertionError("expected COMMENT text for submitting station")
    if not any("CONVERTED TO FITS BY PROGRAM" in text for text in history_texts):
        raise AssertionError("expected conversion HISTORY text")

    keywords = [card["keyword"] for card in cards]
    if keywords.count("COMMENT") < 2 or "OBSVTORY" not in keywords:
        raise AssertionError("expected repeated COMMENT cards before observatory metadata")


def assert_edge_fixture(path: Path) -> None:
    doc = run_fits2json(f"{path}[0]")
    assert_hdu_shape(doc)
    cards = doc["cards"]
    assert_no_continue_cards(cards)

    longstr = find_first(cards, "LONGSTR")
    expected_longstr = (
        "This synthetic long string exists to verify CONTINUE folding, JSON escaping, "
        "and that Phase 2 emits one logical card instead of duplicated physical helpers."
    )
    if longstr.get("value") != expected_longstr:
        raise AssertionError(f"LONGSTR mismatch: {longstr}")

    hierarch = None
    for card in cards:
        if "LONG.KEY" in card["keyword"]:
            hierarch = card
            break
    if hierarch is None:
        raise AssertionError("missing HIERARCH-derived keyword")
    if hierarch.get("value") != "VALUE":
        raise AssertionError(f"unexpected HIERARCH value: {hierarch}")

    bool_card = find_first(cards, "BOOLKEY")
    if bool_card.get("value") is not True:
        raise AssertionError(f"BOOLKEY should map to true: {bool_card}")

    comment_cards = [card for card in cards if card["keyword"] == "COMMENT"]
    history_cards = [card for card in cards if card["keyword"] == "HISTORY"]
    if any("value" in card for card in comment_cards + history_cards):
        raise AssertionError("synthetic COMMENT/HISTORY should not expose value")
    if not any(card.get("comment") == "phase 2 synthetic comment" for card in comment_cards):
        raise AssertionError("missing synthetic COMMENT text")
    if not any(card.get("comment") == "phase 2 synthetic history" for card in history_cards):
        raise AssertionError("missing synthetic HISTORY text")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--fixture-only", type=Path)
    parser.add_argument("--cases", choices={"all", "core"}, default="all")
    args = parser.parse_args()

    if args.build:
        proc = run(["make", "-C", "src", "fits2json"])
        if proc.returncode != 0:
            sys.stderr.write(proc.stdout)
            sys.stderr.write(proc.stderr)
            return proc.returncode

    if args.fixture_only is not None:
        assert_edge_fixture(args.fixture_only)
        return 0

    assert_selectorless_rejected()
    assert_irph0189()
    assert_lspn2790()

    if args.cases == "all":
        if not EDGE_FIXTURE.exists():
            raise AssertionError(
                f"missing synthetic fixture at {EDGE_FIXTURE}; run test/phase2_make_edge_fixture first"
            )
        assert_edge_fixture(EDGE_FIXTURE)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
