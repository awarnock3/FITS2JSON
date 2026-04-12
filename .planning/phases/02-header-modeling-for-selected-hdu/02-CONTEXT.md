# Phase 2: Header Modeling for Selected HDU - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Convert a single selected HDU into valid JSON on stdout using the existing `fits2json` entry point and CFITSIO selector behavior preserved in Phase 1. This phase defines the selected-HDU JSON contract and internal header modeling needed to preserve order and FITS semantics; whole-file emission and alternate schema modes belong to later phases.

</domain>

<decisions>
## Implementation Decisions

### Selected-HDU JSON shape
- **D-01:** Emit one JSON object for the selected HDU rather than raw 80-character card text.
- **D-02:** The HDU JSON object should contain minimal top-level metadata: the HDU `index` and HDU `type`.
- **D-03:** Header content should be represented as an ordered `cards` array, not flattened into a keyword-only object.

### Card representation
- **D-04:** Each entry in `cards` should be a parsed card object with `keyword`, parsed `value` when present, and `comment` when present.
- **D-05:** Do not add raw card text to the default Phase 2 output contract; raw-card inclusion remains deferred unless a later phase or schema mode requires it.

### Scope guardrails
- **D-06:** Keep this phase focused on the selected-HDU contract only. Do not expand into whole-file top-level document design here.
- **D-07:** Preserve FITS semantics called out in requirements and research, especially record order and support for repeated or non-trivial records, while staying within a single C implementation.

### the agent's Discretion
- Exact internal helper boundaries needed to normalize CFITSIO header records into the ordered `cards` array
- Exact string values or enum-mapping used for the emitted HDU `type`
- Exact handling details for FITS records without parsed values, as long as the public contract above remains intact

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` — Phase 2 goal, requirement mapping, and success criteria
- `.planning/PROJECT.md` — locked project-level decisions, especially the single-C-program scope
- `.planning/REQUIREMENTS.md` — Phase 2 requirements `HEAD-01`, `HEAD-04`, `HEAD-05`, `FITS-01`, `FITS-02`, `FITS-03`, and `FITS-04`
- `.planning/STATE.md` — current milestone position and known blockers/concerns

### Prior-phase decisions to preserve
- `.planning/phases/01-seam-extraction-rename/01-CONTEXT.md` — keep the direct `fits2json` entry point, single-binary path, and narrow phase boundaries established in Phase 1

### Existing implementation and research
- `src/fits2json.c` — current single-file runtime flow that opens FITS files, resolves selectors, and iterates HDUs
- `.planning/research/SUMMARY.md` — recommended normalization pipeline and warnings against flattening headers or hand-parsing cards
- `.planning/codebase/ARCHITECTURE.md` — confirms current single-binary procedural structure
- `.planning/codebase/CONCERNS.md` — notes stdout purity and FITS edge-case risks relevant to JSON conversion

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/fits2json.c` already proves FITS open/select/traverse behavior and reads cards in original header order with CFITSIO
- Existing `fits_read_record` loop provides a stable traversal seam where Phase 2 can replace plain-text printing with structured modeling and JSON emission

### Established Patterns
- Single-file procedural CLI centered on `main`
- CFITSIO status-driven control flow with `fits_report_error(stderr, status)` for failures
- Current implementation distinguishes selected-HDU vs whole-file traversal using `single` and the existing selector logic

### Integration Points
- Header modeling work attaches directly to the per-card read loop in `src/fits2json.c`
- Selected-HDU JSON emission should use the current selector behavior without redesigning CLI syntax
- Planning should preserve stdout as the JSON channel and avoid mixing diagnostic text into successful output

</code_context>

<specifics>
## Specific Ideas

- Use an HDU object shaped roughly as:

```json
{
  "index": 1,
  "type": "IMAGE_HDU",
  "cards": [
    { "keyword": "SIMPLE", "value": true, "comment": "file conforms to FITS standard" }
  ]
}
```

- Prefer the `cards` array as the canonical schema because it preserves order and repeated records naturally.
- Keep metadata intentionally small in Phase 2: `index` and `type` only.

</specifics>

<deferred>
## Deferred Ideas

- Alternate schema modes such as grouped keyword objects
- Including raw 80-character card text in default output
- Whole-file top-level JSON document design
- Richer HDU metadata beyond `index` and `type`

</deferred>

---

*Phase: 02-header-modeling-for-selected-hdu*
*Context gathered: 2026-04-12*
