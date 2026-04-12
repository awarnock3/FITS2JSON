# Phase 3: Whole-File JSON Emission - Research

**Researched:** 2026-04-12  
**Domain:** CFITSIO-driven whole-file HDU traversal and atomic JSON emission for a single C CLI [VERIFIED: /home/warnock/dev/FITS2JSON/.planning/ROADMAP.md; VERIFIED: /home/warnock/dev/FITS2JSON/src/fits2json.c]  
**Confidence:** HIGH [VERIFIED: local code inspection + official CFITSIO docs + local environment audit]

<user_constraints>
## User Constraints (from CONTEXT.md) [VERIFIED: /home/warnock/dev/FITS2JSON/.planning/phases/03-whole-file-json-emission/03-CONTEXT.md]

### Locked Decisions
- **D-01:** When no selector is given, emit a top-level JSON array of HDU objects.
- **D-02:** Each array element should reuse the existing Phase 2 HDU object contract rather than introducing a second per-HDU schema.
- **D-03:** Keep explicit selector mode unchanged: it should continue to emit the existing single HDU object from Phase 2.
- **D-04:** Phase 3 is additive: selectorless mode returns an array, while explicit selector mode remains a single object.
- **D-05:** Do not add file-level metadata to the default Phase 3 output unless planning proves it is strictly required to satisfy the phase goal.
- **D-06:** Preserve stdout purity so selectorless whole-file output remains directly pipeable into JSON-consuming tools.

### the agent's Discretion
- Exact helper boundaries for iterating all HDUs while reusing the Phase 2 selected-HDU model/emitter seams
- Exact internal error-handling flow needed to avoid partial selectorless output on failure
- Exact reuse/extraction strategy for producing either a single object or top-level array without duplicating logic

### Deferred Ideas (OUT OF SCOPE)
- Adding filename or other file-level metadata to the default top-level document
- Unifying selected-HDU and selectorless modes under one schema
- Alternate schema modes beyond the Phase 2 ordered-card contract
</user_constraints>

<phase_requirements>
## Phase Requirements [VERIFIED: /home/warnock/dev/FITS2JSON/.planning/REQUIREMENTS.md; VERIFIED: /home/warnock/dev/FITS2JSON/.planning/ROADMAP.md]

| ID | Description | Research Support |
|----|-------------|------------------|
| HEAD-02 | User can receive one JSON document containing all HDUs when no extension is specified [VERIFIED: REQUIREMENTS.md] | Use `fits_get_num_hdus` + `fits_movabs_hdu` to read each HDU in file order and emit one top-level JSON array only after all HDUs are modeled successfully [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node36.html; VERIFIED: src/fits2json.c] |
| CLI-01 | User can pipe successful command output directly into JSON-consuming shell tools without non-JSON text mixed into stdout [VERIFIED: REQUIREMENTS.md] | Keep all diagnostics on `stderr`, retain the existing close-before-emit pattern, and forbid any selectorless streaming before traversal/modeling succeeds [VERIFIED: src/fits2json.c:455-495; VERIFIED: ROADMAP.md] |
</phase_requirements>

## Project Constraints (from copilot-instructions.md) [VERIFIED: /home/warnock/dev/FITS2JSON/copilot-instructions.md]

- Keep Phase 3 inside one existing C program; do not introduce a wrapper script or second runtime [VERIFIED: copilot-instructions.md].  
- Continue building from `src/Makefile` and the `src/fits2json.c` entry point [VERIFIED: copilot-instructions.md; VERIFIED: src/Makefile].  
- Keep CFITSIO as the FITS parser and traversal layer [VERIFIED: copilot-instructions.md; VERIFIED: src/fits2json.c].  
- Preserve stdout as the JSON channel and stderr for diagnostics only [VERIFIED: copilot-instructions.md; VERIFIED: src/fits2json.c].  
- Match the current procedural single-file style and status-driven CFITSIO error flow [VERIFIED: copilot-instructions.md; VERIFIED: src/fits2json.c].  
- No project skills directories were present under `.github/skills/` or `.agents/skills/` during this research pass [VERIFIED: repository path check].

## Summary

