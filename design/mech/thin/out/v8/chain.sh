#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# runs after the US 7 run: one heavy run at a time, nice -n 19 (inside run_check.sh / run_broken.sh)
T=$REPO_ROOT/design/mech/thin/out/v8
until grep -q "^exit" $T/v8_us7.log; do perl -e 'select(undef,undef,undef,10)'; done
for N in 8 10 11 12 13; do
  $T/run_check.sh $N v8
done
$T/run_broken.sh broken_trunk
date > $T/chain.done
