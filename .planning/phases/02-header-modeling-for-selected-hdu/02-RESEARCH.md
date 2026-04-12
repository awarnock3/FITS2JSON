# Phase 2: Header Modeling for Selected HDU - Research

**Researched:** 2026-04-12  
**Domain:** CFITSIO-based FITS header normalization for selected-HDU JSON emission  
**Confidence:** HIGH for CFITSIO API choice and header modeling; MEDIUM for Phase-2 JSON typing policy. [VERIFIED: local codebase][VERIFIED: CFITSIO runtime experiment][CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/]

<user_constraints>
## User Constraints (from CONTEXT.md)

Copied verbatim from `.planning/phases/02-header-modeling-for-selected-hdu/02-CONTEXT.md`. [VERIFIED: local codebase]

### Locked Decisions
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

### Deferred Ideas (OUT OF SCOPE)
- Alternate schema modes such as grouped keyword objects
- Including raw 80-character card text in default output
- Whole-file top-level JSON document design
- Richer HDU metadata beyond `index` and `type`
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HEAD-01 | User can convert FITS header metadata to valid JSON on stdout | Build full in-memory HDU model first, then emit JSON in one pass. [VERIFIED: local codebase][ASSUMED] |
| HEAD-04 | User can receive structured keyword output for each HDU instead of raw 80-character header cards | Use `fits_read_keyn` as primary traversal API, not manual card parsing. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment] |
| HEAD-05 | User can receive keyword comments alongside parsed values where FITS provides them | `fits_read_keyn` returns separated `keyname`, `value`, and `comment`; `fits_read_key_longstr` returns full string/comment for string-valued keys. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment] |
| FITS-01 | User can preserve repeated `COMMENT` records as arrays within each HDU | Preserve each `COMMENT` as its own `cards[]` entry in order; filtered `COMMENT` subsequence is the required array. [VERIFIED: CFITSIO runtime experiment][VERIFIED: local codebase] |
| FITS-02 | User can preserve repeated `HISTORY` records as arrays within each HDU | Preserve each `HISTORY` as its own `cards[]` entry in order; filtered `HISTORY` subsequence is the required array. [VERIFIED: CFITSIO runtime experiment][VERIFIED: local codebase] |
| FITS-03 | User can receive deterministic output that preserves the original header record order within each HDU | Iterate header by ordinal index `1..nkeys`; skip only physical `CONTINUE` helper cards after folding them into the owning string keyword. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment] |
| FITS-04 | User can convert headers without corrupting supported FITS edge cases such as long-string and extended-keyword records | Use `fits_read_key_longstr` for string-valued keywords and rely on CFITSIO HIERARCH handling. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment] |
</phase_requirements>

## Summary

Phase 2 should keep the existing Phase-1 selector/open flow in `src/fits2json.c`, read exactly one current HDU, normalize it into a small in-memory model, close the FITS handle, and only then write the HDU JSON object to stdout. [VERIFIED: local codebase][CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/]

The primary extraction pattern should be: `fits_get_hdu_num` + `fits_get_hdu_type` + `fits_get_hdrspace`, then iterate `keynum=1..nkeys` with `fits_read_keyn`, classify the physical card with `fits_read_record` + `fits_get_keyclass`, skip `CONTINUE` cards, and upgrade string-valued keywords through `fits_read_key_longstr` so long-string values are emitted once, fully assembled, and unquoted. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment]

**Primary recommendation:** Use `fits_read_keyn` as the canonical ordered traversal API, `fits_get_keyclass` to distinguish commentary/continuation records, and `fits_read_key_longstr` for every string-valued non-commentary keyword; emit COMMENT/HISTORY as ordinary ordered card objects with no `value` field. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment]

## Project Constraints (from copilot-instructions.md)

