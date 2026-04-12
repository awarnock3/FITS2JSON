---
phase: 02-header-modeling-for-selected-hdu
verified: 2026-04-12T16:33:58Z
status: passed
score: 7/7 must-haves verified
overrides_applied: 0
---

# Phase 2: Header Modeling for Selected HDU Verification Report

**Phase Goal:** Users can convert a selected HDU into accurate structured JSON without losing FITS header semantics.  
**Verified:** 2026-04-12T16:33:58Z  
**Status:** passed  
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | User can convert a selected HDU and receive valid JSON on stdout. | ✓ VERIFIED | Required gate passed: `make -C src && ./test/phase2_make_edge_fixture testdata/phase2-edge.fits && python3 test/phase2_selected_hdu_smoke.py` exited 0. Manual sample: `./src/fits2json 'testdata/IRPH0189.HDR[0]'` parsed as JSON and reported `index=1`, `type=IMAGE_HDU`, `cards=23`. |
| 2 | Selected-HDU output uses only top-level `index`, `type`, and ordered `cards`. | ✓ VERIFIED | `emit_hdu_json` writes exactly `{"index":...,"type":...,"cards":[...]}` in `src/fits2json.c:368-452`. Smoke test enforces exact top-level keys in `test/phase2_selected_hdu_smoke.py:71-84`. |
| 3 | COMMENT and HISTORY are preserved as repeated ordered cards with no `value`. | ✓ VERIFIED | Commentary cards are handled via `keyclass == TYP_COMM_KEY` and emit comment-only cards in `src/fits2json.c:260-266`. Smoke checks reject any `value` on COMMENT/HISTORY in `test/phase2_selected_hdu_smoke.py:127-145,178-185`. Manual check on `LSPN2790.HDR[0]` returned `16 COMMENT`, `16 HISTORY`, `False` for any `value` present. |
| 4 | FITS logicals become JSON booleans; all other present FITS values remain JSON strings, with comments preserved when present. | ✓ VERIFIED | `normalize_card` maps `value_type == 'L'` to boolean and all other present values to strings in `src/fits2json.c:277-320`. Manual output showed `SIMPLE: true`, `EXTEND: true`, `BITPIX: "8"`, `OBJECT: "P/HALLEY"`. |
| 5 | Header order is preserved, folded long strings do not emit standalone CONTINUE cards, and HIERARCH survives without corruption. | ✓ VERIFIED | Order is preserved by iterating `keynum = 1..nkeys` in `read_selected_hdu_model` (`src/fits2json.c:343-363`). Physical CONTINUE cards are skipped in `src/fits2json.c:250-253`; long strings are re-read through `fits_read_key_longstr` in `src/fits2json.c:283-312`. Edge-fixture output contained `LONGSTR`, `LONG.KEY`, `BOOLKEY`, COMMENT/HISTORY entries and `False` for any `CONTINUE` keyword. |
| 6 | HIERARCH support is implemented through CFITSIO APIs. | ✓ VERIFIED | Plan-required CFITSIO path is present in `src/fits2json.c:238-245,268-312`; synthetic fixture writes `HIERARCH LONG.KEY` in `test/phase2_make_edge_fixture.c:29-34`; smoke test verifies the emitted key/value in `test/phase2_selected_hdu_smoke.py:164-172`. |
| 7 | Phase 2 requires an explicit selector, keeping whole-file JSON deferred, and failures do not emit partial stdout. | ✓ VERIFIED | Selectorless invocation is rejected in `src/fits2json.c:476-507` and smoke-tested in `test/phase2_selected_hdu_smoke.py:50-58`. JSON emission happens only after `fits_close_file` succeeds in `src/fits2json.c:486-495`. Manual checks: selectorless call returned `rc=2` with stderr guidance and no stdout; missing file returned `rc=104`, `stdout_len=0`. |

