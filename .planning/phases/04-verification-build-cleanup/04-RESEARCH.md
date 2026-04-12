# Phase 4: Verification & Build Cleanup - Research

**Researched:** 2026-04-12  
**Domain:** Makefile hardening, CFITSIO discovery, CLI failure contract, repo-local verification  
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Verification command surface
- **D-01:** `make -C src test` is the canonical verification entry point for automation.
- **D-02:** The `test` target should build the CLI and run all repo-local smoke checks by default.
- **D-03:** The default verification path should regenerate the synthetic edge fixture and include error-path checks, not just happy-path JSON smoke tests.

#### Failure contract
- **D-05:** On usage and other failures detected before emission begins, keep stdout empty and write diagnostics to stderr only.
- **D-06:** Detectable stdout write or broken-pipe failures after emission begins should still surface a short `fits2json:` stderr diagnostic and exit `1`; they do not retroactively promise zero-byte stdout once bytes were already accepted downstream.
- **D-07:** Failures should include a short `fits2json:` message on stderr, plus CFITSIO details when they are available and relevant.
- **D-08:** Lock a simple stable exit-code policy: `2` for usage/invalid invocation, `1` for conversion/build/test failures.

#### Build portability
- **D-09:** `src/Makefile` should prefer `pkg-config cfitsio` for dependency discovery.
- **D-10:** The build must still allow standard make-variable overrides such as `CPPFLAGS` and `LDFLAGS`.
- **D-11:** If CFITSIO cannot be found, the build should fail early with a clear prerequisite message.

#### Cleanup behavior
- **D-12:** `make -C src clean` should remove build outputs and test-generated artifacts only.
- **D-13:** Cleanup should cover the built binary, object files, compiled helper binaries, generated FITS fixtures, and caches created by verification.
- **D-14:** Cleanup must never delete checked-in files, even when those files are reproducible.

### the agent's Discretion
- Exact Makefile target/helper layout needed to implement `test` and `clean` cleanly within `src/Makefile`
- Exact wording and helper boundaries for build-time prerequisite errors and runtime/test failure messages, as long as the stderr/stdout and exit-code contract above is preserved
- Exact set of error-path smoke cases needed to prove deterministic failure behavior without expanding scope beyond the existing CLI/build path

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CLI-02 | User receives diagnostics on stderr and a non-zero exit code when the FITS file cannot be opened or converted | Centralized failure helper, stable exit-code mapping, stderr-only error smoke cases |
| CLI-03 | User can rely on deterministic output shape and failure behavior across repeated runs | Reuse existing happy-path smokes, add repeated-run success/failure assertions, regenerate edge fixture every `make test` |
| BLD-01 | User can build the tool from `src/Makefile` as a single C program named `fits2json` | Harden `src/Makefile` around `all`, `test`, `clean`, pkg-config discovery, explicit artifact cleanup |
</phase_requirements>

## Summary

Phase 4 is a hardening phase, not a schema phase: Phase 3 already established the JSON success path, and Phase 4 is about making build, test, cleanup, and failure behavior predictable for automation. [VERIFIED: `.planning/ROADMAP.md`; `.planning/phases/04-verification-build-cleanup/04-CONTEXT.md`]

The current repo already has a buildable single binary and passing happy-path smoke scripts, but the automation contract is incomplete: `make -C src test` does not exist, and `make -C src clean` currently removes only `src/fits2json` and `src/fits2json.o`, leaving generated verification artifacts behind. [VERIFIED: `src/Makefile`; bash `make -C src test`; bash `make -C src clean` + artifact audit; python smoke runs]

The current runtime is close to the desired failure shape for open/read failures because it builds the in-memory model before emitting JSON, so missing-file and bad-selector failures already leave stdout empty; however, it still returns raw CFITSIO status codes like `104` and `45` instead of the locked `1/2` policy, and those failures do not yet prepend a short `fits2json:` message. [VERIFIED: `src/fits2json.c` lines 594-649; bash missing-file and bad-selector probes]

