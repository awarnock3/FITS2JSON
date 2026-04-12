---
phase: 04-verification-build-cleanup
plan: 01
subsystem: cli
tags: [c, cfitsio, make, testing, cli]
requires: [phase-3-whole-file-json]
provides:
  - Canonical `make -C src`, `make -C src test`, and `make -C src clean` workflow
  - Stable CLI failure contract with `fits2json:` stderr diagnostics and exit codes `0/1/2`
  - Repo-local smoke coverage for failure semantics, repeatability, and write-path failures
affects: [release-readiness, cli, build, testing]
tech-stack:
  added: []
  patterns: [makefile-owned-verification, centralized-cli-failure-mapping, pkg-config-discovery]
key-files:
  created: [test/phase4_cli_contract_smoke.py]
  modified: [src/fits2json.c, src/Makefile]
key-decisions:
  - "Use `make -C src test` as the canonical repo-local verification entry point"
  - "Map usage failures to exit 2 and conversion/build/test/write failures to exit 1"
  - "Scope the empty-stdout guarantee to pre-emission failures while still surfacing detectable write-path failures deterministically"
patterns-established:
  - "Prefer `pkg-config cfitsio` with standard make-variable overrides for portability"
  - "Use explicit generated-artifact cleanup lists rather than broad globs"
requirements-completed: [CLI-02, CLI-03, BLD-01]
completed: 2026-04-12
---

# Phase 4: Verification & Build Cleanup Summary

**`fits2json` now has a repeatable Makefile-owned build/test/clean workflow and a deterministic CLI failure contract without changing the Phase 2/3 success schema.**

## Accomplishments
- Added a dedicated Phase 4 smoke harness for usage failure, missing-file failure, invalid-selector failure, repeated-run determinism, and write-path failure handling
- Centralized runtime failure reporting in `src/fits2json.c` so all failures now use `fits2json:` stderr diagnostics and stable `0/1/2` exit categories
- Reworked `src/Makefile` into the canonical build/test/clean surface with `pkg-config`-first CFITSIO discovery, explicit Python prerequisite checking, unconditional synthetic fixture regeneration during `test`, and safe generated-artifact cleanup

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Phase 4 CLI-contract smoke coverage** - `50f4a5b` (test)
2. **Task 2: Harden runtime failure handling and exit-code mapping** - `4824769` (fix)
3. **Task 3: Make `src/Makefile` the canonical verification and cleanup surface** - `81aabfe` (build)
4. **Task 3 follow-up: Force a fresh CLI rebuild on every `make -C src test` run** - `5e6baa2` (build)

**Plan metadata:** `b50378f` (docs: research + execution plan)

## Files Created/Modified
- `test/phase4_cli_contract_smoke.py` - Error-path, repeatability, and write-path failure smoke coverage using Python stdlib
- `src/fits2json.c` - Centralized failure helpers, stable app exit-code mapping, and `SIGPIPE` handling for detectable write-path failures
- `src/Makefile` - Canonical `all`, `test`, and `clean` targets with `pkg-config`-first CFITSIO discovery and explicit generated-artifact cleanup

## Decisions Made
- Treat Python 3 as an accepted verification prerequisite for `make -C src test`
- Regenerate the synthetic `testdata/phase2-edge.fits` fixture on every canonical test run
- Preserve the stronger empty-stdout guarantee for usage and other pre-emission failures, while documenting and testing the scoped behavior for detectable stdout write failures after emission begins

## Deviations from Plan

None - plan executed as written after the planning pass resolved the broken-pipe contract and prerequisite decisions explicitly.

## Issues Encountered

- The first broken-pipe smoke probe closed the read end too late, allowing small JSON outputs to finish before the writer observed a pipe failure; the probe was tightened to start the CLI with no reader at all so the write-path failure becomes deterministic
- The first verifier pass found that repeated `make -C src test` runs were not forcing a fresh `fits2json` rebuild; the `test` target was updated to run `$(MAKE) --always-make fits2json` so the canonical verification command now rebuilds the CLI every time

## User Setup Required

None beyond the existing local toolchain (`make`, `cc`, `python3`, `pkg-config`, CFITSIO).

## Next Phase Readiness

- The repository now has a single canonical local verification command that can be reused for release checks and future maintenance work
- The CLI failure contract is now stable enough for final phase verification and milestone completion without reopening the Phase 2/3 output-shape decisions

---
*Phase: 04-verification-build-cleanup*
*Completed: 2026-04-12*
