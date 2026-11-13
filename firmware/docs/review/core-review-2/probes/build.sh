#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# usage: build.sh <probe.c> <out> [module dir]
M=${3:-$REPO_ROOT/firmware/modules/ring_core}
exec nice -n 19 cc -std=c11 -Wall -Wno-unused-function -I "$M/include" -I "$(dirname "$0")" "$M"/src/*.c "$1" -o "$2"
