CC ?= cc
CFLAGS ?= -O2 -Wall -D_POSIX_C_SOURCE=200809L
CPPFLAGS ?=
LDFLAGS ?=
LDLIBS ?=
PYTHON ?= python3
PKG_CONFIG ?= pkg-config
CFITSIO_PKG ?= cfitsio
CFITSIO_CFLAGS ?= $(shell $(PKG_CONFIG) --cflags $(CFITSIO_PKG) 2>/dev/null)
CFITSIO_LIBS ?= $(shell $(PKG_CONFIG) --libs $(CFITSIO_PKG) 2>/dev/null)

SRCDIR = .
SRCS = $(SRCDIR)/fits2json.c
OBJS = $(SRCS:$(SRCDIR)/%.c=%.o)
HELPER = ../test/phase2_make_edge_fixture
EDGE_FIXTURE = ../testdata/phase2-edge.fits

.PHONY: all test clean check-cfitsio check-python force rebuild-fits2json
.DELETE_ON_ERROR:

all: fits2json

check-cfitsio:
	@if [ -z "$(strip $(CFITSIO_LIBS))" ]; then \
		echo "CFITSIO not found. Install the cfitsio development package or pass CFITSIO_CFLAGS=... CFITSIO_LIBS=..." >&2; \
		exit 1; \
	fi

check-python:
	@command -v "$(PYTHON)" >/dev/null 2>&1 || { \
		echo "Python 3 not found. Install Python 3 or pass PYTHON=/path/to/python3" >&2; \
		exit 1; \
	}

fits2json: $(OBJS) | check-cfitsio
	$(CC) $(LDFLAGS) -o $@ $(OBJS) $(LDLIBS) $(CFITSIO_LIBS)

%.o: $(SRCDIR)/%.c | check-cfitsio
	$(CC) $(CPPFLAGS) $(CFITSIO_CFLAGS) $(CFLAGS) -c -o $@ $<

$(HELPER): ../test/phase2_make_edge_fixture.c | check-cfitsio
	$(CC) $(CPPFLAGS) $(CFITSIO_CFLAGS) $(CFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS) $(CFITSIO_LIBS)

force:

$(EDGE_FIXTURE): force $(HELPER)
	$(HELPER) $(EDGE_FIXTURE)

rebuild-fits2json: force
	$(MAKE) --always-make fits2json

test: check-python rebuild-fits2json $(HELPER) $(EDGE_FIXTURE)
	$(PYTHON) ../test/phase2_selected_hdu_smoke.py
	$(PYTHON) ../test/phase3_whole_file_smoke.py
	$(PYTHON) ../test/phase4_cli_contract_smoke.py

clean:
	rm -f $(OBJS) fits2json $(HELPER) $(EDGE_FIXTURE)
	rm -rf ../test/__pycache__
