# Coding Conventions

**Analysis Date:** 2026-04-12

## Naming Patterns

**Files:**
- Use lowercase source filenames with no separators for the single-purpose CLI translation unit in `src/listhead.c`.
- Keep build configuration in conventional tool names such as `src/Makefile`.

**Functions:**
- Use lower_snake_case for external library calls from CFITSIO, as seen with `fits_open_file`, `fits_get_hdu_num`, and `fits_report_error` in `src/listhead.c`.
- Keep local program entry points minimal and procedural; `src/listhead.c` exposes only `main`.

**Variables:**
- Use short lowercase local names for loop counters and status plumbing, such as `status`, `single`, `hdupos`, `nkeys`, and `ii` in `src/listhead.c`.
- Use pointer abbreviations for library-owned handles, such as `fptr` in `src/listhead.c`.

**Types:**
- Prefer library-provided C types directly instead of project-defined wrappers, e.g. `fitsfile *` and `char card[FLEN_CARD]` in `src/listhead.c`.
- No custom structs, enums, or typedef naming conventions are established outside CFITSIO types in `src/listhead.c`.

## Code Style

**Formatting:**
- Formatting tool configuration is not detected; no `.clang-format`, `.editorconfig`, `.prettierrc`, or equivalent file is present at the repository root.
- Match the existing manual C style in `src/listhead.c`: opening braces usually appear on the next line for functions and multi-line control blocks, and indentation is space-based with some nested blocks using two-space increments.
- Keep include directives grouped with system headers first and the local third-party header last, as in `src/listhead.c`.

**Linting:**
- Dedicated lint configuration is not detected.
- Compiler warnings are the closest enforced style gate: `src/Makefile` builds with `-Wall -O2 -D_POSIX_C_SOURCE=200809L`.

## Import Organization

**Order:**
1. Standard library headers, e.g. `#include <string.h>` and `#include <stdio.h>` in `src/listhead.c`
2. Project or third-party local headers, e.g. `#include "fitsio.h"` in `src/listhead.c`
3. Not applicable beyond those two groups; no internal module include tree exists outside `src/listhead.c`

**Path Aliases:**
- Not detected. Includes in `src/listhead.c` use direct header names only.

## Error Handling

**Patterns:**
- Thread CFITSIO error state through an integer `status` variable initialized to zero in `src/listhead.c`.
- Gate follow-up operations on library success, e.g. `if (!fits_open_file(..., &status))` in `src/listhead.c`.
- Normalize expected terminal conditions before exit, e.g. `if (status == END_OF_FILE) status = 0;` in `src/listhead.c`.
- Delegate final error rendering to the library with `fits_report_error(stderr, status)` in `src/listhead.c`.
- Return process status codes directly from `main`, including the usage path `return(0);` and the final `return(status);` in `src/listhead.c`.

## Logging

**Framework:** `printf` plus CFITSIO error reporting

**Patterns:**
- Use `printf` for user-facing CLI output, including usage guidance and emitted FITS header records in `src/listhead.c`.
- Reserve `stderr` output for library-generated error details through `fits_report_error` in `src/listhead.c`.
- No structured logging, debug logger, or verbosity flag is implemented outside `src/listhead.c`.

## Comments

**When to Comment:**
- Add short block comments to explain CFITSIO-specific behavior or control-flow intent, such as the comments on `status`, header iteration, and single-extension handling in `src/listhead.c`.
- Keep comments close to the line they clarify instead of using large file headers; `src/listhead.c` relies on inline comments only.

**JSDoc/TSDoc:**
- Not applicable. The repository is C-based, and no API documentation block style is established in `src/listhead.c` or `src/Makefile`.

## Function Design

**Size:** Keep functions compact and procedural. The entire program flow currently lives in the 63-line `main` function in `src/listhead.c`.

**Parameters:** Pass arguments explicitly and forward mutable error state by pointer when calling CFITSIO functions, matching the call style in `src/listhead.c`.

**Return Values:** Return integer process codes from top-level routines and rely on CFITSIO status values rather than custom error enums, as shown in `src/listhead.c`.

## Module Design

**Exports:** No internal export pattern is established. The codebase currently consists of one executable translation unit in `src/listhead.c`.

**Barrel Files:** Not applicable. No header files or aggregator modules are present under `src/`.

## Repository-Specific Conventions

- Build from `src/Makefile` rather than a root-level build script.
- Link against CFITSIO from conventional local paths using `-I/usr/local/include` and `-L/usr/local/lib` in `src/Makefile`.
- Treat generated artifacts as disposable local outputs: `.gitignore` excludes object files and executables, and `src/listhead.o` plus `src/listhead` are build products of `src/Makefile`.
- Use sample FITS header files in `testdata/*.HDR` as manual verification fixtures for the CLI in `src/listhead.c`.

---

*Convention analysis: 2026-04-12*
