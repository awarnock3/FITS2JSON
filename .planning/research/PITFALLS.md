# Domain Pitfalls

**Domain:** FITS header to JSON conversion with CFITSIO
**Researched:** 2026-04-12
**Overall confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Flattening the header into a simple one-key/one-value JSON object
**What goes wrong:** The converter assumes every FITS keyword is unique and scalar, so repeated records (`COMMENT`, `HISTORY`, blank/commentary cards, some repeated user keywords) get overwritten or discarded.
**Why it happens:** JSON objects encourage unique keys; FITS headers are ordered card lists, not plain maps.
**Consequences:** Metadata loss, nondeterministic output, and broken parity with the source header. This directly conflicts with the project requirement to preserve repeated/non-key/value records as arrays.
**Warning signs:**
- Data model is `map<string, value>` with no array support
- Only the last `COMMENT`/`HISTORY` survives
- No way to preserve record order or duplicate keys
**Prevention:** Define the JSON schema before coding. Use an HDU object with separate buckets for:
- unique keyword entries
- repeated commentary arrays (`COMMENT`, `HISTORY`)
- optionally a raw `cards` array or positional metadata for lossless/debug output
Do not let the serializer invent structure on the fly.
**Phase should address it:** **Phase 1 — Output contract and schema**

### Pitfall 2: Parsing raw 80-character cards manually instead of using CFITSIO keyword readers
**What goes wrong:** Projects split cards on `=` or `/`, trim by hand, and misparse quoted strings, comments, undefined values, or non-standard-but-supported cards.
**Why it happens:** `fits_read_record` is easy to demo, so teams keep the header-listing loop and bolt on ad hoc string parsing.
**Consequences:** Incorrect values, broken escaping, edge-case bugs, and duplicated parser logic that CFITSIO already provides.
**Warning signs:**
- New helper code manually slices the `card` buffer
- Logic depends on fixed character offsets beyond basic display use
- No use of `fits_read_keyn`, `fits_read_keyword`, or related CFITSIO parsing helpers
**Prevention:** Use `fits_get_hdrspace` + `fits_read_keyn`/`fits_read_keyword` as the extraction path, with `fits_read_record` kept only for optional raw-card preservation. Let CFITSIO parse keyword name/value/comment fields.
**Phase should address it:** **Phase 2 — Header extraction/modeling**

### Pitfall 3: Ignoring FITS long-string (`CONTINUE`) and extended-keyword (`HIERARCH`) conventions
**What goes wrong:** Long string values are truncated or emitted as multiple fake keywords, and extended keyword names are rejected, mangled, or normalized incorrectly.
**Why it happens:** Developers design around only standard 8-character keywords and single-card string values.
**Consequences:** Silent data corruption on real-world headers, especially astronomy metadata from older or instrument-specific pipelines.
**Warning signs:**
- Code assumes keyword names fit traditional 8-char FITS limits
- String extraction uses only raw cards and never tests multi-card string values
- No fixtures for `HIERARCH` or `CONTINUE`
**Prevention:** Treat these as first-class requirements. Verify behavior with CFITSIO support for long strings and HIERARCH keywords, and add fixtures that assert exact JSON output for both cases before release.
**Phase should address it:** **Phase 2 — Header extraction/modeling**, then lock with tests in **Phase 3 — Regression fixtures**

### Pitfall 4: Mixing JSON output with human-readable stdout text
**What goes wrong:** Usage text, “Header listing for HDU #…”, `END`, or other diagnostics leak into stdout alongside JSON.
**Why it happens:** Teams retrofit JSON into an existing printing CLI without separating data output from operator messaging.
**Consequences:** Invalid JSON in pipelines, flaky shell-script behavior, and impossible multi-HDU aggregation.
**Warning signs:**
- `printf` is still used for status banners on stdout
- Usage errors return success or print to stdout
- JSON output is assembled incrementally around existing display text
**Prevention:** Make stdout data-only and stderr diagnostics-only. Remove legacy header-listing banners from JSON mode. Return non-zero on usage and parsing failures. Build tests that pipe stdout to a JSON parser and assert stderr is empty on success.
**Phase should address it:** **Phase 1 — Output contract and CLI semantics**

### Pitfall 5: Mishandling CFITSIO status flow and partial-failure behavior
**What goes wrong:** A non-zero `status` leaks across calls, iteration stops early, or the tool emits partial JSON before reporting an error.
**Why it happens:** CFITSIO uses inherited status semantics: once `status` is positive, later calls no-op until handled/reset correctly.
**Consequences:** Truncated HDU output, malformed aggregate documents, and hard-to-debug failures on one bad keyword or HDU transition.
**Warning signs:**
- JSON is streamed before the whole document is known to be valid
- Error handling is only checked at process end
- HDU loop logic depends on normal CFITSIO errors like `END_OF_FILE`
**Prevention:** Keep one explicit error path. Build the JSON model in memory for one HDU/all HDUs first, then serialize only after successful extraction. Treat `END_OF_FILE` as traversal completion only where intended, and add tests for bad files, missing extensions, and mid-iteration errors.
**Phase should address it:** **Phase 2 — Extraction/control-flow hardening**

