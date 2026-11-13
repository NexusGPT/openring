#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
T=$REPO_ROOT/design/mech/thin/out/v8
( $T/run_check.sh 8 v8c; $T/run_check.sh 10 v8c; $T/run_check.sh 13 v8c ) &
( $T/run_default.sh v8c; $T/run_check.sh 11 v8c; $T/run_broken.sh broken_trunk_full ) &
wait
date > $T/lanes.done
