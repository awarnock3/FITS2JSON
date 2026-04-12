---
phase: 04-verification-build-cleanup
verified: 2026-04-12T20:29:05Z
status: passed
score: 8/8 must-haves verified
overrides_applied: 0
---

# Phase 4: Verification & Build Cleanup Verification Report

**Phase Goal:** Users can build and automate `fits2json` with repeatable results and deterministic failure behavior.  
**Verified:** 2026-04-12T20:29:05Z  
**Status:** passed  
**Re-verification:** Yes - the earlier forced-rebuild gap was rechecked explicitly and is now closed.

## Goal Achievement

Phase 4 passes. The current code and repo behavior satisfy the Phase 4 contract, including the previously-failing requirement that repeated `make -C src test` invocations force a rebuild of `src/fits2json`.

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | User can run `make -C src` and get one executable named `src/fits2json`. | ✓ VERIFIED | `make -C src clean && make -C src` passed; `find src -maxdepth 1 -type f -executable` returned only `fits2json`. Build target is `all: fits2json` in `src/Makefile:21-36`. |
| 2 | User can run `make -C src test` and it rebuilds the CLI on every invocation. | ✓ VERIFIED | `src/Makefile:49-55` routes `test` through `rebuild-fits2json`, which runs `$(MAKE) --always-make fits2json`. Explicit recheck: second `make -C src test` still reran compile and link commands, and `src/fits2json` mtime advanced from `1776025660` to `1776025662`. |
| 3 | `make -C src test` regenerates the synthetic edge fixture every run and executes repo-local success and error-path smoke checks. | ✓ VERIFIED | `$(EDGE_FIXTURE): force $(HELPER)` in `src/Makefile:46-47` forces regeneration every run; fixture mtime advanced from `1776025660` to `1776025662` on the second test run. `test:` runs `phase2_selected_hdu_smoke.py`, `phase3_whole_file_smoke.py`, and `phase4_cli_contract_smoke.py` (`src/Makefile:52-55`). Full gate passed. |
| 4 | Usage failures return `2`; pre-emission conversion/open/selector/model failures return `1`. | ✓ VERIFIED | `fail_usage()` returns `2` and `fail_cfitsio()` / `fail_app()` return `1` (`src/fits2json.c:57-75`). Direct probes: `./src/fits2json` → `rc=2`; `./src/fits2json testdata/does-not-exist.fits` → `rc=1`; `./src/fits2json 'testdata/IRPH0189.HDR[NOPE]'` → `rc=1`. |
| 5 | Usage/open/selector/model failures keep stdout empty, write diagnostics to stderr only, and include a short `fits2json:` prefix plus CFITSIO details when relevant. | ✓ VERIFIED | `main()` emits JSON only after successful read/close (`src/fits2json.c:643-648`), so pre-emission failures never write stdout. `fail_usage()`, `fail_cfitsio()`, and `fail_app()` all write to `stderr` (`src/fits2json.c:57-75`). Direct probes showed `stdout_len=0` for usage, missing-file, and invalid-selector cases; CFITSIO-backed failures included both `fits2json:` and `FITSIO status = ...`. |
| 6 | Repeated success and pre-emission failure runs are deterministic. | ✓ VERIFIED | `test/phase4_cli_contract_smoke.py:50-95` compares `(returncode, stdout, stderr)` across repeated runs for success, missing-file, invalid-selector, and generated-fixture cases. Direct probes also returned `repeat_success_equal=True` and `repeat_failure_equal=True`. |
| 7 | Detectable stdout write failures return `1` with stderr diagnostics; the empty-stdout guarantee is scoped to failures detected before emission begins. | ✓ VERIFIED | `signal(SIGPIPE, SIG_IGN)` plus `APP_STATUS_WRITE` handling in `src/fits2json.c:619, 662-663` routes write failures into `fail_app("failed while writing JSON output")`. `test/phase4_cli_contract_smoke.py:98-121` closes the read end before execution and asserts `rc == 1` with a `fits2json:` stderr prefix. Direct broken-pipe probe matched that behavior. |
| 8 | User can run `make -C src clean` and remove generated outputs without deleting checked-in files. | ✓ VERIFIED | `clean` removes only `$(OBJS)`, `fits2json`, `$(HELPER)`, `$(EDGE_FIXTURE)`, and `../test/__pycache__` (`src/Makefile:57-59`). Full gate assertions confirmed generated artifacts were removed while checked-in files like `test/phase2_make_edge_fixture.c`, `test/phase2_selected_hdu_smoke.py`, `test/phase3_whole_file_smoke.py`, and `test/phase4_cli_contract_smoke.py` remained. |

