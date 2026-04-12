# Phase 3: Whole-File JSON Emission - Validation

**Created:** 2026-04-12
**Purpose:** Define the concrete validation matrix for whole-file selectorless output without changing the locked Phase 2 explicit-selector contract.

## Validation Scope

This validation artifact covers only Phase 3 requirements:

- `HEAD-02`
- `CLI-01`

It does **not** change or revalidate the Phase 2 per-HDU schema beyond ensuring selectorless array elements reuse it.

## Required Behaviors

1. Selectorless invocation returns one top-level JSON array in HDU file order.
2. Each array element is the existing Phase 2 HDU object shape: `index`, `type`, `cards`.
3. Explicit selector mode still returns one HDU object, not a one-element array.
4. Successful selectorless and explicit runs write only JSON to stdout with no success stderr output.
5. One-HDU files still return a one-element array in selectorless mode.

## Validation Matrix

| Requirement | Validation target | Planned check |
|-------------|-------------------|---------------|
| HEAD-02 | Selectorless invocation returns one JSON document covering all HDUs in file order | `python3 test/phase3_whole_file_smoke.py` on `IRPH0189.HDR` and `LSPN2790.HDR` |
| CLI-01 | Successful whole-file output is pipe-safe JSON on stdout | Phase 3 smoke asserts `json.loads(stdout)` succeeds and `stderr` is empty |
| Contract preservation | Explicit selector mode remains a single object | Phase 2 smoke plus Phase 3 parity assertions compare selectorless array elements to explicit `[0]` / `[1]` outputs |

## Fixture Strategy

- `testdata/IRPH0189.HDR` covers selectorless multi-HDU array behavior with two HDUs.
- `testdata/LSPN2790.HDR` covers selectorless one-element-array behavior on a one-HDU file.
- Existing repo fixtures do not currently provide verified `BINARY_TBL` smoke coverage; that should be called out in execution summary if still true after implementation.

## Execution Gate

Phase 3 execution is not complete unless this command passes:

`make -C src fits2json && python3 test/phase2_selected_hdu_smoke.py --cases core && python3 test/phase3_whole_file_smoke.py`

## Notes

- Validation must preserve the locked split between selectorless array mode and explicit single-object mode.
- No new test framework is needed; repo-local Python stdlib smoke scripts are sufficient.
