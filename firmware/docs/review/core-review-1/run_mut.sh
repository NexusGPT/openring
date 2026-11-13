#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# Mutation runner: copies the module into the review folder, applies one perl edit, runs the host tests on the copy.
# Writes only under the review folder. Usage: sh run_mut.sh
R=$REPO_ROOT/firmware/docs/review/core-review-1
SRC=$REPO_ROOT/firmware/modules/ring_core
HOSTSH=$REPO_ROOT/firmware/tests/core/host/run_host_tests.sh
OUT=$R/mut-results.tsv
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
run m01 $SA 's/(case 22:[^\n]*\n\t\tP\(HIGHLIGHT\);\n)\t\tP\(MH\);\n/$1/' "row 22 drops MH"
run m02 $SA 's/(case 21:[^\n]*\n)\t\tP\(CLOSE\);\n\t\tP\(M2\);\n/$1\t\tP(M2);\n\t\tP(CLOSE);\n/' "row 21 swaps close and M2"
run m03 $SA 's/(case 25:[^\n]*\n\t\tP\(CLOSE\);\n\t\tP\(M2\);\n)\t\tP\(CHARGE_ON\);\n/$1/' "row 25 drops charge on"
run m04 $SA 's/(case 31:[^\n]*\n\t\tP\(STOP_PDM\);\n\t\tP\(CLOCKS_LOW\);\n)\t\tP\(MIC_OFF\);\n/$1/' "row 31 drops VDD_MIC off"
run m05 $GE 's/dur > RC_SHORT_MAX_MS/dur >= RC_SHORT_MAX_MS/' "short ceiling 449 (off by one)"
run m06 $GE 's/>= RC_DOUBLE_GAP_MIN_MS/> RC_DOUBLE_GAP_MIN_MS/' "double gap minimum 61"
run m07 $GE 's/g->down_t \+ RC_WARN_MS/g->down_t + RC_WARN_MS + 1/g' "warning pulse at 501 ms"
run m08 $GE 's/g->rel_t \+ RC_RELEASE_HOLDOFF_MS/g->rel_t + RC_RELEASE_HOLDOFF_MS - 1/' "release hold-off 29 ms"
run m09 $GE 's/g->dir_t0 \+ RC_DIR_WINDOW_MS/g->dir_t0 + RC_DIR_WINDOW_MS + 1/' "direction window 41 ms"
run m10 $GE 's/g->next_repeat \+= RC_REPEAT_PERIOD_MS/g->next_repeat += RC_REPEAT_PERIOD_MS + 1/' "repeat period 151 ms"
run m11 $GE 's/g->next_repeat = g->dir_t0 \+ RC_REPEAT_DELAY_MS/g->next_repeat = g->dir_t0 + RC_REPEAT_DELAY_MS + 1/' "first repeat at 501 ms"
run m12 $CO 's/ev == RC_EV_LONG_PRESS \|\| //' "long press injectable through rc_core_event"
run m13 $CO 's/if \(st == RC_ST_STANDBY \|\| st == RC_ST_RECORDING\) \{\n\t\t\t\trc_actions_push\(out, RC_ACT_MW\)/if (st == RC_ST_STANDBY) {\n\t\t\t\trc_actions_push(out, RC_ACT_MW)/' "MW only in STANDBY"
run m14 $CO 's/out->highlight_ms = e->t_down;/out->highlight_ms = e->t;/' "highlight time = window close, not CENTRE_DOWN"
run m15 $CO 's/\t\tc->sm.b15_warned = false;[^\n]*\n//' "B15 flag never cleared by VBUS"
run m16 $CO 's/if \(!c->facts.screen_on\) \{/if (0) {/' "screen lock removed"
run m17 $ST 's/return f->batt >= RC_BATT_B5;/return f->batt > RC_BATT_B5;/' "guard AT_B5 excludes B5"
run m18 $GE 's/\(sw == opposite\(\(enum rc_switch\)g->dir\)\)/(sw != (enum rc_switch)g->dir)/' "PAIR: any other switch makes a centre press"
run m19 $GE 's/\t\t\tg->rel_pending = false;       \/\* roll or bounce: the key stays down \*\/\n//' "roll or bounce does not hold the key down"
run m20 $GE 's/g->second = \(t - g->short_up_t\) >= RC_DOUBLE_GAP_MIN_MS;/g->second = false;/' "double press never recognised"
run m21 $GE 's/return !g->rel_pending \|\| g->rel_t >= mark;/return !g->rel_pending || g->rel_t > mark;/' "hold released at exactly the mark is not long"
run m22 $CO 's/now >= when/now > when/' "state timers fire one ms late"
run m23 $SA 's/a == RC_ACT_MH \|\| a == RC_ACT_MT/a == RC_ACT_MH || a == RC_ACT_MT || a == RC_ACT_MW/' "Vibration off also drops MW"
run m24 $GE 's/RC_DOUBLE_WINDOW_MS \+ 1/RC_DOUBLE_WINDOW_MS/' "short press fires at 400 not 401"
run m25 $SA 's/\t\tsm->s30_warned = false;\n//' "S30 once never re-armed by a new recording"
run m26 $SA 's/if \(f->open_flag\) \{\n\t\t\tP\(RUN_RECOVERY\);\n\t\t\}/P(RUN_RECOVERY);/' "row 53 always runs recovery"
run m27 $SA 's/(case 17:[^\n]*\n\t\tif \(!sm->b15_warned\) \{\n\t\t\tP\(M3\);\n\t\t\tsm->b15_warned = true;\n\t\t\}\n)\t\tP\(SCR_STATUS_5S\);\n/$1/' "row 17 drops status screen"
run m28 $GE 's/dur < RC_SHORT_MIN_MS/dur <= RC_SHORT_MIN_MS/' "graze limit 40 inclusive"
run m29 $ST 's/return !f->open_flag && !f->vbus && f->batt < RC_BATT_B5;/return !f->open_flag \&\& !f->vbus;/' "row 3 guard drops the battery test"
run m30 $SA 's/(case 12:[^\n]*\n\t\tP\(OPEN\);\n)\t\tP\(M1\);\n/$1/' "row 12 drops M1"
run m31 $SA 's/(case 15:[^\n]*\n\t\tP\(SAVE_SETTINGS_TIME\);\n)\t\tP\(M2\);\n(\t\tP\(SHIP_MODE\);)/$1$2/' "row 15 drops M2"
run m32 $GE 's/g->long_fired = true;\n\t\t\tg->warned = true;/g->warned = true;/' "long press may fire again (no once-per-press)"
run m33 $CO 's/ev == RC_EV_TIMER_5S \|\| ev == RC_EV_TIMER_60S \|\| //' "timers injectable through rc_core_event"
run m34 $SA 's/(case 38:[^\n]*\n\t\tP\(LOG_CHARGE_ERROR\);\n)\t\tP\(CHARGE_OFF\);\n/$1/' "row 38 drops charge off"
run m35 $SA 's/(case 29:[^\n]*\n\t\tif \(!sm->s30_warned\) \{\n\t\t\tP\(M3\);\n\t\t\tsm->s30_warned = true;\n\t\t\}\n)\t\tP\(SCR_MSG_30MIN_3S\);\n/$1/' "row 29 drops the 30 min message"
echo done >> $OUT
