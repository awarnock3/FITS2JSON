# Requirements: FITS2JSON

**Defined:** 2026-04-12
**Core Value:** Given a FITS file path, the tool must produce reliable machine-readable JSON for header metadata with as little friction as the current header-dumping workflow.

## v1 Requirements

### Header Output

- [ ] **HEAD-01**: User can convert FITS header metadata to valid JSON on stdout
- [ ] **HEAD-02**: User can receive one JSON document containing all HDUs when no extension is specified
- [ ] **HEAD-03**: User can request a specific HDU using the existing FITS extension selection syntax already accepted by CFITSIO
- [ ] **HEAD-04**: User can receive structured keyword output for each HDU instead of raw 80-character header cards
- [ ] **HEAD-05**: User can receive keyword comments alongside parsed values where FITS provides them

### FITS Fidelity

- [ ] **FITS-01**: User can preserve repeated `COMMENT` records as arrays within each HDU
- [ ] **FITS-02**: User can preserve repeated `HISTORY` records as arrays within each HDU
- [ ] **FITS-03**: User can receive deterministic output that preserves the original header record order within each HDU
- [ ] **FITS-04**: User can convert headers without corrupting supported FITS edge cases such as long-string and extended-keyword records

### CLI Reliability

- [ ] **CLI-01**: User can pipe successful command output directly into JSON-consuming shell tools without non-JSON text mixed into stdout
- [ ] **CLI-02**: User receives diagnostics on stderr and a non-zero exit code when the FITS file cannot be opened or converted
- [ ] **CLI-03**: User can rely on deterministic output shape and failure behavior across repeated runs

### Build and Packaging

- [ ] **BLD-01**: User can build the tool from `src/Makefile` as a single C program named `fits2json`
- [ ] **BLD-02**: User can use the renamed source file `src/fits2json.c` as the implementation entry point for the conversion tool

## v2 Requirements

### Filtering and Schemas

- **FLTR-01**: User can filter output to selected keywords or wildcard patterns
- **SCMA-01**: User can choose between multiple output schemas such as grouped keywords vs ordered cards
- **SCMA-02**: User can include raw card text alongside parsed values for debugging or lossless inspection

## Out of Scope

| Feature | Reason |
|---------|--------|
| FITS image/table payload conversion | Current scope is header metadata only |
| Writing or modifying FITS files | The project is a read-only inspection/conversion tool |
| Replacing CFITSIO with a custom parser | Existing proven dependency already covers FITS parsing needs |
| Wrapper scripts or a second implementation language | The tool should remain a single C program built from `src/Makefile` |
| GUI or service interface | The current project and target workflow are CLI-first |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| HEAD-01 | Phase TBD | Pending |
| HEAD-02 | Phase TBD | Pending |
| HEAD-03 | Phase TBD | Pending |
| HEAD-04 | Phase TBD | Pending |
| HEAD-05 | Phase TBD | Pending |
| FITS-01 | Phase TBD | Pending |
| FITS-02 | Phase TBD | Pending |
| FITS-03 | Phase TBD | Pending |
| FITS-04 | Phase TBD | Pending |
| CLI-01 | Phase TBD | Pending |
| CLI-02 | Phase TBD | Pending |
| CLI-03 | Phase TBD | Pending |
| BLD-01 | Phase TBD | Pending |
| BLD-02 | Phase TBD | Pending |

**Coverage:**
- v1 requirements: 14 total
- Mapped to phases: 0
- Unmapped: 14 ⚠️

---
*Requirements defined: 2026-04-12*
*Last updated: 2026-04-12 after initial definition*
