# Architecture

**Analysis Date:** 2026-04-12

## Pattern Overview

**Overall:** Single-binary procedural CLI around the CFITSIO C library.

**Key Characteristics:**
- Runtime logic is concentrated in one translation unit: `src/listhead.c`.
- Build orchestration is isolated to a single make target in `src/Makefile`.
- FITS parsing is delegated to CFITSIO calls in `src/listhead.c`; the repository does not contain an internal parsing layer, JSON serializer, or service boundary.

## Layers

**CLI Entry Layer:**
- Purpose: Accept a FITS filename from the shell, print usage help, and start header listing.
- Location: `src/listhead.c`
- Contains: `main`, argument count validation, usage text, process exit code selection.
- Depends on: Standard C I/O from `stdio.h`, string checks from `string.h`, and CFITSIO declarations from `fitsio.h`.
- Used by: The compiled `listhead` executable produced by `src/Makefile`.

**FITS Access Layer:**
- Purpose: Open FITS files, inspect HDU position, count header records, and iterate records.
- Location: `src/listhead.c`
- Contains: Calls to `fits_open_file`, `fits_get_hdu_num`, `fits_get_hdrspace`, `fits_read_record`, `fits_movrel_hdu`, and `fits_close_file`.
- Depends on: External CFITSIO shared library linked by `src/Makefile`.
- Used by: The CLI control flow in `main` inside `src/listhead.c`.

**Output Layer:**
- Purpose: Emit header listings and error messages directly to standard streams.
- Location: `src/listhead.c`
- Contains: `printf` output for header cards and `fits_report_error(stderr, status)` for failures.
- Depends on: State gathered by the FITS access loop in `src/listhead.c`.
- Used by: End users invoking `./src/listhead` against files such as `testdata/IRPH0189.HDR`.

**Build Layer:**
- Purpose: Compile and link the executable.
- Location: `src/Makefile`
- Contains: Compiler flags, object-file rule, `all`, `clean`, and `listhead` targets.
- Depends on: `gcc`, headers in `/usr/local/include`, and `libcfitsio` in `/usr/local/lib`.
- Used by: Developers building from `src/` with `make`.

## Data Flow

**FITS Header Listing Flow:**

1. `main` in `src/listhead.c` validates that exactly one CLI argument was passed; otherwise it prints usage help and exits.
2. `fits_open_file` in `src/listhead.c` opens the FITS file path from `argv[1]` and initializes a `fitsfile *` handle.
3. `fits_get_hdu_num` and the `single` flag logic in `src/listhead.c` decide whether to list one HDU or iterate through all HDUs.
4. The outer loop in `src/listhead.c` calls `fits_get_hdrspace` to count header records for the current HDU.
5. The inner loop in `src/listhead.c` calls `fits_read_record` for each card and prints each raw FITS header line with `printf`.
6. `fits_movrel_hdu` in `src/listhead.c` advances to the next HDU until EOF or until a single requested extension has been handled.
7. `fits_close_file` in `src/listhead.c` releases the file handle, and `fits_report_error` writes any non-zero CFITSIO status to `stderr`.

**State Management:**
- All state is function-local inside `main` in `src/listhead.c`: `status`, `single`, `hdupos`, `nkeys`, `ii`, `card`, and `fitsfile *fptr`.
- No heap-managed domain objects, shared mutable module state, or persisted application state are present outside the running process.

## Key Abstractions

**FITS File Handle:**
- Purpose: Represent the currently opened FITS resource.
- Examples: `fitsfile *fptr` in `src/listhead.c`
- Pattern: Opaque library handle managed by CFITSIO open/read/close functions.

**HDU Iteration Loop:**
- Purpose: Walk through one or more header-data units in sequence.
- Examples: The `for (; !status; hdupos++)` loop in `src/listhead.c`
- Pattern: Status-driven iteration controlled by CFITSIO return codes rather than custom iterator types.

**Header Card Buffer:**
- Purpose: Hold one FITS header record before printing.
- Examples: `char card[FLEN_CARD]` in `src/listhead.c`
- Pattern: Fixed-size stack buffer defined by the CFITSIO constant `FLEN_CARD`.

## Entry Points

**Runtime Entry Point:**
- Location: `src/listhead.c`
- Triggers: Direct shell invocation of the compiled binary, for example `./src/listhead testdata/IRPH0189.HDR`.
- Responsibilities: Validate input, open the FITS file, stream header lines, and return a process status code.

**Build Entry Point:**
- Location: `src/Makefile`
- Triggers: Running `make` inside `src/`.
- Responsibilities: Compile `src/listhead.c` into `listhead.o`, link the `listhead` executable, and clean generated build artifacts.

**Documentation Entry Point:**
- Location: `README.md`
- Triggers: Repository discovery from the project root.
- Responsibilities: State the project purpose at a high level; detailed runtime or build guidance is not present there.

## Error Handling

**Strategy:** Use CFITSIO integer status codes as the single error signal and defer detailed reporting to CFITSIO itself.

**Patterns:**
- `src/listhead.c` initializes `status` to `0` and passes it through every CFITSIO call.
- `src/listhead.c` treats `END_OF_FILE` as a normal termination condition by resetting `status` back to `0`.
- `src/listhead.c` exits early with usage text when `argc != 2`.
- `src/listhead.c` reports library-generated diagnostics with `fits_report_error(stderr, status)` instead of building custom error objects or messages.

## Cross-Cutting Concerns

**Logging:** No dedicated logging framework is present; `src/listhead.c` writes normal output with `printf` and errors to `stderr`.
**Validation:** Input validation is minimal and limited to argument count checks in `src/listhead.c`; file format validation is delegated to CFITSIO.
**Authentication:** Not applicable; the code in `src/listhead.c` reads local FITS files only.

---

*Architecture analysis: 2026-04-12*
