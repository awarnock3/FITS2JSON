# Phase 2: Header Modeling for Selected HDU - Validation

**Created:** 2026-04-12
**Purpose:** Define the concrete validation matrix for the Phase 2 plan so execution and verification measure the locked selected-HDU JSON contract instead of drifting into Phase 3 behavior.

## Validation Scope

This validation artifact covers only Phase 2 requirements:

- `HEAD-01`
- `HEAD-04`
- `HEAD-05`
- `FITS-01`
- `FITS-02`
- `FITS-03`
- `FITS-04`

It does **not** validate whole-file output semantics (`HEAD-02`, `CLI-01`), which remain deferred to Phase 3.

## Required Behaviors

1. A CFITSIO-selected HDU converts to one valid JSON object on stdout.
2. The top-level object contains only the locked Phase 2 contract surfaces: `index`, `type`, and ordered `cards`.
3. Card objects expose `keyword`, `value` only when present, and `comment` only when present.
4. `COMMENT` and `HISTORY` remain repeated ordered card entries with no `value`.
5. Original header order is preserved.
6. Physical `CONTINUE` helper cards are not emitted separately after long-string folding.
7. HIERARCH and long-string cases survive conversion without corruption.
8. Failures do not leave partial JSON on stdout.

## Validation Matrix

| Requirement | Validation target | Planned check |
|-------------|-------------------|---------------|
| HEAD-01 | Valid JSON selected-HDU stdout | `make -C src && ./src/fits2json 'testdata/IRPH0189.HDR[0]' | python3 -c 'import json,sys; json.load(sys.stdin)'` |
| HEAD-04 | Ordered `cards` schema replaces raw card dump | Smoke script asserts top-level keys and `cards` list shape |
| HEAD-05 | Comments preserved where present | Smoke script asserts representative card objects retain `comment` fields |
| FITS-01 | Repeated COMMENT preserved | Smoke script filters `cards` by `keyword == "COMMENT"` and checks order/count |
| FITS-02 | Repeated HISTORY preserved | Smoke script filters `cards` by `keyword == "HISTORY"` and checks order/count |
| FITS-03 | Header order deterministic | Smoke script compares keyword sequence for known fixture slices |
| FITS-04 | Long-string and HIERARCH survive correctly | Synthetic CFITSIO-generated edge fixture plus smoke assertions |

## Fixture Strategy

- Existing repo fixtures under `testdata/` cover core header order and repeated commentary behavior.
- A synthetic fixture generated during execution is required to cover the long-string/`CONTINUE`/HIERARCH gap noted in Phase 2 research.
- Validation must document that selectorless whole-file behavior is intentionally out of scope for this phase and must not be silently redefined.

## Execution Gate

Phase 2 execution is not complete unless this command passes:

`make -C src && ./test/phase2_make_edge_fixture testdata/phase2-edge.fits && python3 test/phase2_selected_hdu_smoke.py`

## Notes

- The plan should stay inside the current repo toolchain: `make`, `gcc`, `python3`, and CFITSIO.
- Validation is allowed to add repo-local test assets, but not a new test framework.
