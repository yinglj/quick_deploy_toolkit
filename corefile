#!/bin/sh

if test $# -ne 2; then
    echo "Usage: `basename $0 .sh` exec-file core-file" 1>&2
    exit 1
fi

if test ! -r $1; then
    echo "exec-file $1 not found." 1>&2
    exit 1
fi

if test ! -r $2; then
    echo "core-file $2 not found." 1>&2
    exit 1
fi

# GDB doesn't allow "thread apply all bt" when the process isn't
# threaded; need to peek at the process to determine if that or the
# simpler "bt" should be used.

backtrace="bt"

GDB=${GDB:-/usr/bin/gdb}

# Run GDB, strip out unwanted noise.
# --readnever is no longer used since .gdb_index is now in use.
$GDB --quiet -nx <<EOF 2>&1 | 
set width 0
set height 0
set pagination no
exec-file $1
core-file $2
$backtrace
info proc
!ls -l $2
EOF
/bin/sed -n \
    -e 's/^\((gdb) \)*//' \
    -e '/^#/p' \
    -e '/billing billing/p' \
    -e '/exe =/p' \
    -e '/^Thread/p' |uniq
echo "-----------------------------------------------------------------------------------------------"