**Score:** 8/8 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `src/Makefile` | Canonical build/test/clean workflow with forced CLI rebuild, fixture regeneration, prerequisite checks, and safe cleanup | ✓ VERIFIED | Substantive and wired. Contains `check-cfitsio`, `check-python`, `rebuild-fits2json`, forced `$(EDGE_FIXTURE)`, `test`, and explicit `clean` (`src/Makefile:18-59`). |
| `src/fits2json.c` | Centralized runtime failure mapping with stable exit codes and stderr-only diagnostics | ✓ VERIFIED | Substantive and wired. `fail_usage`, `fail_cfitsio`, `fail_app`, SIGPIPE handling, deferred emission, and write-failure mapping are implemented in one path (`src/fits2json.c:57-75, 601-670`). |
| `test/phase4_cli_contract_smoke.py` | Error-path, repeatability, and broken-pipe contract coverage | ✓ VERIFIED | Substantive and wired. Asserts exit codes, empty stdout for pre-emission failures, repeatability, and broken-pipe handling (`test/phase4_cli_contract_smoke.py:36-152`). Invoked by `make -C src test`. |
| `test/phase2_selected_hdu_smoke.py` | Success-path regression coverage for selected HDUs and generated edge fixture | ✓ VERIFIED | Substantive and wired. Validates selected-HDU shape and generated edge fixture behavior (`test/phase2_selected_hdu_smoke.py:178-214`). Invoked by `make -C src test`. |
| `test/phase3_whole_file_smoke.py` | Success-path regression coverage for selectorless whole-file output | ✓ VERIFIED | Substantive and wired. Validates selectorless array parity and empty success stderr (`test/phase3_whole_file_smoke.py:32-90`). Invoked by `make -C src test`. |
| `test/phase2_make_edge_fixture.c` | Helper that regenerates the synthetic edge FITS fixture | ✓ VERIFIED | Substantive and wired. Creates the synthetic fixture with long-string/HIERARCH/comment/history coverage (`test/phase2_make_edge_fixture.c:7-55`) and is compiled/run from `src/Makefile:41-47`. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `src/Makefile` | `src/fits2json` | `test -> rebuild-fits2json -> $(MAKE) --always-make fits2json` | ✓ WIRED | `src/Makefile:49-55`. Re-verification confirmed second `make -C src test` recompiled and relinked the CLI. |
| `src/Makefile` | `test/phase2_make_edge_fixture.c` | helper compilation and `$(EDGE_FIXTURE): force $(HELPER)` | ✓ WIRED | `src/Makefile:41-47`. Helper binary is built locally and fixture regeneration reruns every test invocation. |
| `src/Makefile` | `test/phase2_selected_hdu_smoke.py`, `test/phase3_whole_file_smoke.py`, `test/phase4_cli_contract_smoke.py` | canonical `test` target | ✓ WIRED | `src/Makefile:52-55`. Full `make -C src test` executed all three scripts successfully. |
| `src/fits2json.c` | `stderr` | centralized failure helpers | ✓ WIRED | Manual verification of `fail_usage`, `fail_cfitsio`, and `fail_app` in `src/fits2json.c:57-75` plus main-path dispatch in `src/fits2json.c:654-667`. Direct probes confirmed stderr-only diagnostics on failures. |
| `src/Makefile` | generated artifacts | explicit `clean` target list | ✓ WIRED | `src/Makefile:57-59`. Post-clean assertions showed generated outputs removed and checked-in files preserved. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `src/fits2json.c` | `model` / `document` | `fits_open_file` -> `read_selected_hdu_model` / `read_whole_file_document` -> `emit_hdu_json` / `emit_document_json` | Yes | ✓ FLOWING |
| `test/phase4_cli_contract_smoke.py` | `proc.returncode`, `proc.stdout`, `proc.stderr` | real subprocess calls to repo-local `src/fits2json` | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Full Phase 4 execution gate | `make -C src clean && make -C src test && make -C src clean` plus post-clean assertions | Exit 0; CLI built; helper compiled; fixture generated; Phase 2/3/4 smoke scripts passed; generated artifacts removed | ✓ PASS |
| Prior rebuild gap recheck | two consecutive `make -C src test` runs | Second run still recompiled/relinked `fits2json`; binary mtime `1776025660 -> 1776025662` | ✓ PASS |
| Fixture regeneration recheck | two consecutive `make -C src test` runs | `testdata/phase2-edge.fits` mtime `1776025660 -> 1776025662` | ✓ PASS |
| Usage / open / selector failures | direct CLI probes | Usage `rc=2`, missing-file `rc=1`, invalid-selector `rc=1`; all had empty stdout | ✓ PASS |
| Broken-pipe / write failure | Python broken-pipe probe from `test/phase4_cli_contract_smoke.py` and manual subprocess probe | `rc=1`; stderr begins with `fits2json:` | ✓ PASS |
| Missing CFITSIO discovery | `make -C src fits2json PKG_CONFIG=false CFITSIO_CFLAGS= CFITSIO_LIBS=` | Clear early `CFITSIO not found...` message before compile/link noise; overall `make` rc was `2` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| `CLI-02` | `04-01-PLAN.md` | User receives diagnostics on stderr and a non-zero exit code when the FITS file cannot be opened or converted | ✓ SATISFIED | `src/fits2json.c:57-75, 621-623, 654-667`; direct missing-file and invalid-selector probes; `test/phase4_cli_contract_smoke.py:65-82`. |
| `CLI-03` | `04-01-PLAN.md` | User can rely on deterministic output shape and failure behavior across repeated runs | ✓ SATISFIED | `test/phase4_cli_contract_smoke.py:50-95`; direct repeat probes returned identical `(rc, stdout, stderr)` for success and failure. |
| `BLD-01` | `04-01-PLAN.md` | User can build the tool from `src/Makefile` as a single C program named `fits2json` | ✓ SATISFIED | `src/Makefile:21-36`; `make -C src clean && make -C src` passed; only executable in `src/` after build was `fits2json`. |

