# Architecture Patterns

**Domain:** FITS header to JSON CLI export
**Researched:** 2026-04-12

## Recommended Architecture

For this codebase, the right shape is **still one CLI binary**, but internally split into a small pipeline:

**CLI/options -> FITS traversal -> header normalization -> JSON emission**

That matches how FITS-header-to-JSON tools are usually structured when they stay close to CFITSIO: the FITS library handles file/HDU/card access, a thin normalization layer converts FITS header cards into a stable in-memory representation, and a serializer emits JSON. The important boundary is **not** “CFITSIO vs app”, but **reader vs normalizer vs writer**.

For this repository, do **not** jump straight to a many-module architecture. First extract helpers from `main`, then split into 3-4 small C modules only when the seams are clear. This keeps the project aligned with its current single-program shape while making JSON export testable.

## Recommended Architecture

```text
main / CLI
  -> open FITS with CFITSIO
  -> iterate target HDUs
  -> build normalized per-HDU header model
  -> stream one JSON document to stdout
```

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| `main` / `cli` | Parse args, choose mode, manage exit codes, own top-level JSON document shape | `fits_reader`, `json_writer` |
| `fits_reader` | Open FITS file, detect selected/current HDU, iterate HDUs and header records via CFITSIO | `header_model` |
| `header_model` / `normalizer` | Convert CFITSIO keyword/card data into a normalized record model; classify normal keywords vs `COMMENT` / `HISTORY` / blank-like records; preserve order | `json_writer` |
| `json_writer` | Emit valid deterministic JSON, escape strings, write arrays/objects without knowing CFITSIO details | stdout |
| `error/reporting` (can stay in `main` initially) | Map CFITSIO status and usage failures to stable stderr + exit behavior | all |

## Data Flow

1. **Parse CLI input**
   - Accept the existing CFITSIO-style filename or extension selector unchanged.
   - Do **not** re-implement extension parsing in your code; CFITSIO already supports `file.fits[2]`, `file.fits[GTI]`, etc.

2. **Open FITS file**
   - `fits_open_file`
   - If open fails, report on `stderr`, return non-zero, emit no partial JSON.

3. **Determine traversal mode**
   - Use current-position logic (`fits_get_hdu_num`) plus the existing “single vs all HDUs” behavior.
   - Single-HDU selection stays in traversal, not in the JSON writer.

4. **Iterate HDUs**
   - For each HDU:
     - capture HDU index
     - optionally capture HDU type (`fits_get_hdu_type`) for richer JSON metadata
     - get keyword count with `fits_get_hdrspace`

5. **Read header records**
   - Prefer `fits_read_keyn` for structured `keyname/value/comment`.
   - Keep `fits_read_record` as a fallback only if you need the raw card for debugging or edge preservation.

6. **Normalize records**
   - Convert each FITS card into a small internal record:
     - keyword/value/comment record
     - `COMMENT` entry
     - `HISTORY` entry
     - optional raw/blank/unclassified entry if preservation matters
   - Preserve original card order in the internal model.

7. **Emit JSON**
   - Start top-level document once.
   - Emit one HDU object at a time.
   - Close document after traversal finishes.
   - This allows one JSON document for all HDUs without holding the full file in memory.

8. **Close FITS and finalize**
   - `fits_close_file`
   - only print CFITSIO diagnostics to `stderr`
   - `stdout` remains JSON-only

## Recommended Internal Model

Use a **small per-HDU accumulator**, not a whole-file DOM.

```c
typedef enum {
    REC_VALUE,
    REC_COMMENT,
    REC_HISTORY,
    REC_OTHER
} record_kind;

typedef struct {
    record_kind kind;
    char key[FLEN_KEYWORD];
    char value[FLEN_VALUE];
    char comment[FLEN_COMMENT];
} header_record;

typedef struct {
    int hdu_index;
    int hdu_type;       /* optional but useful */
    size_t record_count;
    header_record *records;
} hdu_header;
```

### Why this model

- FITS headers are fundamentally **ordered card streams**
- JSON objects are not a safe canonical representation for repeated cards
- `COMMENT` and `HISTORY` are explicitly repeatable
- preserving order internally avoids corner-case rewrites later

So the authoritative internal structure should be **records in order**. Any grouped JSON view is derived from that.

## JSON Shape Recommendation

For this project, prefer an HDU-oriented structure like:

```json
{
  "hdus": [
    {
      "index": 1,
      "type": "IMAGE",
      "keywords": {
        "SIMPLE": { "value": true, "comment": "" },
        "BITPIX": { "value": 8, "comment": "" }
      },
      "comment": [
        "NOTE   A Guiding problems"
      ],
      "history": []
    }
  ]
}
```

### Important note