## Moderate Pitfalls

### Pitfall 6: Over-simplifying FITS value typing and null handling
**What goes wrong:** Everything becomes a JSON string, or everything numeric-looking becomes a JSON number, while undefined values and precision-sensitive integers are mishandled.
**Why it happens:** FITS keyword values span logical, integer, floating, string, complex formatting, and undefined/blank cases; JSON has a smaller native type system.
**Consequences:** Loss of type fidelity, consumer confusion, and inconsistent downstream behavior across languages.
**Warning signs:**
- No schema rule for undefined keyword values
- Numeric conversion is based on string inspection alone
- There is no test coverage for booleans, quoted strings, blank values, or large integers
**Prevention:** Define conversion rules explicitly:
- FITS logical → JSON boolean
- FITS undefined value → JSON `null` plus raw/comment metadata if needed
- numeric values parsed through CFITSIO, not hand-rolled heuristics
- preserve raw string form where precision or formatting matters
Document the contract instead of letting implementation details decide it.
**Phase should address it:** **Phase 1 — Schema rules**, implemented in **Phase 2**

### Pitfall 7: Skipping regression fixtures for real headers
**What goes wrong:** The converter works on a happy-path sample but breaks on archival headers, commentary-heavy files, or multi-HDU traversal.
**Why it happens:** Brownfield CLI work often ships after a manual spot-check instead of fixture-based verification.
**Consequences:** Rewrites after seemingly minor refactors, especially because the current codebase has no automated tests.
**Warning signs:**
- No golden-output tests under version control
- Only one sample FITS file is used during development
- Edge cases are described in code comments but not asserted in tests
**Prevention:** Add golden JSON fixtures for:
- single-HDU and multi-HDU files
- repeated `COMMENT`/`HISTORY`
- extension-selected output
- malformed or missing-file failures
- long-string / HIERARCH cases
Use the existing `testdata/` corpus plus at least a few targeted synthetic fixtures.
**Phase should address it:** **Phase 3 — Regression fixtures and compatibility**

## Minor Pitfalls

### Pitfall 8: Dropping keyword comments and units as “non-essential”
**What goes wrong:** The JSON keeps only values and discards FITS comments, even though comments often carry units or human context needed to interpret values.
**Why it happens:** Comments look optional from a pure key/value perspective.
**Consequences:** Reduced usefulness of exported metadata and pressure to redesign the schema later.
**Warning signs:**
- JSON entry shape has no place for `comment`
- Unit-like text appears only in discarded comment fields
**Prevention:** Store comment text alongside values for normal keyword entries, even if consumers treat it as optional.
**Phase should address it:** **Phase 1 — Schema design**

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Output schema | Flattening duplicates/commentary into a plain object | Design HDU-level schema with arrays for repeated/commentary records before implementation |
| CLI semantics | stdout polluted with banners/usage text | Make stdout JSON-only and stderr diagnostic-only; fix exit codes |
| Header extraction | Manual card parsing | Use CFITSIO keyword readers instead of slicing 80-char cards |
| FITS compatibility | Missing `CONTINUE` / `HIERARCH` handling | Add explicit fixtures and verify behavior with CFITSIO-supported APIs |
| Error handling | Partial JSON on CFITSIO failure | Build model first, serialize after successful extraction |
| Testing | Happy-path-only validation | Add golden tests covering multi-HDU, repeated commentary, extension selection, and failures |

## Sources

- CFITSIO User’s Reference Guide — Error status and inherited-status behavior: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node28.html **(HIGH)**
- CFITSIO User’s Reference Guide — Keyword reading routines, `fits_get_hdrspace`, `fits_read_keyword`, `fits_read_keyn`, undefined values: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node38.html **(HIGH)**
- CFITSIO User’s Reference Guide — Long string keyword values / `CONTINUE`: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node118.html **(HIGH)**
- CFITSIO User’s Reference Guide — HIERARCH convention support: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node121.html **(HIGH)**
- Local CFITSIO headers (`/usr/include/fitsio.h`, `/usr/include/longnam.h`) for keyword-class constants and available APIs; installed version observed via `pkg-config`: 4.2.0 **(HIGH)**
- Project context: `/home/warnock/dev/FITS2JSON/.planning/PROJECT.md`, `/home/warnock/dev/FITS2JSON/.planning/codebase/CONCERNS.md`, `/home/warnock/dev/FITS2JSON/.planning/codebase/CONVENTIONS.md`, `/home/warnock/dev/FITS2JSON/src/listhead.c` **(HIGH)**
