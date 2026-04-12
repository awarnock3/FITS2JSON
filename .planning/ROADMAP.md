# Roadmap: FITS2JSON

## Overview

This roadmap evolves the existing CFITSIO-based `listhead` utility into a single C program named `fits2json`, preserving the current FITS traversal workflow while replacing raw header dumps with deterministic, script-friendly JSON for selected HDUs and whole-file output.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Seam Extraction & Rename** - Rename the brownfield entry point while preserving current HDU-selection behavior. (completed 2026-04-12)
- [x] **Phase 2: Header Modeling for Selected HDU** - Deliver accurate structured JSON for one requested HDU. (completed 2026-04-12)
- [x] **Phase 3: Whole-File JSON Emission** - Extend JSON output to one document covering all HDUs by default. (completed 2026-04-12)
- [ ] **Phase 4: Verification & Build Cleanup** - Harden failure behavior and finalize repeatable delivery from the Makefile.

## Phase Details

### Phase 1: Seam Extraction & Rename
**Goal**: Users can enter the new `fits2json` code path without losing the existing CFITSIO extension-selection workflow.
**Depends on**: Nothing (first phase)
**Requirements**: BLD-02, HEAD-03
**Success Criteria** (what must be TRUE):
  1. User can invoke the renamed conversion path using the same FITS filename selectors already accepted today, including whole-file, numeric-extension, and named-extension forms.
  2. User can request a specific HDU through the renamed `fits2json` implementation entry point instead of `src/listhead.c`.
  3. User can stay on a single C implementation path with no wrapper script or second-language launcher introduced during the rename.
**Plans:** 1/1 plans complete
Plans:
- [ ] `01-01-PLAN.md` — Rename the single-file CLI entry point and Makefile target to `fits2json` while preserving CFITSIO selector behavior.

### Phase 2: Header Modeling for Selected HDU
**Goal**: Users can convert a selected HDU into accurate structured JSON without losing FITS header semantics.
**Depends on**: Phase 1
**Requirements**: HEAD-01, HEAD-04, HEAD-05, FITS-01, FITS-02, FITS-03, FITS-04
**Success Criteria** (what must be TRUE):
  1. User can convert a selected HDU and receive valid JSON on stdout instead of raw 80-character header cards.
  2. User can inspect structured keyword output with parsed values and FITS comments where those comments exist.
  3. User can see repeated `COMMENT` and `HISTORY` records preserved as arrays within the HDU output.
  4. User can observe original header order preserved and supported FITS edge cases such as long-string and extended-keyword records converted without corruption.
**Plans**: 1/1 complete

### Phase 3: Whole-File JSON Emission
**Goal**: Users can convert an entire FITS file into one JSON document that is safe to pipe into downstream tools.
**Depends on**: Phase 2
**Requirements**: HEAD-02, CLI-01
**Success Criteria** (what must be TRUE):
  1. User can omit the extension selector and receive one JSON document containing every HDU in file order.
  2. User can pipe successful command output directly into JSON-consuming shell tools without non-JSON text mixed into stdout.
  3. User can rely on a consistent top-level JSON document shape when converting complete FITS files.
**Plans**: TBD

### Phase 4: Verification & Build Cleanup
**Goal**: Users can build and automate `fits2json` with repeatable results and deterministic failure behavior.
**Depends on**: Phase 3
**Requirements**: CLI-02, CLI-03, BLD-01
**Success Criteria** (what must be TRUE):
  1. User can build the tool from `src/Makefile` as a single executable named `fits2json`.
  2. User receives diagnostics on stderr and a non-zero exit code when a FITS file cannot be opened or converted.
  3. User never receives partial or malformed JSON on stdout for failures detected before emission begins, and detectable stdout write failures still surface deterministic stderr diagnostics and a non-zero exit code.
  4. User gets the same output shape and failure behavior across repeated runs with the same input.
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Seam Extraction & Rename | 1/1 | Complete    | 2026-04-12 |
| 2. Header Modeling for Selected HDU | 1/1 | Complete    | 2026-04-12 |
| 3. Whole-File JSON Emission | 1/1 | Complete    | 2026-04-12 |
| 4. Verification & Build Cleanup | 0/TBD | Not started | - |