- Keep the implementation a single C CLI program built from `src/Makefile`; do not introduce a wrapper script or second runtime. [VERIFIED: local codebase]
- Keep the runtime entry point in `src/fits2json.c` and stay close to the current procedural layout. [VERIFIED: local codebase]
- Preserve CFITSIO status-driven flow and final error reporting via `fits_report_error(stderr, status)` where CFITSIO produced the failure. [VERIFIED: local codebase]
- Keep diagnostics on `stderr`; successful data output belongs on `stdout`. [VERIFIED: local codebase]
- Match existing manual C style and use local helper seams only as needed; do not broaden scope into a multi-file refactor in this phase. [VERIFIED: local codebase]
- Use `testdata/*.HDR` fixtures for manual verification. [VERIFIED: local codebase]

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| CFITSIO | 4.2.0 | FITS open/select/header APIs | Existing project dependency and the official FITS parsing layer already used by `src/fits2json.c`. [VERIFIED: pkg-config cfitsio][VERIFIED: local codebase] |
| C stdlib / stdio | system | in-memory model, allocation, JSON emission | Fits the locked single-C-program constraint and current code structure. [VERIFIED: local codebase] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `fits_read_record` + manual parsing | `fits_read_keyn` + targeted CFITSIO helpers | Prefer `fits_read_keyn`; it already returns separated keyword/value/comment and avoids homegrown FITS parsing. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment] |
| Flattened JSON object keyed by keyword | Ordered `cards` array | Prefer `cards`; repeated COMMENT/HISTORY and header order are preserved naturally. [VERIFIED: local codebase] |

## Architecture Patterns

### Recommended Project Structure

```text
src/fits2json.c
  main
  -> parse existing CLI / selector path
  -> read_selected_hdu_model(...)
  -> emit_hdu_json(...)
```

Keep this as one translation unit with a few `static` helpers, not a multi-file redesign. [VERIFIED: local codebase]

### Pattern 1: Ordered physical traversal, logical card emission

**What:** Iterate physical header positions in order, but emit logical cards. `CONTINUE` cards are physical helpers and should not become standalone output cards once their text has been folded into the owning string keyword. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment]

**When to use:** Every selected-HDU conversion path. [VERIFIED: local codebase]

**Implementation pattern:**
```c
/* Source: CFITSIO User's Reference Guide + runtime verification */
fits_get_hdu_num(fptr, &hdu_index);
fits_get_hdu_type(fptr, &hdu_type, &status);
fits_get_hdrspace(fptr, &nkeys, NULL, &status);

for (int keynum = 1; keynum <= nkeys && !status; keynum++) {
    char card[FLEN_CARD], keyname[FLEN_KEYWORD], value[FLEN_VALUE], comment[FLEN_COMMENT];
    fits_read_record(fptr, keynum, card, &status);
    int keyclass = fits_get_keyclass(card);

    fits_read_keyn(fptr, keynum, keyname, value, comment, &status);

    if (keyclass == TYP_CONT_KEY) continue;          /* folded into prior string */
    if (keyclass == TYP_COMM_KEY) { /* emit keyword + comment only */ }
    else { /* classify value; for strings call fits_read_key_longstr */ }
}
```

### Pattern 2: String-value upgrade path

**What:** Use `fits_read_keyn` first for order and identity, then if the returned value is string-typed, re-read that keyword with `fits_read_key_longstr` and free the allocated memory with `fits_free_memory`. This yields the full dequoted logical string for both ordinary and long-string keywords. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment]

**When to use:** Any non-commentary keyword where `fits_get_keytype(value)` reports `'C'`. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment]

### Anti-Patterns to Avoid

- **Manual 80-character card parsing:** CFITSIO already exposes separated keyword/value/comment APIs. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/]
- **Emitting standalone `CONTINUE` cards:** runtime verification shows `fits_read_keyn` exposes physical `CONTINUE` records separately, so emitting them directly would duplicate long-string semantics. [VERIFIED: CFITSIO runtime experiment]
- **Flattening headers into one JSON object:** repeated COMMENT/HISTORY become lossy. [VERIFIED: local codebase]
- **Streaming stdout before the HDU model is complete:** that risks partial JSON on later failure. [ASSUMED]

## Recommended Internal Model / Helper Seams

Use a minimal heap-backed vector and stay single-file. [VERIFIED: local codebase]

```c
enum value_kind {
    VALUE_NONE = 0,
    VALUE_BOOL,
    VALUE_STRING
};

struct header_card {
    char *keyword;
    int has_value;
    enum value_kind value_kind;
    int bool_value;      /* used when value_kind == VALUE_BOOL */
    char *string_value;  /* used when value_kind == VALUE_STRING */
    int has_comment;
    char *comment;
};

struct hdu_model {
    int index;           /* 1-based CFITSIO HDU number */
    int hdu_type;        /* IMAGE_HDU / ASCII_TBL / BINARY_TBL */
    struct header_card *cards;
    size_t count;
    size_t cap;
};
```

