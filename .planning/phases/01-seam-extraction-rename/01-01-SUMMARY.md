---
phase: 01-seam-extraction-rename
plan: 01
subsystem: cli
tags: [c, cfitsio, make, rename, cli]
requires: []
provides:
  - Renamed the runtime entry source from `src/listhead.c` to `src/fits2json.c`
  - Retargeted the `src/Makefile` build to produce only `fits2json`
  - Switched user-facing naming in help text and `README.md` to `fits2json`
affects: [phase-2-header-modeling, build, cli]
tech-stack:
  added: []
  patterns: [single-c-program rename, make-target-aligned-with-entry-source]
key-files:
  created: [src/fits2json.c]
  modified: [src/Makefile, README.md]
key-decisions:
  - "Renamed the entry source directly with no compatibility shim"
  - "Builds now target only `fits2json` with no `listhead` alias"
patterns-established:
  - "Rename the C entry file, Makefile target, and user-facing CLI name together"
  - "Preserve existing CFITSIO selector behavior while changing only the seam"
requirements-completed: [BLD-02, HEAD-03]
duration: 0min
completed: 2026-04-12
---

# Phase 1: Seam Extraction & Rename Summary

**`fits2json` now replaces the legacy `listhead` seam while preserving the existing CFITSIO HDU selector flow.**

## Performance

- **Duration:** 0 min
- **Started:** 2026-04-12T15:43:33Z
- **Completed:** 2026-04-12T15:43:33Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Renamed the single runtime translation unit to `src/fits2json.c`
- Retargeted the build so `src/Makefile` produces only the `fits2json` executable
- Updated CLI help/examples and the top-level README to use the new program name consistently

## Task Commits

Each task was committed atomically:

1. **Task 1: Rename the CLI entry source and preserve selector behavior** - `45e527e` (feat)
2. **Task 2: Retarget the build and top-level naming to `fits2json` only** - `de27809` (build)

**Plan metadata:** `01b8ea4` (docs: create phase plan)

## Files Created/Modified
- `src/fits2json.c` - Renamed single-file CLI entry point with preserved CFITSIO selector flow
- `src/Makefile` - Builds `fits2json` from `src/fits2json.c`
- `README.md` - Top-level naming aligned to `fits2json`

## Decisions Made
- None - followed plan as specified

## Deviations from Plan

None - plan executed exactly as written

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 2 can now build on `src/fits2json.c` instead of the legacy `listhead` entry point
- The CLI rename seam is complete; remaining work can focus on structured JSON modeling and emission

---
*Phase: 01-seam-extraction-rename*
*Completed: 2026-04-12*
