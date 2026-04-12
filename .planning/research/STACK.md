# Technology Stack

**Project:** FITS2JSON
**Researched:** 2026-04-12
**Scope:** Add structured JSON FITS-header output to the existing CFITSIO-based C CLI
**Overall confidence:** HIGH

## Recommended Stack

For a small 2025-era native CLI like this, the right stack is still:

- **C**
- **CFITSIO**
- **one small C JSON library**
- **GNU Make + pkg-config**

Do **not** turn this into a Python/Rust rewrite or a larger platform change. This feature is an output-layer extension on top of an already-working CFITSIO traversal path.

### Core Stack

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| C | C17 | Implementation language | Best fit for the existing codebase; no rewrite needed; modern-enough baseline without chasing C23 complexity | MEDIUM |
| CFITSIO | Target latest 4.6.x (`4.6.3` current); support older 4.x where needed | FITS file access, HDU traversal, header parsing | This is already the project’s core dependency and CFITSIO already exposes the header APIs needed for structured extraction | HIGH |
| Jansson | Target `2.15.x` (`2.15.0` current); `2.14+` acceptable | JSON object/array construction and emission | Better choice than hand-rolled JSON or cJSON for this tool because it has typed integers/reals, robust object/array APIs, and direct `FILE*`/fd dumping | HIGH |
| GNU Make | current system version | Build orchestration | Keep the existing build shape; this project is too small to justify CMake/Meson migration just for JSON output | MEDIUM |
| pkg-config | current system version | Dependency discovery | Replaces hardcoded `/usr/local/include` and `/usr/local/lib`; makes CFITSIO/Jansson builds portable across Linux/macOS/package-manager installs | HIGH |

### Supporting / Dev Tools

| Tool | Version | Purpose | When to Use | Confidence |
|------|---------|---------|-------------|------------|
| GCC or Clang | current system compiler | Build and warnings | Compile with `-std=c17 -Wall -Wextra -Wpedantic` in normal builds | MEDIUM |
| AddressSanitizer + UBSan | compiler-supported | Catch memory/UB bugs while adding JSON logic | Enable in debug/test builds, not release builds | MEDIUM |
| jq | current system version | Output validation in tests | Dev/test only; useful for fixture assertions, not required at runtime | LOW |

## Recommended Implementation Approach

### 1. Keep the CLI in C and build on the existing `listhead.c` flow

Do not replace CFITSIO. Do not add a scripting-language wrapper. The correct approach is:

- keep `fits_open_file`
- keep CFITSIO extension selection behavior (`file.fits[2]`, `file.fits[GTI]`, etc.)
- replace raw `printf("%s\n", card)` output with JSON document construction

### 2. Prefer CFITSIO header APIs over manual 80-column parsing

Use CFITSIO to extract structured header information instead of slicing raw card strings yourself.

Recommended API mix:

- **HDU traversal**
  - `fits_get_num_hdus`
  - `fits_movabs_hdu`
  - `fits_get_hdu_type`

- **Header enumeration**
  - `fits_get_hdrspace`
  - `fits_read_record`
  - `fits_read_keyn`

- **Value/class parsing**
  - `fits_parse_value`
  - `fits_get_keytype`
  - `fits_get_keyclass`

- **Long string support**
  - `ffgkcsl` / `fits_get_key_com_strlen`
  - `ffgskyc` / `fits_read_string_key_com`
  - or `ffgkls` for long string retrieval

**Why:** CFITSIO already knows FITS rules, including header classes and long-string `CONTINUE` handling. Re-implementing that logic in ad hoc C string code is unnecessary risk.

### 3. Use Jansson to build the JSON tree, then dump to stdout

Use Jansson for:

- `json_object()`
- `json_array()`
- `json_integer()`
- `json_real()`
- `json_string()`
- `json_true()` / `json_false()`
- `json_dumpf(stdout, ...)`

Recommended output behavior:

- compact JSON by default
- single newline after document
- non-zero exit on any CFITSIO or serialization error
- no partial/invalid JSON on stdout

### 4. Canonical JSON shape: ordered cards array per HDU

For FITS headers, **order matters** and some records repeat. So the canonical representation should be an **array of card objects**, not a single flat JSON object.

Recommended shape:

```json
{
  "file": "example.fits",
  "hdus": [
    {
      "index": 1,
      "type": "IMAGE_HDU",
      "cards": [
        {
          "index": 1,
          "keyword": "SIMPLE",
          "class": "structural",
          "value": true,
          "raw_value": "T",
          "comment": "file conforms to FITS standard",
          "card": "SIMPLE  =                    T / file conforms to FITS standard"
        }
      ],
      "comment": [],
      "history": []
    }
  ]
}
```

### 5. Type mapping

Recommended FITS-to-JSON mapping:

