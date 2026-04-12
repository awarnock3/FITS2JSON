# Testing Patterns

**Analysis Date:** 2026-04-12

## Test Framework

**Runner:**
- Not detected. No `jest.config.*`, `vitest.config.*`, `CTest`, `Makefile` test recipe, or other automated test runner configuration is present at the repository root or under `src/`.
- The only build script, `src/Makefile`, declares `.PHONY: all test clean` but does not define a runnable `test` target body.

**Assertion Library:**
- Not detected. `src/listhead.c` contains no assertion macros, and no testing library sources are present.

**Run Commands:**
```bash
make -C src                           # Build the `src/listhead` executable
./src/listhead testdata/IRPH0189.HDR  # Manual smoke test using a checked-in fixture from `testdata/`
make -C src clean                     # Remove `src/listhead.o` and `src/listhead`
```

## Test File Organization

**Location:**
- No automated test files are present. `find . -name "*.test.*" -o -name "*.spec.*"` returns no matches.
- Manual verification data lives in `testdata/`.

**Naming:**
- Sample inputs use uppercase `.HDR` filenames such as `testdata/IRPH0189.HDR` and `testdata/SPEC2444.HDR`.
- No naming convention for test source files is established because no test source tree exists.

**Structure:**
```text
testdata/*.HDR
```

## Test Structure

**Suite Organization:**
```typescript
// Not applicable: no automated test suites are present in `src/` or a separate `test/` directory.
```

**Patterns:**
- Setup pattern: build the CLI with `src/Makefile`, then invoke `src/listhead` directly against files in `testdata/`.
- Teardown pattern: remove local build artifacts with `make -C src clean`.
- Assertion pattern: compare emitted header text from `./src/listhead <fixture>` against expected FITS header records manually; no checked-in golden file comparison is implemented.

## Mocking

**Framework:** Not applicable

**Patterns:**
```typescript
// No mocking framework or substitution layer is implemented in `src/listhead.c`.
```

**What to Mock:**
- No repo convention is established. The current code in `src/listhead.c` talks directly to CFITSIO and the filesystem.

**What NOT to Mock:**
- Preserve real FITS parsing behavior from the linked CFITSIO library when validating `src/listhead.c`; the repository’s existing practice relies on real `.HDR` fixtures under `testdata/`.

## Fixtures and Factories

**Test Data:**
```typescript
// Manual fixture pattern:
// 1. Choose a checked-in FITS header sample from `testdata/`.
// 2. Run `./src/listhead testdata/IRPH0189.HDR`.
// 3. Inspect the printed header listing for correctness.
```

**Location:**
- Fixture files are stored in `testdata/`.
- The repository currently includes 44 checked-in `.HDR` samples in `testdata/`.

## Coverage

**Requirements:** None enforced. No coverage tool or threshold configuration is present.

**View Coverage:**
```bash
# Not applicable: no automated coverage command is configured in `src/Makefile` or elsewhere.
```

## Test Types

**Unit Tests:**
- Not used. No unit test sources or isolated function-level tests exist for `src/listhead.c`.

**Integration Tests:**
- Manual only. Running `src/listhead` against real fixtures in `testdata/` is the repository’s observable integration test pattern.

**E2E Tests:**
- Not used. The repository exposes a single CLI executable in `src/listhead.c` and no dedicated end-to-end harness exists.

## Common Patterns

**Async Testing:**
```typescript
// Not applicable: `src/listhead.c` is synchronous and no async test framework is configured.
```

**Error Testing:**
```typescript
// Manual error-path check:
// ./src/listhead
// Expect usage text from `src/listhead.c` and exit code 0.
```

## Gaps That Affect Future Testing

- `src/Makefile` references `$(MAKE) -C test clean` on line 22, but no `test/` directory exists in the repository.
- No golden outputs, snapshot files, or shell scripts exist to turn the `testdata/` fixtures into repeatable regression tests.
- No CI workflow under `.github/` runs builds or manual smoke checks for `src/listhead.c`.

---

*Testing analysis: 2026-04-12*
