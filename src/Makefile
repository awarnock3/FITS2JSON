CC      = gcc
CFLAGS  = -O2 -Wall -D_POSIX_C_SOURCE=200809L

SRCDIR  = .

SRCS = $(SRCDIR)/listhead.c

OBJS = $(SRCS:$(SRCDIR)/%.c=%.o)

.PHONY: all test clean

all: listhead

listhead: $(OBJS)
	$(CC) $(CFLAGS) -L/usr/local/lib -o listhead $(OBJS) -lcfitsio

%.o: $(SRCDIR)/%.c
	$(CC) $(CFLAGS) -I/usr/local/include -c -o $@ $<

clean:
	rm -f $(OBJS) listhead
	$(MAKE) -C test clean
