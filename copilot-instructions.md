<!-- GSD:project-start source:PROJECT.md -->
## Project

**FITS2JSON**

FITS2JSON is a single C command-line program for reading FITS headers and emitting them as structured JSON instead of raw terminal text. It evolves the existing `src/listhead.c` CFITSIO-based implementation into a renamed `fits2json` program rather than introducing a wrapper script or a second runtime.

**Core Value:** Given a FITS file path, the tool must produce reliable machine-readable JSON for header metadata with as little friction as the current header-dumping workflow.

### Constraints

- **Tech stack**: C with CFITSIO — the existing code and requested starting point are both built around `src/listhead.c` and `fitsio.h`
- **Interface**: CLI stdout output — the tool remains a native command-line program, not an interactive UI or wrapper script
- **Architecture**: Brownfield single-binary program — changes should fit the current procedural layout before any broader refactor
- **Data scope**: FITS headers only — no requirement to serialize image/table payload contents
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- C (version not pinned in-repo) - the only implementation language in `src/listhead.c`
- Makefile syntax - build automation in `src/Makefile`
## Runtime
- Native compiled CLI for Unix-like systems; the current built artifact `src/listhead` is an ELF 64-bit Linux executable
- POSIX APIs are requested at compile time via `-D_POSIX_C_SOURCE=200809L` in `src/Makefile`
- None detected in `/home/warnock/dev/FITS2JSON`; no `package.json`, `go.mod`, `Cargo.toml`, `requirements.txt`, or `pyproject.toml`
- Lockfile: missing
## Frameworks
- CFITSIO (version not pinned in-repo; runtime system currently resolves `libcfitsio.so.10`) - FITS file access and header traversal from `src/listhead.c`
- Not detected; no test runner config or automated test framework files are present under `/home/warnock/dev/FITS2JSON`
- GNU Make - single-target build orchestration in `src/Makefile`
- GCC - configured compiler in `src/Makefile` via `CC = gcc`
## Key Dependencies
- CFITSIO - linked with `-lcfitsio` in `src/Makefile`; all FITS parsing in `src/listhead.c` goes through `fits_open_file`, `fits_get_hdrspace`, `fits_read_record`, and related APIs
- glibc - standard C runtime used by `src/listhead`
- libm - indirect runtime dependency of the built `src/listhead` binary
- zlib - indirect runtime dependency of the built `src/listhead` binary through CFITSIO
## Configuration
- No environment-variable based configuration is implemented in `src/listhead.c`
- Input is provided only as a single command-line path argument in `src/listhead.c`
- Required local system setup is compile-time installation of CFITSIO headers in `/usr/local/include` and libraries in `/usr/local/lib`, as assumed by `src/Makefile`
- Build config is entirely in `src/Makefile`
- Ignore rules for compiled artifacts are in `.gitignore`
- Project intent is stated briefly in `README.md`
## Platform Requirements
- `make`
- `gcc`
- CFITSIO development headers available to `src/Makefile` at `/usr/local/include`
- CFITSIO shared library available to linker and runtime at `/usr/local/lib`
- Local command-line execution of the compiled `src/listhead` binary on a system with the CFITSIO shared library installed
- No server, container, or hosted deployment configuration is present in `/home/warnock/dev/FITS2JSON`
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Use lowercase source filenames with no separators for the single-purpose CLI translation unit in `src/listhead.c`.
- Keep build configuration in conventional tool names such as `src/Makefile`.
- Use lower_snake_case for external library calls from CFITSIO, as seen with `fits_open_file`, `fits_get_hdu_num`, and `fits_report_error` in `src/listhead.c`.
- Keep local program entry points minimal and procedural; `src/listhead.c` exposes only `main`.
- Use short lowercase local names for loop counters and status plumbing, such as `status`, `single`, `hdupos`, `nkeys`, and `ii` in `src/listhead.c`.
- Use pointer abbreviations for library-owned handles, such as `fptr` in `src/listhead.c`.
- Prefer library-provided C types directly instead of project-defined wrappers, e.g. `fitsfile *` and `char card[FLEN_CARD]` in `src/listhead.c`.
- No custom structs, enums, or typedef naming conventions are established outside CFITSIO types in `src/listhead.c`.
## Code Style
- Formatting tool configuration is not detected; no `.clang-format`, `.editorconfig`, `.prettierrc`, or equivalent file is present at the repository root.
- Match the existing manual C style in `src/listhead.c`: opening braces usually appear on the next line for functions and multi-line control blocks, and indentation is space-based with some nested blocks using two-space increments.
- Keep include directives grouped with system headers first and the local third-party header last, as in `src/listhead.c`.
- Dedicated lint configuration is not detected.
- Compiler warnings are the closest enforced style gate: `src/Makefile` builds with `-Wall -O2 -D_POSIX_C_SOURCE=200809L`.
## Import Organization
- Not detected. Includes in `src/listhead.c` use direct header names only.
## Error Handling
- Thread CFITSIO error state through an integer `status` variable initialized to zero in `src/listhead.c`.
- Gate follow-up operations on library success, e.g. `if (!fits_open_file(..., &status))` in `src/listhead.c`.
- Normalize expected terminal conditions before exit, e.g. `if (status == END_OF_FILE) status = 0;` in `src/listhead.c`.
- Delegate final error rendering to the library with `fits_report_error(stderr, status)` in `src/listhead.c`.
- Return process status codes directly from `main`, including the usage path `return(0);` and the final `return(status);` in `src/listhead.c`.
## Logging
- Use `printf` for user-facing CLI output, including usage guidance and emitted FITS header records in `src/listhead.c`.
- Reserve `stderr` output for library-generated error details through `fits_report_error` in `src/listhead.c`.
- No structured logging, debug logger, or verbosity flag is implemented outside `src/listhead.c`.
## Comments
- Add short block comments to explain CFITSIO-specific behavior or control-flow intent, such as the comments on `status`, header iteration, and single-extension handling in `src/listhead.c`.
- Keep comments close to the line they clarify instead of using large file headers; `src/listhead.c` relies on inline comments only.
- Not applicable. The repository is C-based, and no API documentation block style is established in `src/listhead.c` or `src/Makefile`.
## Function Design
## Module Design
## Repository-Specific Conventions
- Build from `src/Makefile` rather than a root-level build script.
- Link against CFITSIO from conventional local paths using `-I/usr/local/include` and `-L/usr/local/lib` in `src/Makefile`.
- Treat generated artifacts as disposable local outputs: `.gitignore` excludes object files and executables, and `src/listhead.o` plus `src/listhead` are build products of `src/Makefile`.
- Use sample FITS header files in `testdata/*.HDR` as manual verification fixtures for the CLI in `src/listhead.c`.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Runtime logic is concentrated in one translation unit: `src/listhead.c`.
- Build orchestration is isolated to a single make target in `src/Makefile`.
- FITS parsing is delegated to CFITSIO calls in `src/listhead.c`; the repository does not contain an internal parsing layer, JSON serializer, or service boundary.
## Layers
- Purpose: Accept a FITS filename from the shell, print usage help, and start header listing.
- Location: `src/listhead.c`
- Contains: `main`, argument count validation, usage text, process exit code selection.
- Depends on: Standard C I/O from `stdio.h`, string checks from `string.h`, and CFITSIO declarations from `fitsio.h`.
- Used by: The compiled `listhead` executable produced by `src/Makefile`.
- Purpose: Open FITS files, inspect HDU position, count header records, and iterate records.
- Location: `src/listhead.c`
- Contains: Calls to `fits_open_file`, `fits_get_hdu_num`, `fits_get_hdrspace`, `fits_read_record`, `fits_movrel_hdu`, and `fits_close_file`.
- Depends on: External CFITSIO shared library linked by `src/Makefile`.
- Used by: The CLI control flow in `main` inside `src/listhead.c`.
- Purpose: Emit header listings and error messages directly to standard streams.
- Location: `src/listhead.c`
- Contains: `printf` output for header cards and `fits_report_error(stderr, status)` for failures.
- Depends on: State gathered by the FITS access loop in `src/listhead.c`.
- Used by: End users invoking `./src/listhead` against files such as `testdata/IRPH0189.HDR`.
- Purpose: Compile and link the executable.
- Location: `src/Makefile`
- Contains: Compiler flags, object-file rule, `all`, `clean`, and `listhead` targets.
- Depends on: `gcc`, headers in `/usr/local/include`, and `libcfitsio` in `/usr/local/lib`.
- Used by: Developers building from `src/` with `make`.
## Data Flow
- All state is function-local inside `main` in `src/listhead.c`: `status`, `single`, `hdupos`, `nkeys`, `ii`, `card`, and `fitsfile *fptr`.
- No heap-managed domain objects, shared mutable module state, or persisted application state are present outside the running process.
## Key Abstractions
- Purpose: Represent the currently opened FITS resource.
- Examples: `fitsfile *fptr` in `src/listhead.c`
- Pattern: Opaque library handle managed by CFITSIO open/read/close functions.
- Purpose: Walk through one or more header-data units in sequence.
- Examples: The `for (; !status; hdupos++)` loop in `src/listhead.c`
- Pattern: Status-driven iteration controlled by CFITSIO return codes rather than custom iterator types.
- Purpose: Hold one FITS header record before printing.
- Examples: `char card[FLEN_CARD]` in `src/listhead.c`
- Pattern: Fixed-size stack buffer defined by the CFITSIO constant `FLEN_CARD`.
## Entry Points
- Location: `src/listhead.c`
- Triggers: Direct shell invocation of the compiled binary, for example `./src/listhead testdata/IRPH0189.HDR`.
- Responsibilities: Validate input, open the FITS file, stream header lines, and return a process status code.
- Location: `src/Makefile`
- Triggers: Running `make` inside `src/`.
- Responsibilities: Compile `src/listhead.c` into `listhead.o`, link the `listhead` executable, and clean generated build artifacts.
- Location: `README.md`
- Triggers: Repository discovery from the project root.
- Responsibilities: State the project purpose at a high level; detailed runtime or build guidance is not present there.
## Error Handling
- `src/listhead.c` initializes `status` to `0` and passes it through every CFITSIO call.
- `src/listhead.c` treats `END_OF_FILE` as a normal termination condition by resetting `status` back to `0`.
- `src/listhead.c` exits early with usage text when `argc != 2`.
- `src/listhead.c` reports library-generated diagnostics with `fits_report_error(stderr, status)` instead of building custom error objects or messages.
## Cross-Cutting Concerns
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.github/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