Recommended static helpers: [ASSUMED]

1. `static int read_selected_hdu_model(fitsfile *fptr, struct hdu_model *out);`
2. `static int append_card(struct hdu_model *hdu, struct header_card *card);`
3. `static int classify_and_fill_value(fitsfile *fptr, const char *keyname, const char *raw_value, struct header_card *card);`
4. `static const char *json_hdu_type_name(int hdutype);`
5. `static int emit_hdu_json(FILE *out, const struct hdu_model *hdu);`
6. `static void free_hdu_model(struct hdu_model *hdu);`

## Concrete CFITSIO APIs to Prefer

| API | Use | Reason |
|-----|-----|--------|
| `fits_open_file` | keep current selector/open behavior | Already proven in current entry point. [VERIFIED: local codebase] |
| `fits_get_hdu_num` | emit `index` | Returns current HDU number where primary array is 1. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/] |
| `fits_get_hdu_type` | emit `type` | Official API for `IMAGE_HDU`, `ASCII_TBL`, `BINARY_TBL`. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/] |
| `fits_get_hdrspace` | get physical header record count | Official nth-key traversal entry point. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/] |
| `fits_read_keyn` | primary ordered read path | Returns nth record as separated key/value/comment strings. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment] |
| `fits_read_record` | fetch raw record only for classification | Needed so `fits_get_keyclass` can identify `CONTINUE` and commentary records without custom parsing. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/] |
| `fits_get_keyclass` | classify physical card | Officially distinguishes `TYP_COMM_KEY` and `TYP_CONT_KEY`. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment] |
| `fits_get_keytype` | decide Phase-2 value coercion | Classifies raw value token as character/logical/integer/float/complex. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment] |
| `fits_read_key_longstr` + `fits_free_memory` | full string extraction | Correctly reads ordinary and long-string keywords, including CONTINUE convention, and returns dequoted content. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment] |
| `fits_close_file` | close before emitting stdout | Lets conversion fail before any JSON is written. [ASSUMED] |
| `fits_report_error` | stderr diagnostics on CFITSIO failure | Current established pattern. [VERIFIED: local codebase] |

## Typed-Value Strategy

**Recommended Phase-2 policy:** emit only two JSON value kinds in `card.value`: JSON booleans for FITS logicals and JSON strings for everything else that has a value. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][CITED: https://www.rfc-editor.org/rfc/rfc8259.txt][VERIFIED: CFITSIO runtime experiment]

Why this is safest: [CITED: https://www.rfc-editor.org/rfc/rfc8259.txt][VERIFIED: CFITSIO runtime experiment]

- CFITSIO classifies FITS literals as character/logical/integer/floating/complex. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/]
- JSON has no complex scalar type, and its numeric grammar only allows `e`/`E` exponents, not FITS-style `D` exponents. [CITED: https://www.rfc-editor.org/rfc/rfc8259.txt][VERIFIED: CFITSIO runtime experiment]
- Runtime verification shows `fits_get_keytype("1.23D+03")` reports a floating value, so blindly copying numeric FITS lexemes into JSON numbers can produce invalid JSON or lossy coercions. [VERIFIED: CFITSIO runtime experiment][CITED: https://www.rfc-editor.org/rfc/rfc8259.txt]

**Planner rule:** [ASSUMED]

- `dtype == 'L'` → emit `true` / `false`
- `dtype == 'C'` → emit JSON string from `fits_read_key_longstr`
- `dtype == 'I' || dtype == 'F' || dtype == 'X'` → emit JSON string containing the original FITS lexical value from CFITSIO
- no value / commentary card → omit `value`

This keeps Phase 2 valid and semantically safe; numeric coercion can be added later only with explicit schema/versioning. [ASSUMED]

## COMMENT and HISTORY Representation

Represent COMMENT and HISTORY as ordinary card objects inside the canonical ordered `cards` array, with `keyword` set to `"COMMENT"` or `"HISTORY"`, no `value` field, and `comment` carrying the body text exactly as CFITSIO returns it. Do not add sibling top-level `comment`/`history` arrays in Phase 2. [VERIFIED: CFITSIO runtime experiment][VERIFIED: local codebase]

Why: [VERIFIED: CFITSIO runtime experiment][VERIFIED: local codebase]

- `fits_read_keyn` returns empty `value` and the remaining body text in `comment` for COMMENT/HISTORY records. [VERIFIED: CFITSIO runtime experiment]
- The locked public contract says the canonical representation is the ordered `cards` array. [VERIFIED: local codebase]
- Repeated COMMENT/HISTORY are still “arrays within the HDU output” because they are preserved as repeated ordered elements in `cards`; tests can assert `cards` filtered by keyword equals the expected COMMENT/HISTORY array. [VERIFIED: local codebase][ASSUMED]

Example:
```json
{
  "keyword": "HISTORY",
  "comment": " CONVERTED TO FITS BY PROGRAM IHWP2F TUE SEP 26,1989"
}
```
[VERIFIED: CFITSIO runtime experiment]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| FITS card splitting | custom parsing of 80-char records | `fits_read_keyn` | Officially returns separated keyword/value/comment. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/] |
| Long-string assembly | manual `CONTINUE` concatenation | `fits_read_key_longstr` + `fits_free_memory` | Runtime verification shows physical `CONTINUE` cards appear separately in nth-record traversal. [VERIFIED: CFITSIO runtime experiment] |
| HIERARCH decoding | stripping `HIERARCH` yourself | CFITSIO keyword APIs | CFITSIO transparently reads HIERARCH names and accepts lookups with or without the `HIERARCH` prefix. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment] |
| HDU type inference | ad-hoc keyword inspection | `fits_get_hdu_type` | Direct API already exists. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/] |

