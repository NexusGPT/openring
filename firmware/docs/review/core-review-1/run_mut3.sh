#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# Mutation runner: copies the module into the review folder, applies one perl edit, runs the host tests on the copy.
# Writes only under the review folder. Usage: sh run_mut.sh
R=$REPO_ROOT/firmware/docs/review/core-review-1
SRC=$REPO_ROOT/firmware/modules/ring_core
HOSTSH=$REPO_ROOT/firmware/tests/core/host/run_host_tests.sh
OUT=$R/mut-results3.tsv
: > $OUT
run() { # name file perl-expr description
  n=$1; f=$2; expr=$3; desc=$4
  d=$R/mut/$n
  mkdir -p $d
  cp -R $SRC/. $d/ring_core/
  cp $d/ring_core/$f $d/orig.txt
  perl -0pi -e "$expr" $d/ring_core/$f > $d/perl.log 2>&1
  diff $d/orig.txt $d/ring_core/$f > $d/change.diff 2>&1
  if [ ! -s $d/change.diff ]; then printf "%s\tNOT-APPLIED\t0\t-\t%s\n" "$n" "$desc" >> $OUT; return; fi
  HOST_BUILD_DIR=$d/build nice -n 19 sh $HOSTSH $d/ring_core > $d/host-run.log 2>&1
  nf=$(grep -c '^FAIL ' $d/host-run.log)
  res=$(grep '^RESULT' $d/host-run.log | tail -1)
  names=$(grep '^FAIL ' $d/host-run.log | sed 's/^FAIL //' | cut -d' ' -f1 | head -4 | tr '\n' ',')
  if [ "$res" = "RESULT FAIL" ]; then c=yes; else c=NO; fi
  if grep -q 'compile failed' $d/host-run.log; then c=COMPILE-ERROR; fi
  printf "%s\t%s\t%s\t%s\t%s\n" "$n" "$c" "$nf" "$names" "$desc" >> $OUT
}
SA=src/state_actions.c; GE=src/gesture.c; CO=src/core.c; ST=src/state_table.c
run m38b $CO 's/\t\t\tc->mic_rail = false;  \/\* a reboot[^\n]*\n//' "mic rail not cleared on power loss into BOOT"
run m55 $GE 's/\tg->second = false;\n\tif \(g->short_pending\) \{/\tg->second = false;\n\tif (0) {/' "second press no longer cancels the pending short press"
echo done >> $OUT