Phase 3 should be implemented as a strict branch on selector presence: explicit-selector invocations stay on the existing Phase 2 single-HDU path, while selectorless invocations open the FITS file at the default primary HDU, count HDUs with `fits_get_num_hdus`, walk them in absolute order with `fits_movabs_hdu`, and reuse the current per-HDU model builder for each element [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node21.html; CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node35.html; CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node36.html; VERIFIED: src/fits2json.c].  

The minimal safe refactor is not a schema redesign; it is helper extraction around the already-correct Phase 2 seams. `read_selected_hdu_model` already reads the current HDU in-place, so whole-file mode mainly needs a document container plus an object-emitter that can be reused inside either a top-level array writer or the existing explicit single-object writer [VERIFIED: src/fits2json.c:323-452].  

**Primary recommendation:** Keep explicit selector mode byte-for-byte contract-compatible, add selectorless mode as an in-memory array build over `fits_get_num_hdus` + `fits_movabs_hdu`, and do not write anything to stdout until all HDUs are modeled and the FITS handle is closed successfully [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node36.html; VERIFIED: src/fits2json.c:486-495; VERIFIED: 03-CONTEXT.md].

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| CFITSIO | 4.2.0 [VERIFIED: `pkg-config --modversion cfitsio`; `/usr/local/include/fitsio.h`] | Open FITS files, honor selector syntax, count HDUs, move across HDUs, read header records and long strings [VERIFIED: src/fits2json.c; CITED: node35.html; CITED: node36.html; CITED: node38.html; CITED: node73.html] | Locked project dependency and official FITS parser; avoids hand-rolled FITS parsing [VERIFIED: REQUIREMENTS.md; VERIFIED: copilot-instructions.md] |
| Existing in-file JSON emitter | repo-local [VERIFIED: src/fits2json.c:119-189,368-452] | Escape JSON strings and serialize Phase 2 HDU/card objects [VERIFIED: src/fits2json.c] | Already present, already compatible with the locked Phase 2 object contract, and consistent with the single-C constraint [VERIFIED: 02-CONTEXT.md; VERIFIED: 03-CONTEXT.md] |

### Supporting

| Tool | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| GNU Make | 4.3 [VERIFIED: `make --version`] | Build `src/fits2json` from `src/Makefile` [VERIFIED: src/Makefile] | Standard local build path for all smoke verification [VERIFIED: copilot-instructions.md] |
| GCC | 13.3.0 [VERIFIED: `gcc --version`] | Compile the single C translation unit [VERIFIED: src/Makefile] | Standard local compiler for this repo [VERIFIED: src/Makefile] |
| Python 3 | 3.12.3 [VERIFIED: `python3 --version`] | Repo-local smoke testing via JSON parse/assert scripts [VERIFIED: test/phase2_selected_hdu_smoke.py] | Use for Phase 3 smoke regression coverage [VERIFIED: test/phase2_selected_hdu_smoke.py] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `fits_get_num_hdus` + `fits_movabs_hdu` [CITED: node36.html] | `fits_movrel_hdu` loop until EOF [CITED: node36.html] | Relative traversal depends on current CHDU state; absolute traversal is safer for keeping selectorless mode independent from explicit-selector behavior [CITED: node36.html; VERIFIED: src/fits2json.c] |
| Build whole document in memory before stdout write [VERIFIED: src/fits2json.c close-before-emit pattern] | Stream `[` then each HDU as it is read | Streaming risks partial JSON if a later HDU read fails; the roadmap explicitly wants pipe-safe output and Phase 4 later hardens no-partial failure behavior [VERIFIED: ROADMAP.md; VERIFIED: src/fits2json.c] |
| Top-level array only [VERIFIED: 03-CONTEXT.md] | Top-level object with file metadata | Violates locked Phase 3 contract and deferred-items list unless strictly required, which current evidence does not show [VERIFIED: 03-CONTEXT.md] |

**Installation:** No new dependency is required for Phase 3 beyond the existing CFITSIO/GCC/Make/Python toolchain already in use by the repo [VERIFIED: src/Makefile; VERIFIED: test/phase2_selected_hdu_smoke.py].

## Architecture Patterns