| FITS value kind | JSON representation | Notes |
|-----------------|--------------------|-------|
| Logical (`T`/`F`) | boolean | direct mapping |
| Integer | integer | use `json_integer()` |
| Floating point | number | use `json_real()` |
| String | string | preserve text; normalize FITS quoting |
| `COMMENT` / `HISTORY` / blank cards | arrays of strings and/or card objects | do not drop them |
| Complex / unknown literal | string in MVP | avoid inventing a lossy schema unless explicitly needed |

### 6. Preserve repeated records explicitly

At minimum:

- `COMMENT` -> array
- `HISTORY` -> array

Do **not** collapse repeated cards into one key and lose data.

If you later add a convenience `keywords` object, repeated keyword names should become arrays there too. But for MVP, the **ordered `cards` array** should be the source of truth.

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| JSON library | Jansson | cJSON | cJSON stores numbers as `double` internally, which is a poor fit when exact integer preservation matters |
| JSON emission | Jansson | hand-rolled `printf` escaping | Too easy to get escaping, commas, and error handling wrong |
| Header extraction | CFITSIO structured APIs | parse `fits_read_record()` text manually | More brittle, especially around long strings and special card types |
| Build config | `pkg-config` | hardcoded `/usr/local/include` + `/usr/local/lib` | Not portable across common installations |
| Scope | extend existing CLI | rewrite in another language | Wasteful for a small brownfield feature |

## What NOT to Use

### Don't hand-roll JSON
Avoid building JSON with manual string concatenation. It is the fastest path to invalid escaping and nondeterministic output bugs.

### Don't use `fits_hdr2str` as the main JSON path
`fits_hdr2str` is useful for passing raw headers to other libraries (for example WCS tooling), but it is not the right primary interface for structured JSON emission.

### Don't use cJSON here
cJSON is small, but its numeric model is centered on `double`, which is a bad default for exact FITS integer keyword preservation.

### Don't keep hardcoded include/library paths
Replace:

- `-I/usr/local/include`
- `-L/usr/local/lib`

with `pkg-config`.

## Installation

### Debian/Ubuntu

```bash
sudo apt-get install build-essential pkg-config libcfitsio-dev libjansson-dev
```

### macOS (Homebrew)

```bash
brew install cfitsio jansson pkg-config
```

### Compile Example

```bash
cc -std=c17 -O2 -Wall -Wextra -Wpedantic \
  $(pkg-config --cflags cfitsio jansson) \
  src/listhead.c \
  -o fits2json \
  $(pkg-config --libs cfitsio jansson)
```

### Recommended Debug Build

```bash
cc -std=c17 -O0 -g -Wall -Wextra -Wpedantic \
  -fsanitize=address,undefined -fno-omit-frame-pointer \
  $(pkg-config --cflags cfitsio jansson) \
  src/listhead.c \
  -o fits2json \
  $(pkg-config --libs cfitsio jansson)
```

## Final Recommendation

**Use:**
- **C17**
- **CFITSIO 4.6.x**
- **Jansson 2.15.x**
- **GNU Make + pkg-config**

**Implementation strategy:**
- keep the current CFITSIO-based CLI
- enumerate HDUs with CFITSIO
- read header cards with CFITSIO's structured APIs
- build a JSON tree with Jansson
- emit one deterministic JSON document to stdout

That is the standard 2025 stack for this feature: **small, native, portable, and no rewrite.**

## Sources

### Official / High-confidence
- CFITSIO official C user's guide — HDU traversal (`fits_movabs_hdu`, `fits_get_num_hdus`, `fits_get_hdu_type`):  
  https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node36.html
- CFITSIO official C user's guide — header read APIs (`fits_get_hdrspace`, `fits_read_record`, `fits_read_keyn`, long string helpers):  
  https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node38.html
- CFITSIO official C user's guide — parsing helpers (`fits_parse_value`, `fits_get_keytype`, `fits_get_keyclass`):  
  https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node52.html
- CFITSIO official C user's guide — `fits_hdr2str` intent:  
  https://heasarc.gsfc.nasa.gov/docs/software/fitsio/c/c_user/node58.html
- CFITSIO latest release (`cfitsio-4.6.3`, published 2025-09-30):  
  https://github.com/HEASARC/cfitsio/releases/tag/cfitsio-4.6.3

### Official / High-confidence
- Jansson API reference (`json_object`, `json_array`, `json_integer`, `json_real`, `json_dumpf`, `json_dumpfd`):  
  https://jansson.readthedocs.io/en/latest/apiref.html
- Jansson latest release (`v2.15.0`, published 2026-01-24):  
  https://github.com/akheron/jansson/releases/tag/v2.15.0

### Official / High-confidence
- cJSON header showing numeric storage (`valueint`, `valuedouble`) and print API:  
  https://raw.githubusercontent.com/DaveGamble/cJSON/master/cJSON.h
- cJSON latest release (`v1.7.19`, published 2025-09-09):  
  https://github.com/DaveGamble/cJSON/releases/tag/v1.7.19
