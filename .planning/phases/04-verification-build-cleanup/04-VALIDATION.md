# Phase 4: Verification & Build Cleanup - Validation

**Created:** 2026-04-12
**Purpose:** Define the concrete validation matrix for deterministic build, verification, cleanup, and failure behavior without changing the Phase 2/3 success schema.

## Validation Scope

This validation artifact covers only Phase 4 requirements:

- `CLI-02`
- `CLI-03`
- `BLD-01`

It does **not** redesign or revalidate the Phase 2/3 successful JSON schema beyond ensuring the hardened verification path preserves it.

## Required Behaviors

1. `make -C src` builds one executable named `src/fits2json`.
2. `make -C src test` rebuilds the CLI, regenerates the synthetic edge fixture, and runs repo-local success and error-path smoke checks.
3. Usage failure returns exit `2`, writes diagnostics only to stderr, and leaves stdout empty.
4. Missing-file and invalid-selector failures return exit `1`, write diagnostics only to stderr, and leave stdout empty.
5. Repeated runs with the same successful or pre-emission failing input produce the same stdout/stderr shape and exit code.
6. Detectable stdout write failures return exit `1` and a `fits2json:` stderr diagnostic; the empty-stdout guarantee applies to failures detected before emission begins.
7. `make -C src clean` removes generated artifacts only and preserves checked-in files.
8. Python 3 is an accepted prerequisite for `make -C src test`.
9. The synthetic edge fixture is regenerated on every canonical test run.
10. Missing CFITSIO discovery fails early with a readable prerequisite message.

## Validation Matrix

| Requirement | Validation target | Planned check |
|-------------|-------------------|---------------|
| BLD-01 | Canonical build path produces `src/fits2json` from `src/Makefile` | `make -C src clean && make -C src && test -x src/fits2json` |
| CLI-02 | Usage/open/selector/write failures produce stderr diagnostics and non-zero exit codes | `python3 test/phase4_cli_contract_smoke.py` |
| CLI-03 | Success/failure behavior stays deterministic across repeated runs | `python3 test/phase4_cli_contract_smoke.py --mode repeatability` plus Phase 2/3 success smokes under `make -C src test` |
| Contract preservation | Existing Phase 2 and Phase 3 JSON success shapes remain unchanged | `python3 test/phase2_selected_hdu_smoke.py && python3 test/phase3_whole_file_smoke.py` from the Makefile `test` target |
| Cleanup safety | `make -C src clean` removes generated outputs only | Post-clean shell assertions for generated vs checked-in files |

## Fixture Strategy

- `testdata/IRPH0189.HDR` covers usage of a real multi-HDU file for invalid-selector and repeatability checks.
- `testdata/LSPN2790.HDR` remains part of the Phase 3 success-path regression coverage.
- `testdata/phase2-edge.fits` is generated during verification and should be regenerated on every canonical test run.
- No new test framework is needed; direct Python stdlib smoke scripts remain the verification harness.

## Execution Gate

Phase 4 execution is not complete unless these commands pass:

`make -C src clean && make -C src test && make -C src clean`

`make -C src fits2json PKG_CONFIG=false CFITSIO_CFLAGS= CFITSIO_LIBS=`

## Notes

- Validation must preserve the Phase 2/3 success schema while hardening build and failure behavior.
- The broken-pipe/stdout-write nuance is explicitly scoped: detect and report write failures deterministically, but do not claim retroactive zero-byte stdout after downstream consumers have already accepted bytes.
