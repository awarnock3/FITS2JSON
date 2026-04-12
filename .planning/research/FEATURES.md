# Feature Landscape

**Domain:** FITS header to JSON CLI conversion
**Researched:** 2026-04-12

## Table Stakes

Features users expect. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Emit valid JSON to stdout | Core promise of the tool is machine-readable header output for scripts/pipelines | Med | Must keep stdout clean JSON and send errors to stderr; non-zero exit codes on failure are part of this |
| Default to all HDUs when no extension is specified | Existing FITS header tools list all HDUs by default when no specific extension is given | Low | Matches current `listhead` behavior and tools like `fitsheader`/`ftlist` |
| Select a specific HDU by number or name | Standard FITS CLI behavior; users often want primary HDU, a numbered extension, or named extension only | Low | Should support numeric index and named extension; EXTNAME+EXTVER support is useful |
| Structured keyword output per HDU | JSON users expect parsed fields, not raw 80-char card dumps | Med | Recommended shape: per-HDU object containing ordered cards + normalized keyword access |
| Preserve repeated commentary records (`COMMENT`, `HISTORY`, blank cards) | FITS headers commonly repeat these; dropping or flattening them is lossy | Med | Should be arrays, not last-write-wins scalars |
| Preserve header order | FITS headers are card-ordered, and some workflows care about original order when auditing/debugging | Med | Order should be stable even if normalized keyword lookup is also provided |
| Parse values into JSON-native types where safe | Users expect booleans/numbers/nulls as values, not only strings | Med | Keep raw card text available or derivable for fidelity/debugging |
| Keyword filtering (`--keyword` / include patterns) | Common in existing FITS header tools for scripting against a subset of metadata | Med | Wildcard support like `NAXIS*` is standard enough to treat as expected |
| Deterministic schema and failure behavior | CLI tools used in automation must be stable across runs | Low | Stable field names, stable ordering, documented exit codes |
| Correct handling of FITS header edge cases | Real-world FITS headers include long strings (`CONTINUE`), hierarchical keywords (`HIERARCH`), and duplicated cards | High | This is where many “simple” converters become unreliable |

## Differentiators

Features that set product apart. Not expected, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Dual representation: normalized JSON + raw card text | Lets users script against parsed values without losing original FITS fidelity | Med | Strong differentiator for debugging and round-trip trust |
| Batch mode over many FITS files | Useful for archives and shell pipelines processing directories or globbed inputs | Med | Single-file mode is enough for MVP; multi-file aggregation is a nice upgrade |
| JSON Lines output for batch workflows | Better streaming behavior than one giant JSON array/object | Med | Valuable once batch mode exists |
| Alternate output schemas (`cards`, `keywords`, `flat`) | Supports both humans and automation without making one schema do everything badly | Med | Good if explicitly versioned |
| Strict vs lenient parsing mode | Helps users choose between “best effort” extraction and standards-enforced failure | High | Especially useful around malformed headers or unexpected cards |
| Compressed-header awareness | Some tools distinguish logical image header vs underlying compressed BINTABLE header | High | Valuable for advanced FITS users, but not MVP table stakes |
| Cross-file comparison / fitsort-style extraction | Useful for observatory/archive workflows comparing selected keywords across files | Med | More of an analysis feature than a converter core feature |
| Schema version field in output | Makes downstream integrations safer over time | Low | Small cost, high long-term payoff |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Serializing FITS data payloads (images/tables) | Major scope expansion; project goal is header metadata only | Stay header-only |
| Re-implementing FITS parsing instead of using CFITSIO | High risk and unnecessary given existing proven dependency | Keep CFITSIO as parser of record |
| Lossy flattening of headers into one simple key/value object | Breaks repeated cards, ordering, blank/commentary cards, and duplicate-key semantics | Use ordered cards plus grouped commentary arrays |
| Writing back or repairing FITS files | Different tool category; increases risk and complexity | Keep tool read-only |
| Overly clever query language | Scope creep for a small CLI | Support simple include/exclude/wildcard filtering first |
| Mixing logs/progress text into stdout | Breaks JSON consumers immediately | Reserve stdout for JSON only; stderr for diagnostics |

## Feature Dependencies

```text
Open FITS file + iterate HDUs
  -> HDU selection
  -> default “all HDUs” document

Structured card extraction
  -> typed JSON values
  -> commentary arrays
  -> preserved card order
  -> raw+normalized dual representation

Stable schema
  -> deterministic scripting behavior
  -> batch mode
  -> JSON Lines / alternate schema modes

Keyword filtering
  -> requires structured keyword/card model
  -> becomes much easier once HDU selection is in place

Strict/lenient parsing
  -> depends on explicit error model
  -> depends on edge-case handling (CONTINUE, HIERARCH, duplicates)

Compressed-header awareness
  -> depends on HDU model and explicit header-source semantics
```

## MVP Recommendation

Prioritize:
1. **Valid JSON emission with deterministic CLI behavior**
2. **All-HDU default plus explicit HDU selection**
3. **Structured per-HDU output that preserves order and repeated commentary cards**
4. **Keyword filtering with simple wildcard support**

One differentiator worth pulling into MVP:
5. **Dual representation of parsed values plus raw card text** — it materially increases trust without changing scope.

Defer:
- **Batch multi-file mode**: useful, but not necessary for the first scriptable single-file converter
- **Compressed-header awareness**: important for advanced users, but niche relative to core conversion
- **Cross-file comparison/fitsort features**: better as a later workflow layer than as core conversion logic

## Sources

- **HIGH** — Astropy executable scripts docs (`fitsheader`, `fitsinfo`): https://docs.astropy.org/en/stable/io/fits/usage/scripts.html
- **HIGH** — Astropy FITS header behavior docs (duplicates, `COMMENT`/`HISTORY`, `CONTINUE`, `HIERARCH`): https://docs.astropy.org/en/stable/io/fits/usage/headers.html
- **HIGH** — HEASoft `ftlist` help (`all HDUs` default, extension selection, include/exclude keyword filtering): https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/help/ftlist.html
- **HIGH** — Project context: `/home/warnock/dev/FITS2JSON/.planning/PROJECT.md`
- **HIGH** — Current implementation baseline: `/home/warnock/dev/FITS2JSON/src/listhead.c`

## Confidence Notes

- **Table stakes: HIGH confidence** — strongly supported by Astropy/HEASoft behavior and current project requirements
- **Differentiators: MEDIUM confidence** — ecosystem-aligned and practical, but less uniformly standardized across tools
