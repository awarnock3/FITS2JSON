---
phase: 03-whole-file-json-emission
verified: 2026-04-12T19:14:06Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
---

# Phase 3: Whole-File JSON Emission Verification Report

**Phase Goal:** Users can convert an entire FITS file into one JSON document that is safe to pipe into downstream tools.  
**Verified:** 2026-04-12T19:14:06Z  
**Status:** passed  
**Re-verification:** No - initial verification

## Goal Achievement

Phase 3 passes. The current code and repo behavior satisfy the locked Phase 3 contract.

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | User can omit the extension selector and receive one top-level JSON array containing every HDU in file order. | ✓ VERIFIED | `read_whole_file_document()` counts HDUs with `fits_get_num_hdus` and traverses `1..N` with `fits_movabs_hdu`, reusing `read_selected_hdu_model()` (`src/fits2json.c:410-445`). Manual probe after build returned `type=list len=2 indexes=[1, 2]` for `IRPH0189.HDR` and `type=list len=1 indexes=[1]` for `LSPN2790.HDR`. |
| 2 | Each selectorless array element uses the existing Phase 2 HDU object contract exactly: `index`, `type`, `cards`, with no default file-level metadata. | ✓ VERIFIED | Object emission is reused through `emit_hdu_json_object()` and array emission only wraps those objects with `[` `]` (`src/fits2json.c:447-578`). Manual probe reported `first_keys=['cards', 'index', 'type']`; no top-level metadata wrapper exists. `test/phase3_whole_file_smoke.py` asserts selectorless elements exactly equal explicit `[0]` / `[1]` outputs (`test/phase3_whole_file_smoke.py:48-76`). |
| 3 | User can still pass an explicit selector and receive one HDU object, not an array. | ✓ VERIFIED | `main()` branches on selector presence and keeps explicit mode on `read_selected_hdu_model()` + `emit_hdu_json()` (`src/fits2json.c:604-627`). Manual probe returned `type=dict keys=['cards', 'index', 'type']` for both `IRPH0189.HDR[0]` and `IRPH0189.HDR[1]`. Phase 2 smoke still enforces exact top-level object keys in `assert_hdu_shape()` and only runs explicit-selector cases in `main()` (`test/phase2_selected_hdu_smoke.py:61-74,196-206`). |
| 4 | Successful selectorless and explicit runs write only JSON to stdout with no success diagnostics on stderr. | ✓ VERIFIED | `main()` closes the FITS handle before any success-path emission, then emits either one object or one array (`src/fits2json.c:615-627`). `test/phase3_whole_file_smoke.py` rejects any non-empty success stderr and parses stdout with `json.loads()` (`test/phase3_whole_file_smoke.py:32-45`). Manual probe showed `rc=0 stderr_len=0` for selectorless and explicit IRPH0189/LSPN2790 runs. |
| 5 | Repo-local smoke covers selectorless array behavior and explicit-vs-selectorless parity using existing fixtures, and any remaining `BINARY_TBL` smoke gap is stated explicitly rather than claimed as covered. | ✓ VERIFIED | Phase gate passed: `make -C src fits2json && python3 test/phase2_selected_hdu_smoke.py --cases core && python3 test/phase3_whole_file_smoke.py`. The Phase 3 smoke file explicitly says current repo-local smoke does not exercise `BINARY_TBL` (`test/phase3_whole_file_smoke.py:3-8`), and the execution summary repeats that limitation (`03-01-SUMMARY.md:60-63`). |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `src/fits2json.c` | Selector branch, whole-file document container, absolute HDU traversal, and array emission | ✓ VERIFIED | Exists and substantive. `read_whole_file_document()` implements selectorless traversal, `emit_hdu_json_object()` preserves the Phase 2 object contract, `emit_document_json()` emits the array, and `main()` wires explicit vs selectorless dispatch. |
| `test/phase3_whole_file_smoke.py` | Repo-local smoke coverage for selectorless array output and explicit-vs-selectorless parity | ✓ VERIFIED | Exists and substantive. Uses the built binary, enforces empty success stderr, parses stdout as JSON, checks selectorless list shape, parity with explicit outputs, and 1-HDU array behavior. |
| `test/phase2_selected_hdu_smoke.py` | Explicit-selector contract regression coverage without Phase 2 selectorless rejection guard | ✓ VERIFIED | Exists and substantive. Still enforces the Phase 2 explicit object shape and explicit HDU semantics, and its `--cases core` path is part of the required Phase 3 gate. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `src/fits2json.c` | `read_selected_hdu_model` | selectorless traversal loop | ✓ WIRED | `read_whole_file_document()` calls `fits_movabs_hdu()` then `read_selected_hdu_model()` for each HDU (`src/fits2json.c:420-437`). |
| `src/fits2json.c` | `stdout` | close FITS handle before any selectorless JSON emission | ✓ WIRED | `fits_close_file()` runs before the success-path call to `emit_document_json()` or `emit_hdu_json()` (`src/fits2json.c:615-627`). |
| `test/phase3_whole_file_smoke.py` | `src/fits2json` | selectorless IRPH0189/LSPN2790 smoke runs parsed with `json.loads` | ✓ WIRED | `load_json()` shells out to the binary, requires empty stderr, and parses stdout with `json.loads()`; the smoke cases invoke both selectorless and explicit IRPH0189/LSPN2790 inputs (`test/phase3_whole_file_smoke.py:32-76`). |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `src/fits2json.c` | `document.hdus` | `read_whole_file_document()` -> `fits_get_num_hdus` / `fits_movabs_hdu` -> `read_selected_hdu_model()` -> CFITSIO header reads | Yes - manual runs produced real FITS-derived objects: IRPH0189 selectorless output had 2 HDUs (`IMAGE_HDU`, `ASCII_TBL`), and LSPN2790 selectorless output had 1 HDU with 89 cards | ✓ FLOWING |
| `test/phase3_whole_file_smoke.py` | `selectorless`, `explicit0`, `explicit1` | subprocess calls to `src/fits2json`, then `json.loads(proc.stdout)` | Yes - gate passed and manual parity probe confirmed `selectorless_irph_matches_explicit=True` and `selectorless_lspn_matches_explicit=True` | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Phase 3 execution gate | `make -C src fits2json && python3 test/phase2_selected_hdu_smoke.py --cases core && python3 test/phase3_whole_file_smoke.py` | Exit 0 | ✓ PASS |
| Selectorless multi-HDU output shape | Manual subprocess probe over `./src/fits2json testdata/IRPH0189.HDR` | `type=list len=2 indexes=[1, 2]`, `stderr_len=0` | ✓ PASS |
| Explicit-selector contract preserved | Manual subprocess probe over `./src/fits2json 'testdata/IRPH0189.HDR[0]'` and `[1]` | Both returned `type=dict keys=['cards', 'index', 'type']`, `stderr_len=0` | ✓ PASS |
| Selectorless/explicit parity | Manual subprocess probe over IRPH0189 and LSPN2790 selectorless vs explicit runs | `selectorless_irph_matches_explicit=True`; `selectorless_lspn_matches_explicit=True` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| HEAD-02 | `03-01-PLAN.md` | User can receive one JSON document containing all HDUs when no extension is specified | ✓ SATISFIED | Selectorless mode emits a top-level array after absolute HDU traversal; gate and manual probes confirmed correct 2-HDU and 1-HDU outputs. |
| CLI-01 | `03-01-PLAN.md` | User can pipe successful command output directly into JSON-consuming shell tools without non-JSON text mixed into stdout | ✓ SATISFIED | Success path emits only JSON after close; phase smoke enforces `json.loads(stdout)` and empty `stderr` on success. |