### Recommended Project Structure
```text
src/
└── fits2json.c              # keep runtime in one C file [VERIFIED: copilot-instructions.md]

test/
├── phase2_selected_hdu_smoke.py   # keep explicit-selector contract coverage [VERIFIED: existing file]
└── phase3_whole_file_smoke.py     # add selectorless array coverage [VERIFIED: research recommendation]

testdata/
├── IRPH0189.HDR            # existing 2-HDU fixture [VERIFIED: fixture audit]
├── LSPN2790.HDR            # existing 1-HDU fixture [VERIFIED: fixture audit]
└── phase2-edge.fits        # existing long-string/HIERARCH fixture [VERIFIED: fixture audit]
```

### Pattern 1: Branch on selector presence before choosing output shape
**What:** Determine selector-vs-selectorless once, then keep explicit mode on the current Phase 2 path and whole-file mode on a separate array path [VERIFIED: src/fits2json.c:205-208,455-495].  
**When to use:** Always at `main` dispatch time [VERIFIED: src/fits2json.c].  
**Example:**
```c
/* Source: src/fits2json.c + Phase 3 recommendation */
fits_get_hdu_num(fptr, &current_hdu);

if (selector_was_provided(argv[1], current_hdu)) {
    app_status = read_current_hdu_model(fptr, &model, &status);
    /* close file, then emit one object */
} else {
    app_status = read_all_hdu_models(fptr, &document, &status);
    /* close file, then emit one top-level array */
}
```
[VERIFIED: src/fits2json.c:205-208,476-495; CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node21.html]

### Pattern 2: Absolute HDU traversal for selectorless mode
**What:** Count HDUs once with `fits_get_num_hdus`, then loop `hdunum = 1..nhdus` using `fits_movabs_hdu` and reuse the current-HDU reader [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node36.html].  
**When to use:** Only when no selector is present [VERIFIED: 03-CONTEXT.md].  
**Example:**
```c
/* Source: CFITSIO HDU Access docs + current model reader */
int nhdus = 0;
int hdunum;

fits_get_num_hdus(fptr, &nhdus, status);
for (hdunum = 1; hdunum <= nhdus && *status == 0; hdunum++) {
    struct hdu_model model;
    memset(&model, 0, sizeof(model));

    fits_movabs_hdu(fptr, hdunum, NULL, status);
    if (*status) break;

    app_status = read_current_hdu_model(fptr, &model, status);
    if (app_status != 0) break;

    app_status = append_hdu_model(&document, &model);
    if (app_status != 0) break;
}
```
[CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node36.html; VERIFIED: src/fits2json.c:323-365]

### Pattern 3: Keep the per-HDU reader and split only the emitter seam
**What:** Reuse the existing current-HDU modeling logic unchanged and refactor only the emission boundary so one helper emits an object body and wrappers decide top-level shape [VERIFIED: src/fits2json.c:323-452].  
**When to use:** Phase 3 implementation; do not duplicate card serialization for array mode [VERIFIED: 03-CONTEXT.md].  
**Example:**
```c
/* Source: src/fits2json.c */
static int emit_hdu_json_object(FILE *stream, const struct hdu_model *model); /* no newline */
static int emit_single_hdu_json(FILE *stream, const struct hdu_model *model); /* object + '\n' + fflush */
static int emit_hdu_array_json(FILE *stream, const struct fits_document *doc); /* '[' object ',' ... ']' '\n' */
```
[VERIFIED: src/fits2json.c:368-452]

