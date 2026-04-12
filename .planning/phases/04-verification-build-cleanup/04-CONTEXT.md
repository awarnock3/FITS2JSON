# Phase 4: Verification & Build Cleanup - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Harden `fits2json` so the existing single-C / CFITSIO CLI has a repeatable build-and-test path, deterministic failure semantics, and safe cleanup behavior. This phase is about automation reliability and failure contracts; it must not redesign the Phase 2/3 JSON output shapes.

</domain>

<decisions>
## Implementation Decisions

### Verification command surface
- **D-01:** `make -C src test` is the canonical verification entry point for automation.
- **D-02:** The `test` target should build the CLI and run all repo-local smoke checks by default.
- **D-03:** The default verification path should regenerate the synthetic edge fixture and include error-path checks, not just happy-path JSON smoke tests.

### Failure contract
- **D-04:** On failure, keep stdout empty and write diagnostics to stderr only.
- **D-05:** Failures should include a short `fits2json:` message on stderr, plus CFITSIO details when they are available and relevant.
- **D-06:** Lock a simple stable exit-code policy: `2` for usage/invalid invocation, `1` for conversion/build/test failures.

### Build portability
- **D-07:** `src/Makefile` should prefer `pkg-config cfitsio` for dependency discovery.
- **D-08:** The build must still allow standard make-variable overrides such as `CPPFLAGS` and `LDFLAGS`.
- **D-09:** If CFITSIO cannot be found, the build should fail early with a clear prerequisite message.

### Cleanup behavior
- **D-10:** `make -C src clean` should remove build outputs and test-generated artifacts only.
- **D-11:** Cleanup should cover the built binary, object files, compiled helper binaries, generated FITS fixtures, and caches created by verification.
- **D-12:** Cleanup must never delete checked-in files, even when those files are reproducible.

### the agent's Discretion
- Exact Makefile target/helper layout needed to implement `test` and `clean` cleanly within `src/Makefile`
- Exact wording and helper boundaries for build-time prerequisite errors and runtime/test failure messages, as long as the stderr/stdout and exit-code contract above is preserved
- Exact set of error-path smoke cases needed to prove deterministic failure behavior without expanding scope beyond the existing CLI/build path

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` — Phase 4 goal, requirement mapping, and success criteria
- `.planning/PROJECT.md` — locked project constraints, especially the single-C-program and CFITSIO scope
- `.planning/REQUIREMENTS.md` — Phase 4 requirements `CLI-02`, `CLI-03`, and `BLD-01`
- `.planning/STATE.md` — current milestone state after Phase 3 completion

### Prior-phase contracts to preserve
- `.planning/phases/01-seam-extraction-rename/01-CONTEXT.md` — keep the build centered on `src/Makefile` and the single executable `fits2json`
- `.planning/phases/02-header-modeling-for-selected-hdu/02-CONTEXT.md` — preserve stdout as the JSON channel and the selected-HDU object contract
- `.planning/phases/03-whole-file-json-emission/03-CONTEXT.md` — preserve pure-JSON stdout and the selectorless-array vs explicit-object split
- `.planning/phases/03-whole-file-json-emission/03-VERIFICATION.md` — current evidence for the stable Phase 3 runtime/output behavior that Phase 4 must harden, not redesign

### Existing implementation and build/test surfaces
- `src/Makefile` — current build entry point, hard-coded CFITSIO paths, and cleanup behavior to be corrected
- `src/fits2json.c` — current runtime error handling, usage path, stdout/stderr split, and exit-code behavior
- `test/phase2_selected_hdu_smoke.py` — explicit-selector regression harness that should be wired into repeatable verification
- `test/phase3_whole_file_smoke.py` — selectorless whole-file smoke harness that should be wired into repeatable verification
- `test/phase2_make_edge_fixture.c` — helper used to generate the synthetic FITS fixture needed by the smoke suite

### Codebase guidance
- `.planning/codebase/CONCERNS.md` — documented Makefile brittleness, cleanup drift, and verification gaps directly targeted by Phase 4
- `.planning/codebase/TESTING.md` — existing test-fixture/testing patterns and current lack of a real automated `test` entry point
- `.planning/codebase/CONVENTIONS.md` — repository conventions around `src/Makefile`, stderr usage, and manual verification patterns

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/Makefile` already owns the build entry point and should become the canonical home for repeatable `test` and `clean` automation
- `test/phase2_selected_hdu_smoke.py` already covers the explicit-selector contract and can be promoted into the standard `make -C src test` flow
- `test/phase3_whole_file_smoke.py` already covers selectorless whole-file parity and should be part of the same standard verification path
- `test/phase2_make_edge_fixture.c` already gives the repo a reproducible way to generate the synthetic long-string/HIERARCH fixture needed for end-to-end smoke checks

### Established Patterns
- Successful CLI output is pure JSON on stdout; failures are expected to surface through stderr
- The project remains a single-file procedural C CLI built from `src/Makefile`
- Verification relies on real FITS fixtures under `testdata/`, not mocked parsing layers

### Integration Points
- Phase 4 build work connects at `src/Makefile` target definitions, dependency discovery, helper compilation, and cleanup rules
- Phase 4 runtime hardening connects at `src/fits2json.c` usage/error branches and any logic that could leak partial stdout on failure
- Phase 4 verification work connects by wiring the existing smoke scripts and synthetic fixture generator into the canonical Makefile test path

</code_context>

<specifics>
## Specific Ideas

- The automation contract should feel like a standard CLI project: `make -C src` builds, `make -C src test` verifies, and `make -C src clean` resets generated state safely.
- The repo should stop depending on one machine's `/usr/local` layout as the default CFITSIO discovery mechanism.
- Error behavior should be simple for scripts: no stdout on failure, short human-readable stderr, and stable exit categories.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-verification-build-cleanup*
*Context gathered: 2026-04-12*
