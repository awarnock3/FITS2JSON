# Phase 3: Whole-File JSON Emission - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Extend `fits2json` so selectorless invocation converts the full FITS file into one JSON document that is safe to pipe into downstream tools. This phase is only about whole-file wrapping and multi-HDU traversal on top of the Phase 2 selected-HDU contract; it must not redesign the per-HDU object shape already established in Phase 2.

</domain>

<decisions>
## Implementation Decisions

### Whole-file top-level shape
- **D-01:** When no selector is given, emit a top-level JSON array of HDU objects.
- **D-02:** Each array element should reuse the existing Phase 2 HDU object contract rather than introducing a second per-HDU schema.

### Relationship to selected-HDU mode
- **D-03:** Keep explicit selector mode unchanged: it should continue to emit the existing single HDU object from Phase 2.
- **D-04:** Phase 3 is additive: selectorless mode returns an array, while explicit selector mode remains a single object.

### Scope guardrails
- **D-05:** Do not add file-level metadata to the default Phase 3 output unless planning proves it is strictly required to satisfy the phase goal.
- **D-06:** Preserve stdout purity so selectorless whole-file output remains directly pipeable into JSON-consuming tools.

### the agent's Discretion
- Exact helper boundaries for iterating all HDUs while reusing the Phase 2 selected-HDU model/emitter seams
- Exact internal error-handling flow needed to avoid partial selectorless output on failure
- Exact reuse/extraction strategy for producing either a single object or top-level array without duplicating logic

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` — Phase 3 goal, requirement mapping, and success criteria
- `.planning/PROJECT.md` — locked project-level constraints, especially the single-C-program scope
- `.planning/REQUIREMENTS.md` — Phase 3 requirements `HEAD-02` and `CLI-01`
- `.planning/STATE.md` — current milestone position and handoff state after Phase 2 completion

### Prior-phase decisions to preserve
- `.planning/phases/02-header-modeling-for-selected-hdu/02-CONTEXT.md` — locked single-HDU JSON contract and deferred whole-file design
- `.planning/phases/02-header-modeling-for-selected-hdu/02-01-SUMMARY.md` — execution summary for the selected-HDU model
- `.planning/phases/02-header-modeling-for-selected-hdu/02-VERIFICATION.md` — evidence that the Phase 2 HDU contract is stable enough to wrap for whole-file mode

### Existing implementation
- `src/fits2json.c` — current selected-HDU JSON implementation and selectorless guardrail that Phase 3 will replace
- `.planning/research/SUMMARY.md` — project-level recommendation that the default no-selector mode should emit one document containing all HDUs

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/fits2json.c` already builds one HDU model in memory and emits the locked Phase 2 object shape
- Existing CFITSIO open/selector flow still provides the seam needed to distinguish explicit selection from selectorless traversal

### Established Patterns
- Single-file procedural CLI centered on `main`
- Close-before-emit discipline to keep stdout clean on failure
- Ordered card modeling is already solved for one HDU and should be reused, not redesigned

### Integration Points
- Phase 3 work should reuse the selected-HDU read/model path for each HDU in file order
- Selectorless mode must re-enter HDU traversal without changing explicit selector behavior
- Whole-file output must remain pure JSON on stdout with no extra banner/help text mixed in

</code_context>

<specifics>
## Specific Ideas

- Selectorless mode should produce a document shaped roughly as:

```json
[
  { "index": 1, "type": "IMAGE_HDU", "cards": [...] },
  { "index": 2, "type": "BINARY_TBL", "cards": [...] }
]
```

- Explicit selector mode should continue to produce exactly one HDU object, not a one-element array.
- File-level metadata is intentionally deferred unless planning finds a phase-goal reason it must exist.

</specifics>

<deferred>
## Deferred Ideas

- Adding filename or other file-level metadata to the default top-level document
- Unifying selected-HDU and selectorless modes under one schema
- Alternate schema modes beyond the Phase 2 ordered-card contract

</deferred>

---

*Phase: 03-whole-file-json-emission*
*Context gathered: 2026-04-12*
