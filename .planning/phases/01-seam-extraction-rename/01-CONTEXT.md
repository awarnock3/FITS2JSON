# Phase 1: Seam Extraction & Rename - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Rename the existing brownfield CLI entry point from `listhead` to `fits2json` while preserving the current CFITSIO extension-selection workflow. This phase is about the rename seam and invocation continuity only; JSON transformation behavior belongs in later phases.

</domain>

<decisions>
## Implementation Decisions

### Rename compatibility
- **D-01:** Build only `fits2json` after the rename. Do not keep `listhead` as a compatibility alias.
- **D-02:** Rename `src/listhead.c` directly to `src/fits2json.c` with no temporary wrapper or forwarding shim.
- **D-03:** Switch user-facing usage/help/examples fully to `fits2json`; do not mention `listhead` in normal CLI guidance after the rename.

### Code structure during rename
- **D-04:** Keep Phase 1 to minimal seam extraction only. Do not do broader refactors beyond what is needed to support the rename cleanly and preserve selector behavior.

### the agent's Discretion
- Exact small helper boundaries, if any, needed to make the rename clean without expanding scope
- Minor Makefile cleanups that are directly required for the rename path

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` — Phase 1 goal, requirement mapping, and success criteria
- `.planning/PROJECT.md` — locked project-level decisions, especially single-C-program scope and rename intent
- `.planning/REQUIREMENTS.md` — Phase 1 requirements `BLD-02` and `HEAD-03`
- `.planning/STATE.md` — current milestone position and known blockers/concerns

### Existing implementation and build entry points
- `src/listhead.c` — current CLI entry point and CFITSIO selector behavior that must be preserved through the rename
- `src/Makefile` — current build target and executable naming that must transition to `fits2json`

### Codebase guidance
- `.planning/codebase/ARCHITECTURE.md` — confirms the current single-binary procedural design centered on `src/listhead.c`
- `.planning/codebase/CONCERNS.md` — identifies build drift and Makefile fragility relevant to rename planning
- `.planning/codebase/CONVENTIONS.md` — current C style, naming, and Makefile conventions
- `.planning/codebase/STRUCTURE.md` — current `src/`-centric repository layout and where renamed code should live

### Phase research
- `.planning/research/SUMMARY.md` — recommended build order and warning to keep early work narrow before JSON behavior phases

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/listhead.c`: the only runtime implementation; already proves FITS file opening, selector handling, HDU traversal, and CFITSIO status flow
- `src/Makefile`: the only build entry point; already defines the compiler, object build rule, and executable target that must be renamed

### Established Patterns
- Single-file procedural CLI centered on `main` in `src/listhead.c`
- CFITSIO status-driven flow with direct library calls and `fits_report_error(stderr, status)` for failures
- Build from `src/Makefile`, not a root-level build script

### Integration Points
- Runtime rename work connects at `src/listhead.c` / future `src/fits2json.c`
- Build rename work connects at `src/Makefile` target, source list, object naming, and clean target
- Existing selector behavior depends on current argument handling and `fits_open_file` / `fits_get_hdu_num` flow in the runtime entry point

</code_context>

<specifics>
## Specific Ideas

- The executable should become `fits2json` immediately rather than carrying a temporary `listhead` alias.
- The source file should be renamed directly to `src/fits2json.c`.
- Phase 1 should stay narrow and avoid broad restructuring before the JSON work in later phases.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-seam-extraction-rename*
*Context gathered: 2026-04-12*
