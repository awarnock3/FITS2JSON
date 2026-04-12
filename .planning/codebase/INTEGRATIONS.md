# External Integrations

**Analysis Date:** 2026-04-12

## APIs & External Services

**Scientific file format library:**
- CFITSIO - used to open FITS files and iterate HDUs/header records in `src/listhead.c`
  - SDK/Client: system C library exposed through `fitsio.h` and linked as `-lcfitsio` in `src/Makefile`
  - Auth: Not applicable

**Networked services:**
- None detected in `src/listhead.c`, `src/Makefile`, or `README.md`

## Data Storage

**Databases:**
- None detected
  - Connection: Not applicable
  - Client: Not applicable

**File Storage:**
- Local filesystem only
- The executable in `src/listhead` reads a user-supplied FITS path from the command line in `src/listhead.c`
- Sample FITS header fixtures are stored in `testdata/*.HDR`, for example `testdata/IRPH0189.HDR`

**Caching:**
- None

## Authentication & Identity

**Auth Provider:**
- None
  - Implementation: No authentication or identity flow is implemented in `src/listhead.c`

## Monitoring & Observability

**Error Tracking:**
- None

**Logs:**
- Standard output and standard error only
- Normal header output is printed with `printf` in `src/listhead.c`
- FITS/CFITSIO failures are surfaced with `fits_report_error(stderr, status)` in `src/listhead.c`

## CI/CD & Deployment

**Hosting:**
- Not applicable; this repository builds a local CLI binary from `src/Makefile`

**CI Pipeline:**
- None detected; `.github/` contains no workflow files and no other CI config files are present at `/home/warnock/dev/FITS2JSON`

## Environment Configuration

**Required env vars:**
- None detected

**Secrets location:**
- Not applicable; no secret-managed integrations are implemented in `src/listhead.c` or `src/Makefile`

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## File Formats & System Integrations

**Primary file format:**
- FITS - the program reads FITS headers and extension headers using CFITSIO in `src/listhead.c`
- Supported selector syntax is passed directly in the input filename argument, including examples like `file.fits[0]`, `file.fits[2]`, `file.fits+2`, and `file.fits[GTI]` documented in `src/listhead.c`

**Output format:**
- Plain-text FITS header card listing to stdout from `src/listhead.c`
- JSON serialization is not implemented anywhere under `/home/warnock/dev/FITS2JSON`

**System library integration:**
- The build expects CFITSIO headers in `/usr/local/include` and libraries in `/usr/local/lib` as hardcoded in `src/Makefile`

---

*Integration audit: 2026-04-12*