**Orphaned requirements:** None. `REQUIREMENTS.md` maps only `HEAD-02` and `CLI-01` to Phase 3, and both are claimed by `03-01-PLAN.md`.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| - | - | None detected in `src/fits2json.c`, `test/phase2_selected_hdu_smoke.py`, `test/phase3_whole_file_smoke.py`, or `test/phase2_make_edge_fixture.c` | - | No TODO/FIXME markers, placeholder output, empty implementations, or stubbed success paths were found in the Phase 3 files. |

### Disconfirmation Notes

- **Partial-requirement nuance:** Smoke coverage is solid for selectorless array behavior and parity, but it still does not exercise `BINARY_TBL`. This is not being hidden; it is called out explicitly in both the Phase 3 smoke header and the execution summary.
- **Misleading-test note:** `test/phase3_whole_file_smoke.py` proves selectorless elements equal explicit outputs, but it relies on Phase 2 smoke to independently guard the exact explicit object schema. That dependence is acceptable here because the required gate runs both scripts together.
- **Uncovered error path:** No automated test forces a failure in the middle of whole-file traversal or simulates memory/write failure after some HDUs are modeled. The code has cleanup/error branches for those cases, but they remain untested in-repo.

### Human Verification Required

None.

### Gaps Summary

No blocking gaps found. Phase 3 passes: selectorless mode now returns one top-level JSON array of Phase 2 HDU objects in file order, explicit selector mode remains a single HDU object, and successful runs keep stdout pure JSON with no success stderr noise. Repo-local smoke still does not exercise `BINARY_TBL`, and the repository correctly states that limitation instead of claiming coverage it does not have.

---

_Verified: 2026-04-12T19:14:06Z_  
_Verifier: the agent (gsd-verifier)_
