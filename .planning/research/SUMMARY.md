# Research Summary

**Project:** FITS2JSON
**Summarized:** 2026-04-12

## Recommended Stack

- Keep the implementation in **C** on top of **CFITSIO**
- Add a small JSON library, with **Jansson** the recommended choice
- Replace hard-coded library paths with **pkg-config**
- Avoid rewriting the tool in another language or hand-rolling JSON output

## Table Stakes

- Valid JSON to stdout with deterministic scripting behavior
- All HDUs in one document by default when no extension is specified
- Specific-HDU selection by number or name
- Structured per-HDU output instead of raw card dumps
- Preservation of repeated records like `COMMENT` and `HISTORY`
- Correct handling of FITS edge cases such as `CONTINUE` and `HIERARCH`

## Architecture Direction

Use a small internal pipeline:

```text
CLI/options -> FITS traversal -> header normalization -> JSON emission
```

The recommended build order is:
1. Extract seams from `main`
2. Introduce a normalized header model
3. Add JSON emission
4. Add regression fixtures and Makefile cleanup

## Watch Out For

- Flattening FITS headers into a plain JSON object and losing repeated/order-sensitive records
- Parsing raw 80-character cards manually instead of using CFITSIO keyword APIs
- Polluting stdout with non-JSON text
- Emitting partial JSON when CFITSIO status handling fails mid-run
- Ignoring long-string and extended-keyword cases

## MVP Recommendation

Prioritize:
1. Valid JSON output contract
2. Multi-HDU and selected-HDU traversal parity with the current CLI
3. Structured keyword extraction with repeated commentary arrays
4. Deterministic error handling for shell scripts

Nice-to-have but deferable:
- Batch multi-file mode
- JSON Lines output
- Alternate schema modes
- Cross-file comparison features

## Files

- `STACK.md`
- `FEATURES.md`
- `ARCHITECTURE.md`
- `PITFALLS.md`