### Anti-Patterns to Avoid
- **Do not reuse selectorless traversal for explicit mode:** explicit selector mode must stay a single object, not a one-element array [VERIFIED: 03-CONTEXT.md].  
- **Do not stream array punctuation before traversal finishes:** it weakens the current close-before-emit safety property [VERIFIED: src/fits2json.c:486-495].  
- **Do not renumber HDUs by array index:** Phase 2 already emits `index` from `fits_get_hdu_num`, which is 1-based for the primary HDU [CITED: node36.html; VERIFIED: src/fits2json.c:328].  
- **Do not parse selector syntax yourself:** CFITSIO already supports extended filename selectors on open [CITED: node35.html].  

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| FITS selector parsing | Custom parsing for `[0]`, `[GTI]`, `+2` [VERIFIED: current usage text] | `fits_open_file` with CFITSIO extended filename syntax [CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node35.html] | Phase 1/2 already rely on CFITSIO selector behavior; hand-rolling risks contract drift [VERIFIED: ROADMAP.md; VERIFIED: 02-CONTEXT.md] |
| Whole-file HDU discovery | Loop until guessed EOF without upfront count | `fits_get_num_hdus` [CITED: node36.html] | Official API returns total fully defined HDUs and does not change current HDU [CITED: node36.html] |
| HDU positioning | Manual stateful increments | `fits_movabs_hdu` [CITED: node36.html] | Absolute positioning preserves file order with less coupling to current CHDU state [CITED: node36.html] |
| Card parsing / long-string folding / key classification | New parser for raw FITS cards | Existing `normalize_card` flow using `fits_read_record`, `fits_read_keyn`, `fits_get_keyclass`, `fits_get_keytype`, `fits_read_key_longstr` [VERIFIED: src/fits2json.c:225-320; CITED: node38.html; CITED: node52.html; CITED: node73.html] | Phase 2 already solved FITS-04 edge cases here; duplicating it is regression risk [VERIFIED: 02-VERIFICATION.md] |

**Key insight:** Phase 3 is a document-wrapping problem, not a new FITS parsing problem [VERIFIED: 03-CONTEXT.md; VERIFIED: 02-01-SUMMARY.md].

## Common Pitfalls

### Pitfall 1: Accidentally changing explicit selector mode into array mode
**What goes wrong:** `file[0]` starts returning `[ { ... } ]` instead of `{ ... }` [VERIFIED: Phase 3 locked decisions].  
**Why it happens:** Developers unify both paths too early at the top-level emitter [ASSUMED].  
**How to avoid:** Keep separate top-level emitters and branch on selector presence before output shape is chosen [VERIFIED: 03-CONTEXT.md; VERIFIED: src/fits2json.c].  
**Warning signs:** Existing explicit-selector smoke assertions fail on top-level type/key set [VERIFIED: test/phase2_selected_hdu_smoke.py:71-83].

### Pitfall 2: Traversal logic that depends on the current CHDU
**What goes wrong:** Selectorless order or starting point changes if open-time selector handling changes later [CITED: node21.html].  
**Why it happens:** Relative traversal uses the current HDU as implicit state [CITED: node36.html].  
**How to avoid:** In selectorless mode, count first and use `fits_movabs_hdu` from `1..nhdus` [CITED: node36.html].  
**Warning signs:** Output starts at the wrong HDU or skips the primary HDU on selectorless input [CITED: node21.html].

### Pitfall 3: Partial JSON from early stdout writes
**What goes wrong:** A later CFITSIO/modeling failure leaves `[` or several objects already on stdout [VERIFIED: roadmap concern + current close-before-emit design].  
**Why it happens:** Emission is interleaved with traversal [VERIFIED: current code avoids this for one HDU].  
**How to avoid:** Build all `hdu_model`s first, close FITS file, then emit exactly once [VERIFIED: src/fits2json.c:486-495; VERIFIED: ROADMAP.md].  
**Warning signs:** Array writer begins before the final `fits_close_file` call [VERIFIED: src/fits2json.c].

### Pitfall 4: Renumbering `index` from 0 because the selector syntax uses `[0]`
**What goes wrong:** Array element 0 gets `"index":0`, breaking Phase 2 semantics [CITED: node21.html; VERIFIED: src/fits2json.c:328].  
**Why it happens:** CFITSIO selector numbers in filenames are 0-based for extensions, but `fits_get_hdu_num` reports CHDU as 1-based [CITED: node21.html; CITED: node36.html].  
**How to avoid:** Keep `model.index` sourced only from `fits_get_hdu_num` [VERIFIED: src/fits2json.c:328].  
**Warning signs:** Explicit `file[1]` no longer reports `"index":2` [VERIFIED: local run of `./src/fits2json 'testdata/IRPH0189.HDR[1]'`].

