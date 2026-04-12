# Phase 3: Whole-File JSON Emission - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-12
**Phase:** 3-Whole-File JSON Emission
**Areas discussed:** Top-level whole-file JSON shape, selectorless vs explicit-selector relationship

---

## Top-level whole-file JSON shape

| Option | Description | Selected |
|--------|-------------|----------|
| An object with an `hdus` array of the existing Phase 2 HDU objects | Adds a wrapper object around the Phase 2 HDU contract | |
| A top-level array of HDU objects only | Keep whole-file output as a direct JSON array of Phase 2 HDU objects | ✓ |
| An object with `hdus` plus lightweight file metadata | Add a wrapper plus file-level metadata in Phase 3 | |
| You decide | Leave the exact whole-file wrapper open | |

**User's choice:** A top-level array of HDU objects only
**Notes:** Selectorless output should stay pipe-friendly and avoid a new wrapper object by default.

## Selectorless vs explicit-selector relationship

| Option | Description | Selected |
|--------|-------------|----------|
| Keep explicit selector mode as the existing single HDU object, and make selectorless mode return an array of HDU objects | Preserve the Phase 2 contract while adding whole-file output separately | ✓ |
| Unify both modes so even explicit selection returns a one-element array | Force one top-level shape for both invocation styles | |
| Keep defaults different now, and defer any schema-unification option to a later phase | Allow later revisit of schema unification | |
| You decide | Leave the relationship open | |

**User's choice:** Keep explicit selector mode as the existing single HDU object, and make selectorless mode return an array of HDU objects
**Notes:** Phase 3 should add selectorless array output without breaking the explicit-selector object contract from Phase 2.

---

## the agent's Discretion

- Exact internal extraction/reuse strategy for walking all HDUs while preserving the Phase 2 per-HDU contract
- Exact failure/cleanup flow for whole-file mode

## Deferred Ideas

- File-level metadata
- Schema unification between selectorless and explicit-selector modes