**Primary recommendation:** Implement this phase around one hardened `src/Makefile` (`all`, `test`, `clean`, explicit prerequisite check) plus one centralized C error-reporting path that maps all non-usage failures to exit `1` and writes diagnostics only to stderr. [VERIFIED: `04-CONTEXT.md`; ASSUMED]

## Project Constraints (from copilot-instructions.md)

- Keep the implementation as a single C command-line program built from `src/Makefile`. [VERIFIED: `copilot-instructions.md`]
- Keep CFITSIO as the parsing dependency; do not replace it with a custom FITS parser. [VERIFIED: `copilot-instructions.md`]
- Do not introduce a wrapper script or second implementation language for the product binary. [VERIFIED: `copilot-instructions.md`]
- Keep changes aligned with the current brownfield single-binary architecture. [VERIFIED: `copilot-instructions.md`]
- Keep scope limited to FITS header metadata, not payload conversion. [VERIFIED: `copilot-instructions.md`]
- No project skills directories are present under `.github/skills/` or `.agents/skills/`. [VERIFIED: directory checks]

## Standard Stack

### Core

| Library/Tool | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| GNU Make | 4.3 [VERIFIED: bash `make --version`] | Canonical build/test/clean entry point | Repo already builds from `src/Makefile`, and GNU make documents phony recipe targets like `clean`/`test`. [VERIFIED: `src/Makefile`][CITED: https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html] |
| GCC | 13.3.0 [VERIFIED: bash `gcc --version`] | Compile the single C executable | `src/Makefile` already uses `gcc`; keeping the compiler interface stable minimizes scope. [VERIFIED: `src/Makefile`] |
| CFITSIO | 4.2.0 via `pkg-config` [VERIFIED: bash `pkg-config --modversion cfitsio`] | FITS open/read/selector handling | Locked project dependency; do not hand-roll FITS parsing. [VERIFIED: `PROJECT.md`; `src/fits2json.c`] |
| pkg-config | 1.8.1 [VERIFIED: bash `pkg-config --version`] | Discover CFITSIO compile/link flags | `pkg-config --cflags/--libs` is the standard metadata interface for library consumers. [CITED: https://people.freedesktop.org/~dbn/pkg-config-guide.html] |

### Supporting

| Library/Tool | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Python 3 | 3.12.3 [VERIFIED: bash `python3 --version`] | Run repo-local smoke/error harnesses | Existing smoke checks are already Python scripts in `test/`. [VERIFIED: `test/phase2_selected_hdu_smoke.py`; `test/phase3_whole_file_smoke.py`] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hard-coded `-I/usr/local/include -L/usr/local/lib` [VERIFIED: `src/Makefile`] | `pkg-config cfitsio` + explicit override vars | `pkg-config` is more portable; manual paths stay available through overrides when `.pc` metadata is missing. [CITED: https://people.freedesktop.org/~dbn/pkg-config-guide.html][CITED: https://www.gnu.org/software/make/manual/html_node/Overriding.html] |
| Raw CFITSIO process exit codes [VERIFIED: bash probes] | Stable app exit categories `2`/`1` | Simpler for scripts; detailed CFITSIO text stays on stderr. [VERIFIED: `04-CONTEXT.md`] |
| Recursive `make -C test` | Direct script invocation from `src/Makefile` | Repo has no `test/Makefile`; direct invocation is the minimal working shape. [VERIFIED: bash `make -C src test`; repo tree] |

**Installation / prerequisite verification:**
```bash
command -v make gcc python3 pkg-config
pkg-config --exists cfitsio
pkg-config --modversion cfitsio
pkg-config --cflags cfitsio
pkg-config --libs cfitsio
```
[VERIFIED: bash]

## Architecture Patterns

### Recommended Project Structure
```text
src/
├── Makefile                  # canonical all/test/clean entry point
└── fits2json.c               # single production CLI

test/
├── phase2_selected_hdu_smoke.py
├── phase3_whole_file_smoke.py
├── phase4_cli_contract_smoke.py   # add in this phase
└── phase2_make_edge_fixture.c

testdata/
├── *.HDR                     # checked-in fixtures
└── phase2-edge.fits          # generated fixture; never checked in
```
[VERIFIED: repo files][ASSUMED: new phase4 test filename]

### Pattern 1: Makefile owns the full verification contract
**What:** `make -C src test` should be the single entry point that checks prerequisites, builds `fits2json`, compiles the edge-fixture helper, regenerates `testdata/phase2-edge.fits`, and runs happy-path plus error-path smokes. [VERIFIED: `04-CONTEXT.md`; `test/phase2_selected_hdu_smoke.py` lines 185-203; `test/phase3_whole_file_smoke.py`][ASSUMED: exact target decomposition]

**When to use:** Always; D-01 through D-03 lock this as the canonical automation surface. [VERIFIED: `04-CONTEXT.md`]

**Example:**
```make
.PHONY: all test clean check-cfitsio
.DELETE_ON_ERROR:

CC ?= cc
CFLAGS ?= -O2 -Wall -D_POSIX_C_SOURCE=200809L
CPPFLAGS ?=
LDFLAGS ?=
LDLIBS ?=
PYTHON ?= python3
PKG_CONFIG ?= pkg-config
CFITSIO_PKG ?= cfitsio

ifeq ($(origin CFITSIO_CFLAGS), undefined)
CFITSIO_CFLAGS := $(shell $(PKG_CONFIG) --cflags $(CFITSIO_PKG) 2>/dev/null)
endif
ifeq ($(origin CFITSIO_LIBS), undefined)
CFITSIO_LIBS := $(shell $(PKG_CONFIG) --libs $(CFITSIO_PKG) 2>/dev/null)
endif

ifeq ($(strip $(CFITSIO_CFLAGS) $(CFITSIO_LIBS)),)
$(error CFITSIO not found; install the cfitsio development package or pass CFITSIO_CFLAGS=... CFITSIO_LIBS=...)
endif

CPPFLAGS += $(CFITSIO_CFLAGS)
LDLIBS += $(CFITSIO_LIBS)

all: fits2json
test: fits2json ../test/phase2_make_edge_fixture ../testdata/phase2-edge.fits
	$(PYTHON) ../test/phase2_selected_hdu_smoke.py
	$(PYTHON) ../test/phase3_whole_file_smoke.py
	$(PYTHON) ../test/phase4_cli_contract_smoke.py

clean:
	$(RM) fits2json *.o ../test/phase2_make_edge_fixture ../testdata/phase2-edge.fits
	$(RM) -r ../test/__pycache__
```
Source: synthesis from repo requirements plus GNU make docs on phony targets, command-line overrides, and `.DELETE_ON_ERROR`. [VERIFIED: `src/Makefile`; `.gitignore`; `04-CONTEXT.md`][CITED: https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html][CITED: https://www.gnu.org/software/make/manual/html_node/Overriding.html][CITED: https://www.gnu.org/software/make/manual/html_node/Errors.html]

### Pattern 2: Centralized runtime failure mapping
**What:** Keep CFITSIO status in one variable, but map process exit codes through one app-level helper: `2` for usage, `1` for every other failure. [VERIFIED: `04-CONTEXT.md`]

**When to use:** Every non-success exit path in `main`. [VERIFIED: `04-CONTEXT.md`]

**Example:**
```c
static int fail_usage(void)
{
    fprintf(stderr, "fits2json: expected exactly 1 FITS path argument\n");
    print_usage(stderr);
    return 2;
}

static int fail_cfitsio(const char *context, int status)
{
    fprintf(stderr, "fits2json: %s\n", context);
    fits_report_error(stderr, status);
    return 1;
}

static int fail_app(const char *message)
{
    fprintf(stderr, "fits2json: %s\n", message);
    return 1;
}
```
Source: synthesized from current `fits2json.c` error branches and locked failure contract. [VERIFIED: `src/fits2json.c`; `04-CONTEXT.md`]

### Anti-Patterns to Avoid
- **Returning raw CFITSIO status codes from `main`:** Current code returns values like `104`, `45`, and `107`, which violates D-06. [VERIFIED: bash probes; `src/fits2json.c` lines 599-601, 633-645]
- **Deferring CFITSIO discovery to compile/link failure:** Fail early with an explicit prerequisite message instead. [VERIFIED: `04-CONTEXT.md`][CITED: https://people.freedesktop.org/~dbn/pkg-config-guide.html]
- **Broad cleanup globs outside an explicit artifact list:** D-12 requires never deleting checked-in files. [VERIFIED: `04-CONTEXT.md`; `.gitignore`]
- **A fake `test` interface:** `make -C src test` must become real; today it fails with “No rule to make target `test`”. [VERIFIED: bash `make -C src test`]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| FITS parsing/selectors | Custom FITS parser | CFITSIO | Project scope explicitly keeps CFITSIO; parser correctness and edge cases are already delegated there. [VERIFIED: `PROJECT.md`; `src/fits2json.c`] |
| Library discovery | Machine-specific `/usr/local` assumptions | `pkg-config cfitsio` with manual override escape hatch | More portable, still overrideable when needed. [VERIFIED: `src/Makefile`; bash `pkg-config --cflags/--libs cfitsio`][CITED: https://people.freedesktop.org/~dbn/pkg-config-guide.html] |
| JSON smoke assertions in shell | Grep-based text checks | Existing Python `json.loads` harness pattern | Existing tests already validate actual JSON structure and stderr cleanliness. [VERIFIED: `test/phase2_selected_hdu_smoke.py`; `test/phase3_whole_file_smoke.py`] |
| Exit semantics | Library-defined exit space | App-defined `0/1/2` contract | Locked by D-06 and easier for automation consumers. [VERIFIED: `04-CONTEXT.md`] |

**Key insight:** The repo already has the right ingredients; Phase 4 should wire them together and standardize failure semantics, not invent a new framework. [VERIFIED: repo files]

## Common Pitfalls

### Pitfall 1: Silent pkg-config failure
**What goes wrong:** `$(shell pkg-config --cflags --libs cfitsio 2>/dev/null)` can collapse to empty text, causing confusing later compiler/linker failures. [ASSUMED]  
**Why it happens:** `pkg-config` communicates missing metadata through exit status and stderr, not through a guaranteed non-empty expansion. [CITED: https://people.freedesktop.org/~dbn/pkg-config-guide.html]  
**How to avoid:** Check discovery explicitly and fail early with a prerequisite message, while still allowing `CFITSIO_CFLAGS=... CFITSIO_LIBS=...` overrides. [VERIFIED: `04-CONTEXT.md`][CITED: https://www.gnu.org/software/make/manual/html_node/Overriding.html]  
**Warning signs:** Build fails only at compile/link time, or succeeds only on one machine layout. [VERIFIED: `src/Makefile`; `.planning/codebase/CONCERNS.md`]

### Pitfall 2: Wrong exit-code surface for automation
**What goes wrong:** Current failures return raw CFITSIO codes (`104`, `45`, `107`) instead of stable app categories. [VERIFIED: bash probes]  
**Why it happens:** `main` returns `status` directly on CFITSIO errors. [VERIFIED: `src/fits2json.c` lines 599-601, 633-645]  
**How to avoid:** Separate `cfitsio_status` from `exit_code`; only `exit_code` should reach `return`. [ASSUMED]  
**Warning signs:** Shell scripts must special-case many numeric failure codes. [ASSUMED]

### Pitfall 3: Incomplete cleanup
**What goes wrong:** Current `clean` leaves `test/phase2_make_edge_fixture` and `testdata/phase2-edge.fits` behind. [VERIFIED: bash clean audit]  
**Why it happens:** `src/Makefile` only removes `fits2json.o` and `fits2json`. [VERIFIED: `src/Makefile` lines 20-21]  
**How to avoid:** Keep an explicit generated-artifact list in `src/Makefile`, limited to binary/object/helper/generated-fixture/cache paths. [VERIFIED: `04-CONTEXT.md`; `.gitignore`][ASSUMED]  
**Warning signs:** Re-running tests uses stale generated inputs or `git status` stays dirty after verification. [VERIFIED: `.gitignore`; bash artifact audit]

### Pitfall 4: Assuming “stdout empty on failure” is already fully solved
**What goes wrong:** Open/read failures are safe today, but streamed emission may still permit partial stdout if a write fails mid-output. [VERIFIED: `src/fits2json.c` emits only after read; ASSUMED: partial-write risk]  
**Why it happens:** JSON is written directly to `stdout` one chunk at a time. [VERIFIED: `src/fits2json.c` lines 447-577]  
**How to avoid:** Either serialize to memory before the first stdout write, or explicitly narrow the contract to pre-emission failures. [ASSUMED]  
**Warning signs:** Broken-pipe or write-error handling is unspecified in plan/tasks. [ASSUMED]

## Code Examples

### Canonical repo-local verification sequence
```make
test: fits2json ../test/phase2_make_edge_fixture ../testdata/phase2-edge.fits
	$(PYTHON) ../test/phase2_selected_hdu_smoke.py
	$(PYTHON) ../test/phase3_whole_file_smoke.py
	$(PYTHON) ../test/phase4_cli_contract_smoke.py
```
Source: synthesis from locked decisions plus existing test scripts. [VERIFIED: `04-CONTEXT.md`; `test/phase2_selected_hdu_smoke.py`; `test/phase3_whole_file_smoke.py`]

### Minimal new error-contract smoke shape
```python
def assert_failure(args, expected_rc, required_substrings):
    proc = subprocess.run(args, text=True, capture_output=True, check=False)
    assert proc.returncode == expected_rc
    assert proc.stdout == ""
    for text in required_substrings:
        assert text in proc.stderr

# usage
assert_failure([BINARY], 2, ["fits2json:", "Usage:"])

# missing file
assert_failure([BINARY, "does-not-exist.fits"], 1, ["fits2json:", "FITSIO status ="])

# bad selector on real file
assert_failure([BINARY, "testdata/IRPH0189.HDR[NOPE]"], 1, ["fits2json:", "FITSIO status ="])
```
Source: synthesized from existing Python smoke style and locked failure contract. [VERIFIED: `test/phase2_selected_hdu_smoke.py`; `04-CONTEXT.md`]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hard-coded include/lib paths in Makefile [VERIFIED: `src/Makefile`] | `pkg-config cfitsio` with overrideable flags [VERIFIED: D-09/D-10] | Phase 4 decision, 2026-04-12 [VERIFIED: `04-CONTEXT.md`] | Build becomes portable across different install prefixes without blocking manual overrides. [CITED: https://people.freedesktop.org/~dbn/pkg-config-guide.html][CITED: https://www.gnu.org/software/make/manual/html_node/Overriding.html] |
| Manual smoke invocation [VERIFIED: repo test scripts] | `make -C src test` as canonical automation surface [VERIFIED: D-01/D-03] | Phase 4 decision, 2026-04-12 [VERIFIED: `04-CONTEXT.md`] | One command can build, regenerate fixtures, and verify both success and failure behavior. [VERIFIED: `04-CONTEXT.md`] |
| Library exit codes leaking to callers [VERIFIED: bash probes] | Stable app exit categories `2`/`1` [VERIFIED: D-08] | Phase 4 decision, 2026-04-12 [VERIFIED: `04-CONTEXT.md`] | Scripts stop depending on CFITSIO’s numeric error space. [VERIFIED: `04-CONTEXT.md`] |

**Deprecated/outdated:**
- Hard-coded `/usr/local/include` and `/usr/local/lib` in `src/Makefile`. [VERIFIED: `src/Makefile`][VERIFIED: `.planning/codebase/CONCERNS.md`]
- Pretending `make -C src test` exists when it currently does not. [VERIFIED: bash `make -C src test`]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The D-04 “stdout empty on failure” contract should cover stdout write/broken-pipe failures, not just open/read/convert failures | Common Pitfalls / Open Questions | Planner may under-scope the implementation; strict compliance may require buffering before stdout writes |
| A2 | A new `test/phase4_cli_contract_smoke.py` is the smallest maintainable way to add error/repeatability coverage | Architecture Patterns / Validation Architecture | Planner might choose a shell-based harness instead |

## Open Questions (RESOLVED)

1. **Does D-04 include broken-pipe / stdout write failures?**
   - **Resolved:** No. The empty-stdout guarantee is locked to failures detected before emission begins; detectable broken-pipe/write failures after emission starts must still report `fits2json:` diagnostics on stderr and exit `1`, but do not promise zero-byte stdout retroactively.
   - What we know: Open/read/selector failures already leave stdout empty because emission happens after model building. [VERIFIED: `src/fits2json.c` lines 609-628]

2. **Is Python 3 an acceptable hard prerequisite for `make -C src test`?**
   - **Resolved:** Yes. Python 3 is an accepted verification prerequisite for the canonical `test` target.
   - What we know: Existing smoke harnesses are Python scripts, and Python 3.12.3 is available in the current environment. [VERIFIED: repo test files; bash `python3 --version`]

3. **Should `test` always regenerate the edge fixture, even if timestamps suggest it is current?**
   - **Resolved:** Yes. The synthetic edge fixture should be regenerated on every `make -C src test` run.
   - What we know: D-03 explicitly says the default verification path should regenerate it. [VERIFIED: `04-CONTEXT.md`]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| make | `make -C src`, `make -C src test`, `make -C src clean` | ✓ [VERIFIED: bash `command -v make`] | 4.3 [VERIFIED: bash] | — |
| gcc | building `fits2json` and helper binary | ✓ [VERIFIED: bash `command -v gcc`] | 13.3.0 [VERIFIED: bash] | `CC=...` override is possible in make, but no alternate compiler was verified in-session [CITED: https://www.gnu.org/software/make/manual/html_node/Overriding.html] |
| pkg-config | preferred CFITSIO discovery | ✓ [VERIFIED: bash `command -v pkg-config`] | 1.8.1 [VERIFIED: bash] | Manual `CFITSIO_CFLAGS` / `CFITSIO_LIBS` overrides [VERIFIED: D-08][CITED: https://www.gnu.org/software/make/manual/html_node/Overriding.html] |
| CFITSIO `.pc` metadata + library | build/link and runtime FITS parsing | ✓ [VERIFIED: bash `pkg-config --exists cfitsio`] | 4.2.0 [VERIFIED: bash `pkg-config --modversion cfitsio`] | Manual flags can bypass missing `.pc` metadata if the library is installed elsewhere [CITED: https://people.freedesktop.org/~dbn/pkg-config-guide.html] |
| Python 3 | repo-local smoke/error scripts | ✓ [VERIFIED: bash `command -v python3`] | 3.12.3 [VERIFIED: bash] | No verified repo-local fallback today |

**Missing dependencies with no fallback:** None in the current environment. [VERIFIED: bash]  
**Missing dependencies with fallback:** None in the current environment. [VERIFIED: bash]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Direct Python smoke scripts + GNU make target, not pytest/unittest config [VERIFIED: `test/phase2_selected_hdu_smoke.py`; `test/phase3_whole_file_smoke.py`; no test runner config detected] |
| Config file | none — direct script entry points [VERIFIED: repo scan from provided files] |
| Quick run command | `make -C src test` [VERIFIED: D-01/D-03; currently missing implementation] |
| Full suite command | `make -C src test` [VERIFIED: D-01/D-03; phase scope is repo-local smoke/error coverage] |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| BLD-01 | `make -C src` builds single executable `src/fits2json` | build/smoke | `make -C src clean && make -C src && test -x src/fits2json` | ✅ existing Makefile, but no explicit scripted assertion file [VERIFIED: `src/Makefile`] |
| CLI-02 | usage/open/selector failures emit stderr-only diagnostics and non-zero exit | integration | `python3 test/phase4_cli_contract_smoke.py --mode errors` | ❌ Wave 0 [ASSUMED] |
| CLI-03 | repeated success/failure runs are deterministic | integration | `python3 test/phase4_cli_contract_smoke.py --mode repeatability` | ❌ Wave 0 [ASSUMED] |
| CLI-03 | successful JSON shape remains unchanged | integration | `python3 test/phase2_selected_hdu_smoke.py && python3 test/phase3_whole_file_smoke.py` | ✅ [VERIFIED: repo test files] |

### Sampling Rate
- **Per task commit:** `make -C src test` [VERIFIED: D-01]  
- **Per wave merge:** `make -C src test` [VERIFIED: D-01]  
- **Phase gate:** `make -C src clean && make -C src test && make -C src clean` [ASSUMED]

### Wave 0 Gaps
- [ ] `src/Makefile` — add real `test` target wired to existing smoke scripts and new error-contract smoke [VERIFIED: bash `make -C src test`]
- [ ] `src/Makefile` — expand `clean` to remove helper binary, generated edge fixture, and caches only [VERIFIED: bash clean audit; `.gitignore`]
- [ ] `src/Makefile` — add early CFITSIO prerequisite check using `pkg-config` with override escape hatch [VERIFIED: D-07/D-09]
- [ ] `test/phase4_cli_contract_smoke.py` — usage/missing-file/bad-selector/repeatability checks [ASSUMED]
- [ ] `src/fits2json.c` — centralize failure-reporting and exit-code mapping [VERIFIED: `src/fits2json.c`; `04-CONTEXT.md`]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no [VERIFIED: local CLI only] | — |
| V3 Session Management | no [VERIFIED: local CLI only] | — |
| V4 Access Control | no [VERIFIED: local CLI only] | — |
| V5 Input Validation | yes [VERIFIED: CLI argument and FITS path are untrusted inputs] | strict `argc` validation, stderr-only failures, CFITSIO parser boundary [VERIFIED: `src/fits2json.c`][ASSUMED] |
| V6 Cryptography | no [VERIFIED: no crypto in scope] | — |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed FITS input triggers parser/library edge behavior | Tampering / DoS | Keep parsing in CFITSIO, document/discover version, add regression cases for failure paths. [VERIFIED: `.planning/codebase/CONCERNS.md`; `src/fits2json.c`][ASSUMED] |
| Ambiguous exit codes break automation | Denial of Service | Stable app exit contract `2`/`1` plus stderr diagnostics. [VERIFIED: `04-CONTEXT.md`] |
| Partial or mixed stdout/stderr corrupts downstream JSON pipelines | Tampering | Preserve stdout as success-only channel and run error-path smoke checks. [VERIFIED: `REQUIREMENTS.md`; `04-CONTEXT.md`; existing smoke scripts] |

## Sources

### Primary (HIGH confidence)
- Repository files:
  - `.planning/phases/04-verification-build-cleanup/04-CONTEXT.md` — locked scope and decisions
  - `.planning/REQUIREMENTS.md` — CLI-02, CLI-03, BLD-01
  - `src/Makefile` — current build/clean behavior
  - `src/fits2json.c` — current runtime failure/output behavior
  - `test/phase2_selected_hdu_smoke.py` — selected-HDU success checks
  - `test/phase3_whole_file_smoke.py` — whole-file success checks
  - `test/phase2_make_edge_fixture.c` — synthetic fixture generator
  - `.planning/codebase/CONCERNS.md`, `.planning/codebase/TESTING.md`, `.planning/codebase/CONVENTIONS.md`
  - `copilot-instructions.md`
- Bash verification:
  - `make --version`, `gcc --version`, `python3 --version`, `pkg-config --version`
  - `pkg-config --exists/--modversion/--cflags/--libs cfitsio`
  - `make -C src`
  - `make -C src test`
  - `make -C src clean` + artifact audit
  - runtime probes for usage, missing file, bad selector, repeatability
  - existing smoke runs for Phase 2 and Phase 3

### Secondary (MEDIUM confidence)
- GNU Make manual:
  - https://www.gnu.org/software/make/manual/html_node/Overriding.html
  - https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html
  - https://www.gnu.org/software/make/manual/html_node/Errors.html
- pkg-config guide:
  - https://people.freedesktop.org/~dbn/pkg-config-guide.html

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — repo tooling and local environment were directly verified.
- Architecture: MEDIUM — Makefile/test wiring is clear, but strict stdout-empty semantics for write failures remain an explicit scope question.
- Pitfalls: HIGH — current gaps were directly reproduced from repo and shell.

**Research date:** 2026-04-12  
**Valid until:** 2026-05-12