### Pitfall 5: Assuming existing repo fixtures cover every HDU type
**What goes wrong:** Planner thinks `BINARY_TBL` is smoke-covered when current repo fixtures only showed `IMAGE_HDU` and `ASCII_TBL` in the audited multi-HDU files [VERIFIED: fixture audit over `testdata/*` using CFITSIO + current binary].  
**Why it happens:** The code supports `BINARY_TBL`, but the current local fixtures do not demonstrate it [VERIFIED: src/fits2json.c:191-203; VERIFIED: fixture audit].  
**How to avoid:** Treat `BINARY_TBL` support as code-covered but not repo-smoke-covered unless a new fixture is added [VERIFIED: fixture audit].  
**Warning signs:** Phase 3 smoke passes without ever exercising `BINARY_TBL` [VERIFIED: fixture audit].

## Code Examples

Verified planner-ready patterns:

### Selectorless whole-file traversal
```c
/* Source: CFITSIO HDU Access docs + current read_selected_hdu_model seam */
int read_all_hdu_models(fitsfile *fptr, struct fits_document *doc, int *status)
{
    int nhdus = 0;
    int hdunum;
    int app_status = 0;

    fits_get_num_hdus(fptr, &nhdus, status);
    if (*status) {
        return *status;
    }

    for (hdunum = 1; hdunum <= nhdus; hdunum++) {
        struct hdu_model model;
        memset(&model, 0, sizeof(model));

        fits_movabs_hdu(fptr, hdunum, NULL, status);
        if (*status) {
            free_hdu_model(&model);
            return *status;
        }

        app_status = read_current_hdu_model(fptr, &model, status);
        if (app_status != 0) {
            free_hdu_model(&model);
            return app_status;
        }

        app_status = append_hdu_model(doc, &model);
        if (app_status != 0) {
            free_hdu_model(&model);
            return app_status;
        }
    }

    return 0;
}
```
[CITED: https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node36.html; VERIFIED: src/fits2json.c:323-365]

### Top-level array emission without duplicating Phase 2 object serialization
```c
/* Source: current emit_hdu_json structure */
static int emit_hdu_array_json(FILE *stream, const struct fits_document *doc)
{
    size_t i;
    int status = write_text(stream, "[");

    if (status != 0) return status;

    for (i = 0; i < doc->count; i++) {
        if (i > 0 && fputc(',', stream) == EOF) {
            return APP_STATUS_WRITE;
        }

        status = emit_hdu_json_object(stream, &doc->hdus[i]); /* no newline here */
        if (status != 0) return status;
    }

    status = write_text(stream, "]\n");
    if (status != 0) return status;

    return fflush(stream) == EOF ? APP_STATUS_WRITE : 0;
}
```
[VERIFIED: src/fits2json.c:368-452]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase 2 rejected selectorless invocation with a stderr message and no stdout [VERIFIED: src/fits2json.c:476-480; VERIFIED: test/phase2_selected_hdu_smoke.py:50-57] | Phase 3 should accept selectorless invocation and return a top-level JSON array of Phase 2 HDU objects [VERIFIED: 03-CONTEXT.md; VERIFIED: ROADMAP.md] | Phase 3 planning target on 2026-04-12 [VERIFIED: 03-CONTEXT.md] | Whole-file conversion becomes pipe-safe without changing explicit-selector object output [VERIFIED: 03-CONTEXT.md] |

**Deprecated/outdated:**
- Selectorless rejection in `main` is a Phase 2 guardrail that Phase 3 should replace only for the no-selector branch [VERIFIED: src/fits2json.c:476-480; VERIFIED: 02-01-SUMMARY.md].

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Developers are more likely to introduce explicit-mode contract drift if they unify top-level emitters too early [ASSUMED] | Common Pitfalls | Low — this affects task ordering, not the target behavior |

## Open Questions (RESOLVED)

