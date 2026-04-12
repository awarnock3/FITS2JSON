# Phase 4: Verification & Build Cleanup - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-12
**Phase:** 4-Verification & Build Cleanup
**Areas discussed:** Build and test command surface, Failure contract on errors, Build portability and dependency discovery, Cleanup behavior for generated artifacts

---

## Build and test command surface

| Option | Description | Selected |
|--------|-------------|----------|
| `make -C src test` as the canonical smoke/verification entry point | Promote verification into the existing Makefile entry point so automation has one documented command | ✓ |
| Keep `make -C src` for build only, and document separate test commands | Preserve build-only Makefile behavior and rely on external documentation for verification | |
| Expose both build and verification through Make targets in `src/Makefile`, with `test` as the documented verification command | Similar direction, but leaves the canonical entry point less explicit | |

**User's choice:** `make -C src test` as the canonical smoke/verification entry point
**Notes:** The Makefile should own the repeatable verification path rather than leaving it as ad hoc shell commands.

## Default verification scope

| Option | Description | Selected |
|--------|-------------|----------|
| Build plus all repo-local smoke checks, including regenerating the synthetic edge fixture and exercising error-path behavior | Make the canonical test path cover both happy-path regressions and deterministic failure checks | ✓ |
| Build plus happy-path smoke checks only | Limit automation to successful conversions and leave failure semantics for manual testing | |
| Only run the Python smoke scripts and assume the binary was already built | Narrow the test target to smoke scripts without owning the full build-and-test flow | |

**User's choice:** Build plus all repo-local smoke checks, including regenerating the synthetic edge fixture and exercising error-path behavior
**Notes:** Phase 4 should harden the full automation path, not only preserve successful conversions.

## Failure contract on errors

| Option | Description | Selected |
|--------|-------------|----------|
| Keep stdout empty on failure, print a short `fits2json:` message on stderr plus CFITSIO details when available, and use stable category-based non-zero exit codes | Makes failures easy to script against while still preserving library detail for debugging | ✓ |
| Keep stdout empty on failure, but return raw CFITSIO/library status codes directly | Leans on library codes rather than a project-level failure contract | |
| Print only CFITSIO/library error text on stderr and avoid project-specific messages | Minimizes project messaging but gives a weaker CLI contract | |

**User's choice:** Keep stdout empty on failure, print a short `fits2json:` message on stderr plus CFITSIO details when available, and use stable category-based non-zero exit codes
**Notes:** The user wants deterministic script-friendly behavior rather than exposing raw library semantics as the primary contract.

## Exit-code policy

| Option | Description | Selected |
|--------|-------------|----------|
| Simple categories: `2` for usage/invalid invocation, `1` for conversion/build/test failures | Keep the failure contract small, stable, and easy for scripts to reason about | ✓ |
| More granular categories for different failure classes | Expose a broader numeric matrix for open/parse/write/build failures | |
| Keep the door open for category-based codes later, but don't lock a numeric policy in Phase 4 | Defer the concrete numeric policy | |

**User's choice:** Simple categories: `2` for usage/invalid invocation, `1` for conversion/build/test failures
**Notes:** Simplicity and determinism matter more here than fine-grained error taxonomy.

## Build portability and dependency discovery

| Option | Description | Selected |
|--------|-------------|----------|
| Prefer `pkg-config cfitsio`, but allow standard make-variable overrides (`CPPFLAGS`, `LDFLAGS`, etc.) and fail with a clear prerequisite message if CFITSIO can't be found | Improve portability without blocking manual overrides on nonstandard setups | ✓ |
| Keep the current hard-coded `/usr/local` paths and just document that assumption | Optimize for the current machine layout only | |
| Use only manual make-variable overrides and do not rely on `pkg-config` | Avoid `pkg-config`, but require users/CI to pass all discovery flags explicitly | |

**User's choice:** Prefer `pkg-config cfitsio`, but allow standard make-variable overrides (`CPPFLAGS`, `LDFLAGS`, etc.) and fail with a clear prerequisite message if CFITSIO can't be found
**Notes:** The default build should become portable, but manual overrides should remain available.

## Cleanup behavior for generated artifacts

| Option | Description | Selected |
|--------|-------------|----------|
| All build and test-generated artifacts only — binary, objects, compiled helper, generated FITS fixture, and caches — but never checked-in files | Reset generated state safely without deleting tracked repo content | ✓ |
| Only build artifacts from `src/`, and leave test-generated files alone | Keep `clean` narrow and let test outputs accumulate | |
| Be aggressive and remove both generated artifacts and any reproducible fixture outputs under `testdata/` whether tracked or not | Risk deleting tracked files in the name of a deeper clean | |

**User's choice:** All build and test-generated artifacts only — binary, objects, compiled helper, generated FITS fixture, and caches — but never checked-in files
**Notes:** Cleanup should make the workspace repeatable but must stay safe around checked-in fixtures and docs.

---

## the agent's Discretion

- Exact target/helper factoring inside `src/Makefile`
- Exact error-path cases needed to prove deterministic failure behavior
- Exact wording of prerequisite and failure messages, within the locked stderr/stdout and exit-code contract

## Deferred Ideas

None.