## Common Pitfalls

### Pitfall 1: Duplicating long strings
`fits_read_keyn` walks physical records, not logical string values; runtime verification shows a long string appears as one truncated string card followed by one or more `CONTINUE` records. If the code emits both, the JSON is wrong. [VERIFIED: CFITSIO runtime experiment]

**Avoid:** skip `TYP_CONT_KEY` output and re-read string keywords with `fits_read_key_longstr`. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/]

### Pitfall 2: Misinterpreting COMMENT/HISTORY
COMMENT/HISTORY cards do not have a FITS value field; CFITSIO returns the body in `comment`, not `value`. Treating these like normal `KEY = VALUE / COMMENT` cards will lose data. [VERIFIED: CFITSIO runtime experiment]

### Pitfall 3: Emitting invalid JSON numbers
FITS floating literals may use `D` exponents, and FITS also has complex values; these are not safe direct JSON numbers. [VERIFIED: CFITSIO runtime experiment][CITED: https://www.rfc-editor.org/rfc/rfc8259.txt]

### Pitfall 4: Carrying over the old synthetic `END`
Current `src/fits2json.c` prints `END` manually after the loop; that is presentation logic from the header-listing tool, not a card that needs to be synthesized into Phase-2 JSON. [VERIFIED: local codebase]

### Pitfall 5: Partial stdout on failure
If JSON starts streaming before all cards are modeled, later CFITSIO or allocation failures will leave malformed stdout. [ASSUMED]

## Failure-Handling Constraints for the Planner

Enforce these as plan requirements: [ASSUMED][VERIFIED: local codebase]

1. **No stdout before success is known.** Build the entire selected-HDU model in memory first. [ASSUMED]
2. **Close the FITS handle before emitting JSON.** That keeps open/read/close failures on the no-stdout side of the boundary. [ASSUMED]
3. **All diagnostics go to stderr.** Keep `fits_report_error(stderr, status)` for CFITSIO errors and a tiny custom stderr path for allocation/internal errors. [VERIFIED: local codebase]
4. **Return non-zero on conversion failure.** This aligns with later CLI reliability phases. [VERIFIED: local codebase][ASSUMED]
5. **Never mix usage/help text into successful stdout.** If usage text remains, send it to stderr for forward compatibility. [ASSUMED]
6. **Free all long-string buffers with `fits_free_memory` and all model allocations before exit.** `fits_read_key_longstr` allocates memory. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/]

## Code Examples

