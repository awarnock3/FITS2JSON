# Technology Stack

**Analysis Date:** 2026-04-12

## Languages

**Primary:**
- C (version not pinned in-repo) - the only implementation language in `src/listhead.c`

**Secondary:**
- Makefile syntax - build automation in `src/Makefile`

## Runtime

**Environment:**
- Native compiled CLI for Unix-like systems; the current built artifact `src/listhead` is an ELF 64-bit Linux executable
- POSIX APIs are requested at compile time via `-D_POSIX_C_SOURCE=200809L` in `src/Makefile`

**Package Manager:**
- None detected in `/home/warnock/dev/FITS2JSON`; no `package.json`, `go.mod`, `Cargo.toml`, `requirements.txt`, or `pyproject.toml`
- Lockfile: missing

## Frameworks

**Core:**
- CFITSIO (version not pinned in-repo; runtime system currently resolves `libcfitsio.so.10`) - FITS file access and header traversal from `src/listhead.c`

**Testing:**
- Not detected; no test runner config or automated test framework files are present under `/home/warnock/dev/FITS2JSON`

**Build/Dev:**
- GNU Make - single-target build orchestration in `src/Makefile`
- GCC - configured compiler in `src/Makefile` via `CC = gcc`

## Key Dependencies

**Critical:**
- CFITSIO - linked with `-lcfitsio` in `src/Makefile`; all FITS parsing in `src/listhead.c` goes through `fits_open_file`, `fits_get_hdrspace`, `fits_read_record`, and related APIs

**Infrastructure:**
- glibc - standard C runtime used by `src/listhead`
- libm - indirect runtime dependency of the built `src/listhead` binary
- zlib - indirect runtime dependency of the built `src/listhead` binary through CFITSIO

## Configuration

**Environment:**
- No environment-variable based configuration is implemented in `src/listhead.c`
- Input is provided only as a single command-line path argument in `src/listhead.c`
- Required local system setup is compile-time installation of CFITSIO headers in `/usr/local/include` and libraries in `/usr/local/lib`, as assumed by `src/Makefile`

**Build:**
- Build config is entirely in `src/Makefile`
- Ignore rules for compiled artifacts are in `.gitignore`
- Project intent is stated briefly in `README.md`

## Platform Requirements

**Development:**
- `make`
- `gcc`
- CFITSIO development headers available to `src/Makefile` at `/usr/local/include`
- CFITSIO shared library available to linker and runtime at `/usr/local/lib`

**Production:**
- Local command-line execution of the compiled `src/listhead` binary on a system with the CFITSIO shared library installed
- No server, container, or hosted deployment configuration is present in `/home/warnock/dev/FITS2JSON`

---

*Stack analysis: 2026-04-12*
