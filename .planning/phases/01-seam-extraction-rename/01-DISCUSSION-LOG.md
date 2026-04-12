# Phase 1: Seam Extraction & Rename - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-12
**Phase:** 1-Seam Extraction & Rename
**Areas discussed:** Rename compatibility

---

## Rename compatibility

| Option | Description | Selected |
|--------|-------------|----------|
| Only build `fits2json` | Rename the executable fully in this phase and drop `listhead` as a build target | ✓ |
| Build `fits2json` and keep `listhead` as a temporary compatibility alias | Preserve the old command name during a transition window | |
| Keep the executable named `listhead` for now and only rename the source file | Delay the command rename while changing only internals | |
| You decide | Leave the exact compatibility approach open to planning | |

**User's choice:** Only build `fits2json`
**Notes:** The rename should be real, not a transition alias.

| Option | Description | Selected |
|--------|-------------|----------|
| Rename `src/listhead.c` directly to `src/fits2json.c` with no compatibility shim | Clean direct rename of the source file | ✓ |
| Keep `src/listhead.c` as a thin wrapper that forwards to renamed code temporarily | Preserve the old filename briefly while new code is introduced | |
| You decide | Leave the source rename mechanics open | |

**User's choice:** Rename `src/listhead.c` directly to `src/fits2json.c` with no compatibility shim
**Notes:** No wrapper file should survive Phase 1.

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal seam extraction only | Keep the phase narrow and avoid broad refactors | ✓ |
| Rename plus small helper extraction if it improves Phase 2 handoff | Allow a little cleanup while renaming | |
| You decide | Leave the refactor depth open | |

**User's choice:** Minimal seam extraction only
**Notes:** Structural cleanup should stay minimal until later phases.

| Option | Description | Selected |
|--------|-------------|----------|
| Only `fits2json` in usage and examples | Rewrite help text and examples fully to the new name | ✓ |
| Mention both `fits2json` and legacy `listhead` during transition | Explain both names in CLI help temporarily | |
| You decide | Leave help wording open | |

**User's choice:** Only `fits2json` in usage and examples
**Notes:** User-facing guidance should not mention `listhead` after the rename.

---

## the agent's Discretion

- Exact small helper extraction, if any, needed to support the rename cleanly

## Deferred Ideas

None.