### Selected-HDU card normalization
```c
/* Source: CFITSIO docs + runtime verification */
static int normalize_card(fitsfile *fptr, int keynum, struct header_card *out, int *status)
{
    char card[FLEN_CARD], keyname[FLEN_KEYWORD], raw_value[FLEN_VALUE], comment[FLEN_COMMENT];
    char dtype = 0;

    fits_read_record(fptr, keynum, card, status);
    if (*status) return *status;

    int keyclass = fits_get_keyclass(card);

    fits_read_keyn(fptr, keynum, keyname, raw_value, comment, status);
    if (*status) return *status;

    if (keyclass == TYP_CONT_KEY) return 1; /* caller treats as skipped */

    out->keyword = strdup(keyname);
    out->has_value = 0;
    out->has_comment = 0;

    if (keyclass == TYP_COMM_KEY) {
        if (comment[0] != '\0') {
            out->comment = strdup(comment);
            out->has_comment = 1;
        }
        return 0;
    }

    fits_get_keytype(raw_value, &dtype, status);
    if (*status == VALUE_UNDEFINED) { *status = 0; return 0; }

    if (dtype == 'L') {
        out->has_value = 1;
        out->value_kind = VALUE_BOOL;
        out->bool_value = (raw_value[0] == 'T');
    } else if (dtype == 'C') {
        char *longstr = NULL;
        char full_comment[FLEN_COMMENT] = {0};

        fits_read_key_longstr(fptr, keyname, &longstr, full_comment, status);
        if (*status) return *status;

        out->has_value = 1;
        out->value_kind = VALUE_STRING;
        out->string_value = strdup(longstr ? longstr : "");
        if (full_comment[0] != '\0') {
            out->comment = strdup(full_comment);
            out->has_comment = 1;
        }

        fits_free_memory(longstr, status);
    } else {
        out->has_value = 1;
        out->value_kind = VALUE_STRING;
        out->string_value = strdup(raw_value);
        if (comment[0] != '\0') {
            out->comment = strdup(comment);
            out->has_comment = 1;
        }
    }

    return 0;
}
```
[ASSUMED][CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment]

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| `fits_read_record` + print raw cards + synthetic `END` | `fits_read_keyn`-driven logical card model with string upgrade via `fits_read_key_longstr` | Preserves FITS semantics while giving a machine-readable schema. [VERIFIED: local codebase][VERIFIED: CFITSIO runtime experiment] |
| Physical card output | Ordered logical `cards` array | Repeated commentary stays intact and long strings can be emitted once, correctly. [VERIFIED: CFITSIO runtime experiment] |

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| gcc | build | ✓ | 13.3.0 | — |
| make | build | ✓ | 4.3 | — |
| CFITSIO dev pkg | runtime/build | ✓ | 4.2.0 | — |
| python3 | validation fallback | ✓ | 3.12.3 | manual inspection |

[VERIFIED: local environment]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | none detected. [VERIFIED: local codebase] |
| Config file | none — see Wave 0. [VERIFIED: local codebase] |
| Quick run command | `make -C src && ./src/fits2json 'testdata/IRPH0189.HDR[0]' | python3 -c 'import json,sys; json.load(sys.stdin)'` [ASSUMED] |
| Full suite command | same plus a second fixture with repeated COMMENT/HISTORY, e.g. `LSPN2790.HDR`. [ASSUMED] |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HEAD-01 | stdout is valid JSON for selected HDU | smoke | `make -C src && ./src/fits2json 'testdata/IRPH0189.HDR[0]' | python3 -c 'import json,sys; json.load(sys.stdin)'` | ❌ Wave 0 |
| HEAD-04 | structured `cards` objects emitted | smoke/golden | `... | python3 -c 'import json,sys; d=json.load(sys.stdin); assert isinstance(d[\"cards\"], list)'` | ❌ Wave 0 |
| HEAD-05 | comments preserved | smoke/golden | fixture-specific Python assertion on card comment fields | ❌ Wave 0 |
| FITS-01 | repeated COMMENT preserved in order | smoke/golden | use `NNSN2261.HDR` or `LSPN2790.HDR`, assert filtered COMMENT subsequence length/order | ❌ Wave 0 |
| FITS-02 | repeated HISTORY preserved in order | smoke/golden | use `LSPN2790.HDR`, assert filtered HISTORY subsequence length/order | ❌ Wave 0 |
| FITS-03 | card order deterministic | golden | compare keyword sequence from JSON to fixture-derived expectation | ❌ Wave 0 |
| FITS-04 | long-string/HIERARCH path not corrupted | targeted unit/manual | add a synthetic fixture or in-memory harness; current repo fixtures do not verify this edge case. [VERIFIED: local codebase][VERIFIED: CFITSIO runtime experiment] | ❌ Wave 0 |