**Score:** 7/7 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `src/fits2json.c` | single-file HDU/card model, CFITSIO normalization helpers, JSON emitter | ✓ VERIFIED | Exists, substantive (525 lines), wired through `main`, uses `fits_get_hdu_type`, `fits_read_keyn`, `fits_read_record`, `fits_get_keyclass`, `fits_read_key_longstr`, and emits JSON only after close. |
| `test/phase2_selected_hdu_smoke.py` | automated selected-HDU JSON regression checks | ✓ VERIFIED | Exists, substantive, and used by the required verification command. Covers selectorless rejection, JSON shape, COMMENT/HISTORY behavior, CONTINUE suppression, long-string/HIERARCH edge case. |
| `test/phase2_make_edge_fixture.c` | reproducible CFITSIO-generated long-string/HIERARCH fixture | ✓ VERIFIED | Exists, substantive, and used by the required verification command to generate `testdata/phase2-edge.fits` with BOOL, LONGSTR, HIERARCH, COMMENT, and HISTORY records. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `src/fits2json.c` | CFITSIO current HDU selection | `main -> read_selected_hdu_model` | ✓ WIRED | `main` opens selected FITS target, enforces selector rules, and passes current HDU into model read path (`src/fits2json.c:471-484`). |
| `src/fits2json.c` | logical card normalization | `fits_read_keyn + fits_read_record + fits_get_keyclass + fits_read_key_longstr` | ✓ WIRED | Normalization path present in `src/fits2json.c:225-320`. |
| `src/fits2json.c` | stdout | `emit_hdu_json` only after `fits_close_file` succeeds | ✓ WIRED | Close-then-emit sequence implemented in `src/fits2json.c:486-495`. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `src/fits2json.c` | `model.cards` | `read_selected_hdu_model` → `normalize_card` → CFITSIO reads from selected FITS HDU (`fits_read_record`, `fits_read_keyn`, `fits_read_key_longstr`) | Yes — manual outputs show real header content from repo fixtures and synthetic edge fixture | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Full Phase 2 gate passes | `make -C src && ./test/phase2_make_edge_fixture testdata/phase2-edge.fits && python3 test/phase2_selected_hdu_smoke.py` | Exit 0 | ✓ PASS |
| Selected HDU emits expected JSON shape | `./src/fits2json 'testdata/IRPH0189.HDR[0]' \| python3 -c '...'` | Printed `1 IMAGE_HDU 23` and first cards `SIMPLE/BITPIX/NAXIS/EXTEND/OBJECT` | ✓ PASS |
| Edge fixture preserves long-string/HIERARCH and suppresses CONTINUE | `./src/fits2json 'testdata/phase2-edge.fits[0]' \| python3 -c '...'` | LONGSTR/HIERARCH/BOOLKEY present; `CONTINUE` absent (`False`) | ✓ PASS |
| Failure paths avoid stdout pollution | selectorless and missing-file checks | Selectorless `rc=2`, missing file `rc=104`, both with `stdout_len=0` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| HEAD-01 | `02-01-PLAN.md` | User can convert FITS header metadata to valid JSON on stdout | ✓ SATISFIED | Required verification path passed; JSON parses for selected HDUs. |
| HEAD-04 | `02-01-PLAN.md` | User can receive structured keyword output for each HDU instead of raw 80-character header cards | ✓ SATISFIED | Top-level output is `index/type/cards`; cards are structured objects. |
| HEAD-05 | `02-01-PLAN.md` | User can receive keyword comments alongside parsed values where FITS provides them | ✓ SATISFIED | `comment` fields are emitted when present; verified in smoke tests and manual samples. |
| FITS-01 | `02-01-PLAN.md` | User can preserve repeated COMMENT records as arrays within each HDU | ✓ SATISFIED | COMMENT records remain repeated ordered `cards` entries; counts and sample text verified. |
| FITS-02 | `02-01-PLAN.md` | User can preserve repeated HISTORY records as arrays within each HDU | ✓ SATISFIED | HISTORY records remain repeated ordered `cards` entries; counts and sample text verified. |
| FITS-03 | `02-01-PLAN.md` | User can receive deterministic output that preserves original header record order | ✓ SATISFIED | Physical key iteration in order; smoke check confirms known prefix ordering. |
| FITS-04 | `02-01-PLAN.md` | User can convert headers without corrupting long-string and extended-keyword records | ✓ SATISFIED | Synthetic CFITSIO fixture plus smoke assertions verify LONGSTR folding and HIERARCH output. |

**Orphaned requirements:** None. All Phase 2 requirements mapped in `REQUIREMENTS.md` are claimed by `02-01-PLAN.md`.

### Anti-Patterns Found

No blocker or warning-level stub patterns detected in `src/fits2json.c`, `test/phase2_make_edge_fixture.c`, `test/phase2_selected_hdu_smoke.py`, or `.gitignore`.

### Disconfirmation Notes

- **Partial-requirement nuance:** Roadmap wording says “parsed values,” but the implemented and plan-locked policy is intentionally conservative: logicals become booleans, all other present FITS values remain strings. This matches the plan and user verification target, so it is not a gap.
- **Misleading test note:** `test/phase2_selected_hdu_smoke.py` claims order coverage, but `assert_lspn2790()` checks counts/text presence more than exact full-card ordering. Order is still supported by stronger code evidence: `read_selected_hdu_model()` iterates physical keys sequentially.
- **Uncovered error path:** No automated test forces allocator failure or write failure during `emit_hdu_json()`. The code has guards for both, but those paths are untested.

### Gaps Summary

No blocking gaps found. The code, wiring, data flow, and required verification path all support the Phase 2 goal: selected-HDU conversion now emits accurate structured JSON while preserving header order, repeated commentary semantics, long-string folding, HIERARCH handling, and Phase 2’s explicit-selector boundary.

---

_Verified: 2026-04-12T16:33:58Z_  
_Verifier: the agent (gsd-verifier)_
