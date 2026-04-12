# Phase 2: Header Modeling for Selected HDU - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-12
**Phase:** 2-Header Modeling for Selected HDU
**Areas discussed:** JSON shape for one HDU

---

## JSON shape for one HDU

| Option | Description | Selected |
|--------|-------------|----------|
| An HDU object with `index`, metadata, and a `cards` array | Preserve order and repeated records directly in the public schema | ✓ |
| An HDU object with a `keywords` object only | Simpler flattened schema with weaker fidelity for repeats/order | |
| Both `cards` and `keywords` views in the same output | Offer multiple views in the default schema | |
| You decide | Leave the exact public shape open | |

**User's choice:** An HDU object with `index`, metadata, and a `cards` array
**Notes:** The ordered `cards` array should be the canonical representation for Phase 2.

| Option | Description | Selected |
|--------|-------------|----------|
| Just `index` and HDU type | Keep top-level metadata minimal in Phase 2 | ✓ |
| `index`, HDU type, and extension name when present | Add lightweight identity metadata | |
| A richer metadata block if it can be obtained cleanly | Expand scope to broader HDU description | |
| You decide | Leave metadata breadth open | |

**User's choice:** Just `index` and HDU type
**Notes:** Richer metadata can wait for later if needed.

| Option | Description | Selected |
|--------|-------------|----------|
| A card object with `keyword`, parsed `value` when present, and `comment` when present | Make parsed fields the default contract | ✓ |
| A card object with `keyword` and raw card text only | Minimize parsing in Phase 2 | |
| A card object with both parsed fields and raw card text | Add a richer but heavier default schema | |
| You decide | Leave per-card shape open | |

**User's choice:** A card object with `keyword`, parsed `value` when present, and `comment` when present
**Notes:** Raw card text should not be part of the default Phase 2 contract.

---

## the agent's Discretion

- Exact internal model types and helper boundaries used to build the ordered `cards` array
- Exact emitted HDU type strings and per-card omissions for fields that are not present

## Deferred Ideas

- Typed-value policy details
- Exact representation for repeated `COMMENT` and `HISTORY` handling
- Raw-card preservation beyond the default schema
