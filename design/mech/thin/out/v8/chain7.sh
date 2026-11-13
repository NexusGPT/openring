#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
T=$REPO_ROOT/design/mech/thin/out/v8
until [ -f $T/chain6.done ]; do perl -e 'select(undef,undef,undef,10)'; done
python3 $T/finalize.py > $T/finalize.log 2>&1
date > $T/chain7.done
