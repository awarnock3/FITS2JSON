---
phase: 03-whole-file-json-emission
plan: 01
subsystem: cli
tags: [c, cfitsio, json, cli, testing]
requires: [phase-2-selected-hdu-json]
provides:
  - Selectorless whole-file JSON array emission in FITS HDU order
  - Preserved explicit-selector single-HDU JSON contract from Phase 2
  - Repo-local smoke coverage for selectorless array parity against explicit selectors
affects: [phase-4-resilience, cli, testing]
tech-stack:
  added: []
  patterns: [whole-file-document-model, selector-aware-json-emission, absolute-hdu-traversal]
key-files:
  created: [test/phase3_whole_file_smoke.py]
  modified: [src/fits2json.c, test/phase2_selected_hdu_smoke.py]
key-decisions:
  - "Selectorless mode emits one top-level array of Phase 2 HDU objects"
  - "Explicit selector mode remains a single HDU object and is not unified into array output"
patterns-established:
  - "Build the full selectorless document in memory, close the FITS file, then emit JSON once"
  - "Traverse whole files with fits_get_num_hdus plus fits_movabs_hdu while reusing read_selected_hdu_model"
requirements-completed: [HEAD-02, CLI-01]
completed: 2026-04-12
---

# Phase 3: Whole-File JSON Emission Summary

**`fits2json` now supports selectorless whole-file conversion as a top-level JSON array while preserving the locked Phase 2 single-HDU object contract for explicit selectors.**

## Accomplishments
- Removed the old Phase 2 selectorless-rejection assertion from the explicit-selector smoke harness
- Added repo-local Phase 3 smoke coverage that checks selectorless whole-file output matches explicit `[0]` / `[1]` output exactly
- Refactored `src/fits2json.c` to branch on selector presence, reuse the existing per-HDU model builder, and emit selectorless output only after full traversal and file close

## Task Commits

Each task was committed atomically:

1. **Task 1: Add whole-file smoke coverage and preserve explicit-selector regression checks** - `1abebe1` (test)
2. **Task 2: Emit selectorless whole-file JSON arrays while preserving explicit-selector object output** - `d414544` (feat)

**Plan metadata:** `e8b5548` (docs: research + execution plan)

## Files Created/Modified
- `src/fits2json.c` - Selector-aware runtime branch, whole-file document container, absolute HDU traversal, and reusable object/array emitters
- `test/phase2_selected_hdu_smoke.py` - Explicit-selector regression coverage only, without the retired Phase 2 selectorless guard assertion
- `test/phase3_whole_file_smoke.py` - Selectorless whole-file array and explicit-parity smoke checks for repo fixtures

## Decisions Made
- Keep selectorless mode additive: whole-file calls return an array, explicit selectors still return one object
- Reuse `read_selected_hdu_model(...)` for selectorless traversal rather than duplicating FITS parsing logic
- Preserve pure-JSON stdout on success by modeling first, closing the FITS handle, and only then emitting the final array

## Deviations from Plan

None - plan executed exactly as written

## Issues Encountered

- No runtime blockers were hit during execution
- Repo-local smoke still does not demonstrate `BINARY_TBL`; this remains an explicit coverage gap rather than an unverified claim of full HDU-type smoke coverage

## User Setup Required

None - verification uses the existing local toolchain (`make`, `gcc`, `python3`, CFITSIO).

## Next Phase Readiness

- Phase 4 can focus on resilience and failure-hardening without reopening the Phase 2/3 JSON shape decisions
- The selector-aware emission split now gives later phases a stable seam for adding safer diagnostics or tighter failure behavior

---
*Phase: 03-whole-file-json-emission*
*Completed: 2026-04-12*