1. **Should Phase 3 add a synthetic multi-HDU fixture, or is existing repo coverage enough?**
    - What we know: Existing repo fixtures include many 2-HDU files such as `IRPH0189.HDR`, and a local CFITSIO audit showed those files expose 2 HDUs in order [VERIFIED: fixture audit].
    - What's unclear: None of the audited local multi-HDU fixtures exposed `BINARY_TBL` in this session [VERIFIED: fixture audit].
    - Resolution: Use existing `IRPH0189.HDR` plus a 1-HDU fixture for minimum Phase 3 scope, and log `BINARY_TBL` smoke as a non-blocking follow-up instead of expanding Phase 3 scope with another synthetic fixture [VERIFIED: fixture audit].

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| make | Build + smoke tests | ✓ [VERIFIED: local audit] | 4.3 [VERIFIED: `make --version`] | — |
| gcc | Build | ✓ [VERIFIED: local audit] | 13.3.0 [VERIFIED: `gcc --version`] | — |
| python3 | Smoke tests | ✓ [VERIFIED: local audit] | 3.12.3 [VERIFIED: `python3 --version`] | — |
| CFITSIO library | Runtime + FITS traversal | ✓ [VERIFIED: local audit] | 4.2.0 [VERIFIED: pkg-config + fitsio.h] | — |

**Missing dependencies with no fallback:** None [VERIFIED: local audit].  
**Missing dependencies with fallback:** None [VERIFIED: local audit].

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Custom Python stdlib smoke scripts with `subprocess` + `json` assertions [VERIFIED: test/phase2_selected_hdu_smoke.py] |
| Config file | none [VERIFIED: repository inspection] |
| Quick run command | `make -C src fits2json && python3 test/phase3_whole_file_smoke.py` [VERIFIED: planner recommendation] |
| Full suite command | `make -C src fits2json && python3 test/phase2_selected_hdu_smoke.py --cases core && python3 test/phase3_whole_file_smoke.py` [VERIFIED: existing test style + planner recommendation] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HEAD-02 | Selectorless invocation returns one JSON array containing every HDU in file order [VERIFIED: REQUIREMENTS.md; VERIFIED: ROADMAP.md] | smoke | `python3 test/phase3_whole_file_smoke.py` [VERIFIED: planner recommendation] | ❌ Wave 0 |
| CLI-01 | Successful selectorless output is pure JSON on stdout and no success stderr text is mixed in [VERIFIED: REQUIREMENTS.md] | smoke | `python3 test/phase3_whole_file_smoke.py` [VERIFIED: planner recommendation] | ❌ Wave 0 |
| Contract preservation | Explicit `file[0]` / `file[1]` still return one object, not an array [VERIFIED: 03-CONTEXT.md] | smoke | `python3 test/phase3_whole_file_smoke.py` [VERIFIED: planner recommendation] | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `make -C src fits2json && python3 test/phase3_whole_file_smoke.py` [VERIFIED: planner recommendation]
- **Per wave merge:** `make -C src fits2json && python3 test/phase2_selected_hdu_smoke.py --cases core && python3 test/phase3_whole_file_smoke.py` [VERIFIED: planner recommendation]
- **Phase gate:** Full suite green before `/gsd-verify-work` [VERIFIED: workflow config]

### Wave 0 Gaps
- [ ] `test/phase3_whole_file_smoke.py` — add selectorless array coverage on a known 2-HDU fixture such as `IRPH0189.HDR` [VERIFIED: fixture audit]
- [ ] Update or split the current selectorless Phase 2 assertion so it no longer requires rejection once Phase 3 lands [VERIFIED: test/phase2_selected_hdu_smoke.py:50-57]
- [ ] Add equality-style regression: selectorless `IRPH0189.HDR` array elements must match explicit `IRPH0189.HDR[0]` and `IRPH0189.HDR[1]` object outputs exactly [VERIFIED: 03-CONTEXT.md; VERIFIED: current explicit mode]
- [ ] Add single-HDU selectorless smoke: `LSPN2790.HDR` or `phase2-edge.fits` should return a one-element array whose element matches explicit `[0]` output [VERIFIED: fixture audit]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no [VERIFIED: CLI-only local tool shape] | — |
| V3 Session Management | no [VERIFIED: CLI-only local tool shape] | — |
| V4 Access Control | no [VERIFIED: local file reader, no auth model] | — |
| V5 Input Validation | yes [VERIFIED: CLI accepts file path input] | Validate `argc`, keep selector parsing delegated to CFITSIO, and keep JSON escaping in `write_json_string` [VERIFIED: src/fits2json.c:37-49,127-189,466-469; CITED: node35.html] |
| V6 Cryptography | no [VERIFIED: repo scope] | — |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed FITS/header input | Tampering | Let CFITSIO parse FITS structure; report library errors on `stderr`; do not invent a second parser [VERIFIED: src/fits2json.c; CITED: node35.html; CITED: node38.html] |
| Stdout JSON corruption by mixed diagnostics | Tampering | Keep diagnostics on `stderr` and only emit JSON after successful traversal/close [VERIFIED: src/fits2json.c:486-500; VERIFIED: ROADMAP.md] |
| JSON string injection via header content | Tampering | Reuse `write_json_string` escaping for all string fields [VERIFIED: src/fits2json.c:127-189] |

