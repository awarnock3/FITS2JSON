# Codebase Concerns

**Analysis Date:** 2026-04-12

## Tech Debt

**Build and test scaffolding drift:**
- Issue: `src/Makefile` declares `.PHONY: all test clean`, but there is no `test` target and `clean` shells into a non-existent `test/` directory.
- Files: `src/Makefile`
- Impact: `make clean` exits with an error, local automation cannot rely on standard cleanup behavior, and the repository advertises a test structure that does not exist.
- Fix approach: Remove the stale `test` references or add a real `test/` directory and `test` target wired to executable checks.

**Hard-coded CFITSIO paths:**
- Issue: Compilation and linking are pinned to `/usr/local/include` and `/usr/local/lib` in `src/Makefile` instead of discovering CFITSIO from the environment.
- Files: `src/Makefile`
- Impact: Builds are brittle across Linux distributions, package managers, CI images, and macOS setups where CFITSIO is installed elsewhere.
- Fix approach: Resolve flags with `pkg-config cfitsio`, configurable `CPPFLAGS`/`LDFLAGS`, or overridable make variables.

**Build artifacts are not ignored:**
- Issue: Local builds create `src/listhead`, but `.gitignore` does not exclude that binary.
- Files: `.gitignore`, `src/Makefile`
- Impact: Routine builds dirty the working tree and increase the chance of accidental binary commits.
- Fix approach: Add `src/listhead` or a broader binary pattern for this project to `.gitignore`.

## Known Bugs

**CLI usage error returns success:**
- Symptoms: Running the program with no filename prints usage text and exits with status `0`.
- Files: `src/listhead.c`
- Trigger: Invoke `src/listhead` without exactly one positional argument.
- Workaround: Wrap the binary with external argument validation; the source should return a non-zero code from the `argc != 2` branch.

**Cleanup command is broken:**
- Symptoms: `make clean` removes local objects, then fails with `make -C test clean` because `test/` is missing.
- Files: `src/Makefile`
- Trigger: Run `make clean` inside `src/`.
- Workaround: Delete `src/listhead` and `src/listhead.o` manually until the Makefile is corrected.

## Security Considerations

**Parser surface relies entirely on external library behavior:**
- Risk: `src/listhead.c` accepts arbitrary FITS paths from the command line and sends them straight into CFITSIO via `fits_open_file` / `fits_read_record`; malformed-file safety depends on the linked CFITSIO build.
- Files: `src/listhead.c`, `src/Makefile`, `testdata/`
- Current mitigation: FITS parsing is delegated to CFITSIO rather than custom parsing logic.
- Recommendations: Pin and document a supported CFITSIO version, add malformed-input regression cases under `testdata/`, and run them in CI once workflow files exist under `.github/`.

**No automated verification around sample data ingestion:**
- Risk: Parsing regressions or unsafe behavior against real headers can ship unnoticed because sample files in `testdata/` are never exercised automatically.
- Files: `testdata/`, `.github/`, `src/Makefile`
- Current mitigation: Not detected.
- Recommendations: Add a non-interactive test command that runs `src/listhead` against representative files such as `testdata/IRPH0189.HDR` and validates deterministic output.

## Performance Bottlenecks

**Header output is stdout-bound for large FITS sets:**
- Problem: The core loop reads one card at a time and emits one `printf` per record.
- Files: `src/listhead.c`
- Cause: `fits_read_record` and `printf("%s\n", card)` are executed for every header entry in every HDU from the nested loop at `src/listhead.c`.
- Improvement path: Buffer output, add selective keyword filtering, or emit structured JSON in one pass to reduce terminal and pipe overhead on large multi-HDU files.

## Fragile Areas

**Single-file CLI with all behavior in `main`:**
- Files: `src/listhead.c`
- Why fragile: Argument handling, HDU traversal, formatting, and error reporting are all coupled inside one `main` function, so feature work changes the only execution path.
- Safe modification: Extract argument parsing, FITS iteration, and output formatting into separate helpers before adding new behavior such as JSON serialization.
- Test coverage: No automated tests detected under `src/`, `test/`, or `.github/`.

**Build workflow depends on local machine state:**
- Files: `src/Makefile`, `.github/`
- Why fragile: The build assumes GCC plus CFITSIO headers and libraries under `/usr/local`, and there are no workflow files in `.github/` to prove that assumption on a clean machine.
- Safe modification: Parameterize compiler and library locations first, then add a minimal CI build job to validate clean-environment setup.
- Test coverage: No CI or build verification detected in `.github/`.

## Scaling Limits

**Throughput scales one file per process:**
- Current capacity: One FITS file is processed per invocation, sequentially, by the single `main` loop in `src/listhead.c`.
- Limit: Batch conversions require external shell scripting; there is no built-in batching, parallelism, or machine-readable aggregation.
- Scaling path: Add a batch CLI mode, structured output, and an automated test harness that validates multiple files from `testdata/`.

## Dependencies at Risk

**CFITSIO integration is unversioned and environment-specific:**
- Risk: The project links against whatever `-lcfitsio` is available in `/usr/local/lib`, with no documented version floor or compatibility check.
- Impact: Builds can fail or behavior can drift across developer machines and deployment targets.
- Migration plan: Document the supported CFITSIO version in `README.md`, discover it at build time, and fail early with a readable prerequisite check.

## Missing Critical Features

**JSON translation is not implemented:**
- Problem: `README.md` describes “A program to translate FITS headers to JSON”, but `src/listhead.c` prints raw FITS header cards and `END` markers rather than JSON.
- Blocks: Any downstream workflow expecting valid JSON output, machine-readable integration, or schema-based validation.

**Automated tests are not implemented:**
- Problem: The repository has sample FITS headers in `testdata/`, but no executable tests, no `test/` directory, and no CI workflow files under `.github/`.
- Blocks: Safe refactoring, dependency upgrades, and confident verification of edge cases such as malformed files or extension selection.

## Test Coverage Gaps

**CLI behavior and exit semantics are untested:**
- What's not tested: Usage failures, missing-file errors, single-extension handling, and multi-HDU traversal.
- Files: `src/listhead.c`, `testdata/`
- Risk: Changes to argument parsing or HDU iteration can silently alter scripting behavior.
- Priority: High

**Build and cleanup workflow are untested:**
- What's not tested: `make`, `make clean`, and clean-machine setup with CFITSIO prerequisites.
- Files: `src/Makefile`, `.github/`
- Risk: The repository can appear healthy while standard developer commands fail outside the current machine state.
- Priority: High

---

*Concerns audit: 2026-04-12*
