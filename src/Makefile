CC      = gcc
CFLAGS  = -O2 -Wall -D_POSIX_C_SOURCE=200809L

SRCDIR  = .

SRCS = $(SRCDIR)/fits2json.c

OBJS = $(SRCS:$(SRCDIR)/%.c=%.o)

.PHONY: all clean

all: fits2json

fits2json: $(OBJS)
	$(CC) $(CFLAGS) -L/usr/local/lib -o fits2json $(OBJS) -lcfitsio

%.o: $(SRCDIR)/%.c
	$(CC) $(CFLAGS) -I/usr/local/include -c -o $@ $<

clean:
	rm -f $(OBJS) fits2json