### Wave 0 Gaps

- [ ] Add at least one smoke script or test harness for JSON-validity checks. [ASSUMED]
- [ ] Add a fixture or harness covering long-string + `CONTINUE`. [VERIFIED: local codebase][VERIFIED: CFITSIO runtime experiment]
- [ ] Add a fixture or harness covering HIERARCH extended keyword names. [VERIFIED: local codebase][VERIFIED: CFITSIO runtime experiment]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | not applicable to local CLI header conversion. [ASSUMED] |
| V3 Session Management | no | not applicable. [ASSUMED] |
| V4 Access Control | no | not applicable. [ASSUMED] |
| V5 Input Validation | yes | validate argc, pass file path directly to CFITSIO, reject malformed conversion state via status checks. [VERIFIED: local codebase][ASSUMED] |
| V6 Cryptography | no | not applicable. [ASSUMED] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed FITS header/card content | Tampering | Use CFITSIO parsing APIs; do not write a custom parser. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/] |
| Large/continued string causing allocation bugs | DoS | Centralize `fits_read_key_longstr` usage and free buffers deterministically. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/] |
| Partial JSON on failure | Integrity | Buffer model first, emit after success only. [ASSUMED] |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Usage/help text should move to stderr in Phase 2 for forward compatibility | Failure-Handling Constraints | Low |
| A2 | Filtered COMMENT/HISTORY subsequences in `cards` satisfy FITS-01/FITS-02 without adding sibling arrays | COMMENT and HISTORY Representation | Medium |
| A3 | Phase 2 should keep numeric FITS literals as JSON strings instead of numbers | Typed-Value Strategy | Medium |
| A4 | Close-before-emit is the right atomicity boundary | Failure-Handling Constraints | Low |

## Sources

### Primary (HIGH confidence)
- CFITSIO User's Reference Guide, header/key routines. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/]
- RFC 8259 JSON grammar. [CITED: https://www.rfc-editor.org/rfc/rfc8259.txt]
- Local project files: `src/fits2json.c`, `src/Makefile`, `.planning/...`, `copilot-instructions.md`. [VERIFIED: local codebase]
- Local CFITSIO package/header/runtime on this machine (`pkg-config cfitsio`, `/usr/include/fitsio.h`, ctypes experiments). [VERIFIED: pkg-config cfitsio][VERIFIED: CFITSIO runtime experiment]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - current dependency and version were verified locally. [VERIFIED: pkg-config cfitsio][VERIFIED: local codebase]
- Architecture: HIGH - directly constrained by current single-file program and Phase 2 context. [VERIFIED: local codebase]
- Pitfalls: HIGH - confirmed by CFITSIO runtime experiments for COMMENT/HISTORY, CONTINUE, long strings, and HIERARCH. [VERIFIED: CFITSIO runtime experiment]

**Valid until:** 30 days for repo constraints, 30 days for CFITSIO API guidance. [ASSUMED]

## RESEARCH COMPLETE

**Phase:** 2 - Header Modeling for Selected HDU  
**Confidence:** HIGH

### Key Findings
- Prefer `fits_read_keyn` for ordered traversal, `fits_get_keyclass` for commentary/continuation classification, and `fits_read_key_longstr` for all string-valued non-commentary keywords. [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/][VERIFIED: CFITSIO runtime experiment]
- COMMENT and HISTORY should remain ordinary ordered `cards[]` entries with `keyword` plus `comment`, and no `value`. [VERIFIED: CFITSIO runtime experiment]
- The safest Phase-2 `value` policy is boolean-or-string only; keep numeric and complex FITS lexemes as JSON strings to avoid invalid JSON and semantic corruption. [CITED: https://www.rfc-editor.org/rfc/rfc8259.txt][VERIFIED: CFITSIO runtime experiment]
- Add only small `static` helper seams inside `src/fits2json.c`; do not refactor into multiple files in this phase. [VERIFIED: local codebase]
- Enforce no-stdout-until-success and close-before-emit so later reliability phases do not have to undo partial-JSON behavior. [ASSUMED]

**Planner-ready outcome:** The planner can now create Phase-2 tasks around one in-memory HDU model, a CFITSIO-driven normalization loop, a conservative JSON emitter, and fixture-based smoke validation.