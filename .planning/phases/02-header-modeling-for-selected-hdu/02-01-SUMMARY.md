---
phase: 02-header-modeling-for-selected-hdu
plan: 01
subsystem: cli
tags: [c, cfitsio, json, cli, testing]
requires: []
provides:
  - Selected-HDU JSON emission with top-level `index`, `type`, and ordered `cards`
  - Ordered FITS card normalization that preserves COMMENT/HISTORY records and folds long strings
  - Repo-local smoke coverage for selected-HDU JSON plus synthetic long-string/HIERARCH edge cases
affects: [phase-3-whole-file-json, cli, testing]
tech-stack:
  added: []
  patterns: [ordered-header-card-model, selected-hdu-json-emission, cfitsio-longstring-folding]
key-files:
  created: [test/phase2_make_edge_fixture.c, test/phase2_selected_hdu_smoke.py]
  modified: [src/fits2json.c, .gitignore]
key-decisions:
  - "Phase 2 requires an explicit HDU selector so whole-file JSON remains deferred to Phase 3"
  - "FITS logicals emit as JSON booleans while other present FITS values emit as JSON strings"
patterns-established:
  - "Model the selected HDU fully in memory before writing JSON to stdout"
  - "Preserve FITS header order with ordered `cards` rather than flattening to a keyword object"
requirements-completed: [HEAD-01, HEAD-04, HEAD-05, FITS-01, FITS-02, FITS-03, FITS-04]
duration: 7min
completed: 2026-04-12
---

# Phase 2: Header Modeling for Selected HDU Summary

**`fits2json` now converts one explicitly selected HDU into structured JSON while preserving FITS header order, repeated commentary records, and long-string semantics.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-12T16:24:09Z
- **Completed:** 2026-04-12T16:31:30Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- Added repo-local verification assets for Phase 2, including a CFITSIO-generated edge fixture covering long-string and HIERARCH handling
- Reworked `src/fits2json.c` from a raw card dumper into a selected-HDU JSON converter with an in-memory header model
- Locked selectorless invocation out of Phase 2 so whole-file JSON remains a Phase 3 concern instead of silently changing behavior early

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Phase 2 verification assets before production edits** - `d909047` (test)
2. **Tasks 2-3: Build the selected-HDU model and emit the Phase 2 JSON contract** - `9724047` (feat)

**Plan metadata:** `9fed395` (docs: research + execution plan)

## Files Created/Modified
- `src/fits2json.c` - Selected-HDU model, CFITSIO-backed card normalization, JSON emission, and selectorless guardrail
- `test/phase2_make_edge_fixture.c` - Synthetic FITS fixture generator for long-string and HIERARCH coverage
- `test/phase2_selected_hdu_smoke.py` - Automated JSON smoke checks for repo fixtures and the synthetic edge case
- `.gitignore` - Ignores generated Phase 2 helper artifacts and the built `src/fits2json` binary

## Decisions Made
- Keep Phase 2 selected-HDU only by requiring an explicit selector and rejecting selectorless whole-file-style invocation
- Emit JSON booleans only for FITS logical values; preserve all other present FITS values as JSON strings for safety

## Deviations from Plan

None - plan executed exactly as written

## Issues Encountered

None

## User Setup Required

None - verification uses the existing local toolchain (`make`, `gcc`, `python3`, CFITSIO).

## Next Phase Readiness

- Phase 3 can build on the ordered single-HDU card model instead of re-parsing FITS headers
- Whole-file JSON emission can now focus on wrapping repeated per-HDU conversion cleanly without changing the selected-HDU contract

---
*Phase: 02-header-modeling-for-selected-hdu*
*Completed: 2026-04-12*