## Sources

### Primary (HIGH confidence)
- `https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node21.html` — CHDU behavior; selectorless opens primary by default; selector syntax context [CITED]
- `https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node35.html` — `fits_open_file` and extended filename selector syntax [CITED]
- `https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node36.html` — `fits_movabs_hdu`, `fits_movrel_hdu`, `fits_get_num_hdus`, `fits_get_hdu_num`, `fits_get_hdu_type` [CITED]
- `https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node38.html` — `fits_get_hdrspace`, `fits_read_record`, `fits_read_keyn` [CITED]
- `https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node52.html` — `fits_get_keytype`, `fits_get_keyclass` [CITED]
- `https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node73.html` — `fits_read_key_longstr`, `fits_free_memory` [CITED]
- `/home/warnock/dev/FITS2JSON/src/fits2json.c` — current model/emitter/error-flow seams [VERIFIED]
- `/home/warnock/dev/FITS2JSON/test/phase2_selected_hdu_smoke.py` — existing smoke coverage and current selectorless rejection assertion [VERIFIED]
- `/home/warnock/dev/FITS2JSON/.planning/phases/03-whole-file-json-emission/03-CONTEXT.md` — locked Phase 3 contract [VERIFIED]

### Secondary (MEDIUM confidence)
- Local environment audit: `make --version`, `gcc --version`, `python3 --version`, `pkg-config --modversion cfitsio`, `/usr/local/include/fitsio.h` [VERIFIED]
- Local fixture audit using CFITSIO symbol calls and current binary over `testdata/*` to identify HDU counts and observed HDU types [VERIFIED]

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - local toolchain and CFITSIO version were directly verified, and API usage was confirmed against official docs [VERIFIED/CITED]
- Architecture: HIGH - Phase 3 constraints and current code seams are explicit in local planning artifacts and `src/fits2json.c` [VERIFIED]
- Pitfalls: MEDIUM - most are directly inferred from current code and locked contracts, but one developer-behavior pitfall remains an assumption [VERIFIED + ASSUMED]

**Research date:** 2026-04-12  
**Valid until:** 2026-05-12 [ASSUMED]

## RESEARCH COMPLETE

**Phase:** 3 - Whole-File JSON Emission  
**Confidence:** HIGH

### Key Findings
- Prefer selectorless traversal with `fits_get_num_hdus` followed by `fits_movabs_hdu(1..N)`; this preserves HDU order and avoids coupling whole-file mode to current CHDU state [CITED: node36.html].
- Reuse the existing current-HDU model reader; the minimal refactor is to add a document container and split the emitter into reusable object-level and top-level-shape wrappers [VERIFIED: src/fits2json.c:323-452].
- Preserve the current close-before-emit discipline for whole-file mode: read all HDUs, close the FITS file, then write one JSON array to stdout [VERIFIED: src/fits2json.c:486-495].
- Add Phase 3 smoke coverage for: 2-HDU selectorless array output, explicit-selector object preservation, and 1-HDU selectorless one-element array behavior [VERIFIED: fixture audit; VERIFIED: test/phase2_selected_hdu_smoke.py].
- Repo-local fixtures currently demonstrate `IMAGE_HDU` + `ASCII_TBL` in multi-HDU files, but not `BINARY_TBL`; planner should treat binary-table smoke as a gap, not as already covered [VERIFIED: fixture audit].

### Ready for Planning
Research complete. Planner can now create Phase 3 PLAN.md files.
