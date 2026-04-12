# FITS2JSON

## What This Is

FITS2JSON is a single C command-line program for reading FITS headers and emitting them as structured JSON instead of raw terminal text. It evolves the existing `src/listhead.c` CFITSIO-based implementation into a renamed `fits2json` program rather than introducing a wrapper script or a second runtime.

## Core Value

Given a FITS file path, the tool must produce reliable machine-readable JSON for header metadata with as little friction as the current header-dumping workflow.

## Requirements

### Validated

- ✓ User can pass a FITS filename or extension selector and the CLI opens the file through CFITSIO — existing
- ✓ User can read header records from a specific HDU or iterate all HDUs when no extension is specified — existing
- ✓ User can inspect raw FITS header content from the terminal via the current CLI flow — existing

### Active

- [ ] User can emit FITS header metadata as valid JSON to stdout instead of raw header cards
- [ ] User can receive one JSON document containing all HDUs when no extension is specified
- [ ] User can receive structured keyword output per HDU rather than raw card strings
- [ ] User can preserve repeated or non-key/value records like `COMMENT` and `HISTORY` as arrays within each HDU
- [ ] User can build and run the tool as a single C program named `fits2json`

### Out of Scope

- Converting FITS data payloads beyond header units — current scope is header metadata only
- Building a GUI, service, or non-CLI interface — the existing codebase is a native command-line utility
- Adding a wrapper script or second implementation language — the user wants the current C program evolved in place
- Replacing CFITSIO with a custom FITS parser — the project should build on the proven library already in use

## Context

The repository already contains a small brownfield C codebase centered on `src/listhead.c`, which opens a FITS file with CFITSIO and prints header cards for one or more HDUs. The stated project goal in `README.md` is JSON translation, but that behavior is not yet implemented. The codebase map shows a single-binary procedural design, no automated tests, and a `src/Makefile` that currently handles the CFITSIO dependency through `/usr/local/include` and `/usr/local/lib`.

The immediate feature direction is to keep the existing FITS traversal behavior and change the output layer from raw card dumps to structured JSON. The user explicitly wants `src/listhead.c` used as the starting point, renamed to `src/fits2json.c`, and expects the implementation to stay in a single C program built by the existing `src/Makefile`.

## Constraints

- **Tech stack**: C with CFITSIO — the existing code and requested starting point are both built around `src/listhead.c` and `fitsio.h`
- **Interface**: CLI stdout output — the tool remains a native command-line program, not an interactive UI or wrapper script
- **Architecture**: Brownfield single-binary program — changes should fit the current procedural layout before any broader refactor
- **Data scope**: FITS headers only — no requirement to serialize image/table payload contents

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Emit structured keywords per HDU instead of raw header cards | The user wants machine-readable JSON rather than a textual header dump | — Pending |
| Output all HDUs in one JSON document when no extension is specified | This preserves the current multi-HDU traversal behavior in a script-friendly format | — Pending |
| Represent repeated/non-key/value records like `COMMENT` and `HISTORY` as arrays | FITS headers can contain repeated informational records that should not be discarded | — Pending |
| Build from the existing `src/listhead.c` and CFITSIO flow | The repository already proves FITS header traversal through this path, reducing implementation risk | — Pending |
| Keep the implementation as a single C program renamed to `fits2json` | The user wants the current program evolved in place, not wrapped by scripts or split into a separate runtime | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-12 after initialization*
