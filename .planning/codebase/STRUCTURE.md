# Codebase Structure

**Analysis Date:** 2026-04-12

## Directory Layout

```text
FITS2JSON/
├── README.md                 # Minimal project description
├── LICENSE                   # Repository license
├── src/                      # C source, build script, and local build artifacts
│   ├── Makefile              # Build and clean targets for `listhead`
│   └── listhead.c            # Entire runtime implementation
├── testdata/                 # Sample FITS header files used as manual input corpus
├── .github/                  # GitHub metadata directory; no tracked files detected
└── .planning/codebase/       # Generated planning documents for codebase mapping
```

## Directory Purposes

**`src/`:**
- Purpose: Hold the only tracked implementation and its build definition.
- Contains: `C` source in `src/listhead.c`, build rules in `src/Makefile`, and ignored local artifacts such as `src/listhead.o`; an untracked compiled binary `src/listhead` is present in the working tree.
- Key files: `src/listhead.c`, `src/Makefile`

**`testdata/`:**
- Purpose: Store sample FITS-compatible header files for manual execution and inspection.
- Contains: Uppercase `.HDR` files such as `testdata/IRPH0189.HDR` and `testdata/SPEC2445.HDR`.
- Key files: `testdata/IRPH0189.HDR`, `testdata/PFLX1995.HDR`

**`.github/`:**
- Purpose: Reserved location for GitHub automation or repository metadata.
- Contains: No tracked files were detected under `.github/`.
- Key files: Not applicable

**`.planning/codebase/`:**
- Purpose: Store generated analysis documents used by planning and execution workflows.
- Contains: Architecture and structure references such as `.planning/codebase/ARCHITECTURE.md` and `.planning/codebase/STRUCTURE.md`.
- Key files: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`

## Key File Locations

**Entry Points:**
- `src/listhead.c`: Program runtime entry via `main`.
- `src/Makefile`: Build entry for `make`, `make all`, and `make clean`.

**Configuration:**
- `src/Makefile`: Compiler selection, include/library search paths, optimization flags, and CFITSIO link settings.
- `.gitignore`: Ignore rules for object files, executables, libraries, and debug artifacts that can be generated during local builds.

**Core Logic:**
- `src/listhead.c`: FITS file opening, HDU iteration, header-card reading, stdout formatting, and CFITSIO error reporting.

**Testing:**
- `testdata/`: Manual fixture directory only; no `test/`, `tests/`, or automated test runner configuration files are present in the tracked repository.

## Naming Conventions

**Files:**
- Lowercase implementation filenames are used in `src/`, as in `src/listhead.c`.
- Build configuration uses the conventional capitalized filename `src/Makefile`.
- Sample data files in `testdata/` use uppercase `.HDR` names such as `testdata/NNSN2261.HDR`.

**Directories:**
- Top-level source and fixture directories are short lowercase nouns: `src/` and `testdata/`.
- Hidden metadata directories use dot-prefixed names: `.github/` and `.planning/`.

## Where to Add New Code

**New Feature:**
- Primary code: `src/`, alongside `src/listhead.c`, because all tracked runtime logic currently lives there.
- Tests: `testdata/` for additional manual FITS fixtures; no automated test directory exists in the current layout.

**New Component/Module:**
- Implementation: `src/`; add new `.c` and accompanying `.h` files there and update `src/Makefile` so they are compiled into the executable.

**Utilities:**
- Shared helpers: `src/`; there is no dedicated `utils/` or `lib/` directory in the current repository.

## Special Directories

**`testdata/`:**
- Purpose: Manual sample corpus for exercising the CLI against real FITS headers.
- Generated: No
- Committed: Yes

**`.planning/codebase/`:**
- Purpose: Generated planning/reference docs for future automation.
- Generated: Yes
- Committed: No

**`.github/`:**
- Purpose: Placeholder for GitHub-specific repository automation.
- Generated: No
- Committed: Directory present, but no tracked files detected

**`src/`:**
- Purpose: Source and local build output directory.
- Generated: No for tracked files such as `src/listhead.c` and `src/Makefile`; yes for ignored artifacts such as `src/listhead.o`
- Committed: Yes for tracked source/build files; the current `src/listhead` binary is untracked

---

*Structure analysis: 2026-04-12*