This JSON shape is good for scripts, but the **internal model should still preserve card order**. If later you discover duplicate non-comment keywords or need strict round-tripping, you can add:

- `records: [...]` as the canonical ordered form, or
- arrays for duplicate keywords

without reworking FITS traversal.

## Patterns to Follow

### Pattern 1: Reader / Normalizer / Writer split
**What:** Separate CFITSIO access from JSON formatting.  
**When:** Immediately; this is the minimum refactor that de-risks the feature.  
**Why:** It prevents `printf`-style JSON generation from becoming tangled with FITS iteration.

### Pattern 2: Per-HDU accumulation, streamed top-level output
**What:** Accumulate one HDU, serialize it, then move on.  
**When:** Default approach.  
**Why:** Keeps memory low and fits a CLI that writes one document to stdout.

### Pattern 3: Preserve FITS semantics in the model, not the writer
**What:** Classify `COMMENT`, `HISTORY`, and ordinary keywords before serialization.  
**When:** During normalization.  
**Why:** Writers should not need FITS-specific branching logic.

## Anti-Patterns to Avoid

### Anti-Pattern 1: Interleaving CFITSIO calls with ad hoc JSON `printf`s
**Why bad:** hard to test, easy to break commas/brackets, impossible to reason about error cleanup  
**Instead:** build a per-HDU model, then serialize

### Anti-Pattern 2: Writing a custom FITS card parser
**Why bad:** FITS header syntax has edge cases; CFITSIO already exposes structured keyword reads  
**Instead:** use `fits_read_keyn`, `fits_get_hdrspace`, and related helpers

### Anti-Pattern 3: Exploding the codebase into many files too early
**Why bad:** high refactor cost for a small CLI, weak test coverage today  
**Instead:** first extract static helper functions inside `listhead.c`, then split once seams stabilize

### Anti-Pattern 4: Treating JSON object keys as the only source of truth
**Why bad:** repeated cards and ordering semantics get lost  
**Instead:** keep ordered records internally; emit grouped JSON as a view

## Suggested Build Order

1. **Refactor without changing behavior**
   - Extract from `main`:
     - `parse_args`
     - `open_fits`
     - `iterate_hdus`
     - `print_usage`
   - Keep raw header printing working

2. **Introduce header normalization**
   - Add `header_record` / `hdu_header`
   - Replace direct `printf("%s\n", card)` flow with record collection
   - Still no JSON yet

3. **Add JSON writer**
   - Implement string escaping
   - Implement object/array emission
   - Unit-test formatting against fixed small inputs

4. **Switch CLI output to JSON**
   - Preserve current single-HDU/all-HDU behavior
   - Ensure `stdout` is valid JSON and `stderr` is diagnostics only

5. **Then split files if needed**
   - `cli.c`
   - `fits_reader.c`
   - `header_model.c`
   - `json_writer.c`

6. **Finally fix build plumbing**
   - update `src/Makefile` for multiple objects
   - prefer overridable flags or `pkg-config cfitsio`

## Small-Codebase Advice

For this milestone, the best fit is:

- **one binary**
- **3-4 internal responsibilities**
- **no new external JSON dependency unless necessary**
- **no generic plugin architecture**
- **no whole-program rewrite**

A good intermediate state is even simpler:

- keep one `.c` file
- add `static` helper functions
- add one small header-model struct
- add one JSON writer section

That is enough to create real boundaries without over-engineering.

## Build-Order Implications for the Roadmap

- **Phase 1 should be seam extraction**, not JSON features first
- **Phase 2 should be normalization**, because repeated `COMMENT` / `HISTORY` handling belongs there
- **Phase 3 should be JSON emission**, once the internal model is stable
- **Phase 4 should be tests + Makefile cleanup**, to lock behavior down

This order reduces rewrite risk because the current fragility is concentrated in `main`.

## Sources

- Project context: `/home/warnock/dev/FITS2JSON/.planning/PROJECT.md`
- Existing architecture: `/home/warnock/dev/FITS2JSON/.planning/codebase/ARCHITECTURE.md`
- Existing concerns: `/home/warnock/dev/FITS2JSON/.planning/codebase/CONCERNS.md`
- Current implementation: `/home/warnock/dev/FITS2JSON/src/listhead.c`
- Build layout: `/home/warnock/dev/FITS2JSON/src/Makefile`
- CFITSIO keyword reading routines (official docs): https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node38.html
- CFITSIO installed headers observed locally: `/usr/include/fitsio.h`, `/usr/include/longnam.h`

## Confidence

**Architecture fit for this codebase:** HIGH  
**CFITSIO capability claims:** HIGH  
**“Typical tool structure” generalization:** MEDIUM — based on common converter design patterns plus CFITSIO interfaces, not a single formal standard