**Orphaned requirements:** None. `REQUIREMENTS.md` maps only `CLI-02`, `CLI-03`, and `BLD-01` to Phase 4, and all are claimed by `04-01-PLAN.md`.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| - | - | None detected in the inspected Phase 4 files | - | No TODO/FIXME markers, placeholder implementations, empty handlers, or hardcoded hollow outputs were found in `src/Makefile`, `src/fits2json.c`, `test/phase4_cli_contract_smoke.py`, `test/phase2_selected_hdu_smoke.py`, `test/phase3_whole_file_smoke.py`, or `test/phase2_make_edge_fixture.c`. |

### Disconfirmation Notes

- **Partial-requirement nuance:** The stable `0/1/2` exit-code contract is verified on the `fits2json` CLI itself. The explicit CFITSIO prerequisite probe exits through GNU make with overall rc `2` after printing the expected readable prerequisite message.
- **Misleading-test note:** `python3 test/phase4_cli_contract_smoke.py` proves CLI repeatability, but by itself it does **not** prove that `make -C src test` forces a rebuild. That earlier gap was rechecked separately with a second `make -C src test` run, command-log inspection, and mtime changes.
- **Uncovered error path:** No repo-local test forces `APP_STATUS_MEMORY` or a close/read failure after partial in-memory modeling. Those branches exist, but they are not directly exercised.

### Human Verification Required

None.

### Gaps Summary

No blocking gaps found. Phase 4 passes.

The earlier verification gap is closed: repeated `make -C src test` runs now force a rebuild of `src/fits2json`, regenerate `testdata/phase2-edge.fits`, and rerun the repo-local smoke suite. The CLI failure contract is deterministic and consistent with the phase goal, and `make -C src clean` removes only generated artifacts.

---

_Verified: 2026-04-12T20:29:05Z_  
_Verifier: the agent (gsd-verifier)_
