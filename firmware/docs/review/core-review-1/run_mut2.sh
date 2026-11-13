#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# Mutation runner: copies the module into the review folder, applies one perl edit, runs the host tests on the copy.
# Writes only under the review folder. Usage: sh run_mut.sh
R=$REPO_ROOT/firmware/docs/review/core-review-1
SRC=$REPO_ROOT/firmware/modules/ring_core
HOSTSH=$REPO_ROOT/firmware/tests/core/host/run_host_tests.sh
OUT=$R/mut-results2.tsv
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
run m18b $GE 's/\(sw == opposite\(\(enum rc_switch\)g->dir\)\)/(sw == opposite((enum rc_switch)g->dir) || sw != (enum rc_switch)g->dir)/' "PAIR: any other switch also makes a centre press"
run m23b $SA 's/a == RC_ACT_MH \|\| a == RC_ACT_MT/a == RC_ACT_MH || a == RC_ACT_MT || a == RC_ACT_M3/' "Vibration off also drops M3"
run m36 $GE 's/return !g->rel_pending \|\| g->rel_t >= mark;/return 1;/' "marks after the release instant still fire during hold-off"
run m38 $CO 's/\t\t\t\tc->mic_rail = false;  \/\* a reboot[^\n]*\n//' "mic rail not cleared on power loss into BOOT"
run m39 $SA 's/(case 5:[^\n]*\n)\t\tP\(SD_OFF\);\n\t\tP\(CHARGE_ON\);\n/$1\t\tP(CHARGE_ON);\n\t\tP(SD_OFF);\n/' "row 5 swaps SD off and charge on"
run m45 $GE 's/g->down_t \+ RC_LONG_MS/g->down_t + RC_LONG_MS - 1/g' "long press at 999 ms"
run m52 $GE 's/g->kstate = g->held \? RC_K_IGNORE : RC_K_IDLE;\n\t\t}\n\t\tbreak;\n\tcase RC_K_IGNORE/g->kstate = RC_K_IDLE;\n\t\t}\n\t\tbreak;\n\tcase RC_K_IGNORE/' "after a sent direction other held switches are no longer ignored"
run m53 $CO 's/RC_ACT_SCREEN_UP, RC_ACT_NONE, RC_ACT_SCREEN_DOWN,/RC_ACT_SCREEN_DOWN, RC_ACT_NONE, RC_ACT_SCREEN_UP,/' "up and down swapped on the screen"
run m54 $ST 's/return !f->storage_full && f->batt < RC_BATT_B5;/return !f->storage_full;/' "row 35 guard drops the battery test"
echo done >> $OUT
