#!/bin/sh
# Deliberately broken copy: copies the ring core module, applies one small
# wrong change, runs the host tests on the copy, and expects "RESULT FAIL".
# Exit 0 when the tests caught the break (they printed RESULT FAIL), 1 otherwise.
#
# Usage: sh run_broken.sh [MUTATION]
#   long900   (default) the long press threshold 900 ms instead of 1000 ms (FW 2.1 line 220)
#   row12to   row 12 goes to STANDBY instead of RECORDING (line 144), in the generated table
#   gap60     the double-press minimum gap 50 ms instead of 60 ms (FW 2.1 line 222)
#   row27act  the RECORDING B5 row loses its "close" action (row 27 in F6, row 31 now)
#   m09 m15 m21 m23 m25 m29 m33  the review's mutations of the same name (core-review-1/mut-table.md)
#   sign_ignored sign_hook_twice sign_before_b5  step 6: the sign hook (rule R-SIGN, row 16)
# The copy lives in firmware/tests/core/broken/copy-<MUTATION>/ (overwritten each run, never deleted).
# Environment:
#   RING_BROKEN_OUT         folder that holds copy-<MUTATION>/ (default: this folder); broken_run.sh sets it
#   RING_BROKEN_APPLY_ONLY  1: make the copy and print the diff, run nothing (broken_run.sh then builds it with twister)
# The case each mutation must fail is named in named_cases.txt ("-" = an equivalent mutation that passes, as argued in
# docs/core-notes.md); the run counts as caught only when that case printed FAIL.

BROKEN_DIR=$(cd "$(dirname "$0")" && pwd)
FW_DIR=$(cd "$BROKEN_DIR/../../.." && pwd)
SRC=$FW_DIR/modules/ring_core
M=${1:-long900}
OUT_BASE=${RING_BROKEN_OUT:-$BROKEN_DIR}
COPY=$OUT_BASE/copy-$M/ring_core

echo "broken copy run $(date '+%Y-%m-%d %H:%M:%S %Z'), mutation $M"
mkdir -p "$COPY"
cp -R "$SRC/." "$COPY/"

case "$M" in
long900)
	FILE=$COPY/include/ring_core/rc_gesture.h
	sed -i.orig 's/^#define RC_LONG_MS            1000/#define RC_LONG_MS            900/' "$FILE" ;;
row12to)
	FILE=$COPY/src/state_table.inc
	sed -i.orig 's/^RC_ROW(12, 144, STANDBY, LONG_PRESS, OPEN_CLEAR_ABOVE_B5_ABOVE_SFULL_SIGN, RECORDING,/RC_ROW(12, 144, STANDBY, LONG_PRESS, OPEN_CLEAR_ABOVE_B5_ABOVE_SFULL_SIGN, STANDBY,/' "$FILE" ;;
gap60)
	FILE=$COPY/include/ring_core/rc_gesture.h
	sed -i.orig 's/^#define RC_DOUBLE_GAP_MIN_MS  60/#define RC_DOUBLE_GAP_MIN_MS  50/' "$FILE" ;;
row27act)
	# the B5 row of RECORDING ("battery reaches B5", close; M3): row 27 in F6, row 31 before step 6, row 32 now
	FILE=$COPY/src/state_actions.c
	perl -0pi.orig -e 's/(case 32: [^\n]*\n)\t\tP\(CLOSE\);\n/$1/' "$FILE" ;;
m09)
	# review mutation m09: direction window 41 ms (crashed the run in round 1, ruling C4)
	FILE=$COPY/src/gesture.c
	perl -0pi.orig -e 's/g->dir_t0 \+ RC_DIR_WINDOW_MS/g->dir_t0 + RC_DIR_WINDOW_MS + 1/' "$FILE" ;;
m15)
	# review mutation m15: B15 flag never cleared by VBUS
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/\t\tc->sm\.b15_warned = false;[^\n]*\n//' "$FILE" ;;
m21r1)
	# review 1 mutation m21 (equivalent, ruling C6): hold released exactly at the mark
	FILE=$COPY/src/gesture.c
	perl -0pi.orig -e 's/g->rel_t >= mark/g->rel_t > mark/' "$FILE" ;;
m21)
	# review 2 mutation m21 in its R9 form: asking for recovery (entering RECOVERY) clears the open flag
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/(\t\tif \(c->sm\.state == RC_ST_ERR_STORAGE_FAULT\) \{\n\t\t\tc->facts\.storage_fault = true;)/\t\tif (c->sm.state == RC_ST_RECOVERY) {\n\t\t\tc->facts.open_flag = false;\n\t\t}\n$1/' "$FILE" ;;
m31)
	# review 2 mutation m31: a repeated battery level fires its row again
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/if \(level > old\) \{/if (level >= old) {/' "$FILE" ;;
r15)
	# ruling R15 undone: no B2 check on entry into a state
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/if \(c->sm\.state != from && c->facts\.batt == RC_BATT_B2/if (0 \&\& c->sm.state != from \&\& c->facts.batt == RC_BATT_B2/' "$FILE" ;;
r16)
	# ruling R16 undone: no B2 check when VBUS is removed
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/if \(ev == RC_EV_VBUS_OUT && c->facts\.batt == RC_BATT_B2 &&/if (0 \&\& ev == RC_EV_VBUS_OUT \&\& c->facts.batt == RC_BATT_B2 \&\&/' "$FILE" ;;
r21)
	# review 3 mutation r21: the internal event STORAGE_FAULT_SET accepted by rc_core_event
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/ ev == RC_EV_STORAGE_FAULT_SET \|\|//' "$FILE" ;;
v02)
	# review 4 mutation v02: the VBUS-removal check also fires at B5
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/if \(ev == RC_EV_VBUS_OUT && c->facts\.batt == RC_BATT_B2 &&/if (ev == RC_EV_VBUS_OUT \&\& c->facts.batt >= RC_BATT_B5 \&\&/' "$FILE" ;;
v09)
	# review 4 mutation v09: the VBUS-removal check skips BOOT
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/if \(ev == RC_EV_VBUS_OUT && c->facts\.batt == RC_BATT_B2 &&/if (ev == RC_EV_VBUS_OUT \&\& from != RC_ST_BOOT \&\& c->facts.batt == RC_BATT_B2 \&\&/' "$FILE" ;;
m33)
	# review 2 mutation m33 (equivalent, ruling C9): the battery fact set after the row runs
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/\tc->facts\.batt = \(uint8_t\)level;\n(\tif \(c->sm\.state == RC_ST_BOOT\) \{\n\t\treturn;[^\n]*\n\t\}\n\tif \(level > old\) \{\n[^\n]*\n\t\tsm_event\(c, \(enum rc_event\)ev_of\[level\], t, out\);\n\t\})/\tif (c->sm.state == RC_ST_BOOT) {\n\t\tc->facts.batt = (uint8_t)level;\n\t\treturn;\n\t}\n\tif (level > old) {\n\t\tsm_event(c, (enum rc_event)ev_of[level], t, out);\n\t}\n\tc->facts.batt = (uint8_t)level;/' "$FILE" ;;
m35)
	# review 2 mutation m35: an invalid battery level is accepted
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/if \(\(unsigned\)level > RC_BATT_B2\) \{/if ((unsigned)level > 9) {/' "$FILE" ;;
m40)
	# review 2 mutation m40: the storage-full event does not set the fact
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/\tcase RC_EV_STORAGE_SFULL:\n\t\tc->facts\.storage_full = true;\n\t\tbreak;\n//' "$FILE" ;;
m41)
	# review 2 mutation m41 (equivalent, ruling C9): a hold whose long press fired is not cancelled
	FILE=$COPY/src/gesture.c
	perl -0pi.orig -e 's/if \(g->pressing\) \{\n\t\tg->cancelled = true;/if (g->pressing \&\& !g->long_fired) {\n\t\tg->cancelled = true;/' "$FILE" ;;
m23)
	# review mutation m23 (equivalent, ruling C6): Vibration off also drops MW in the row filter
	FILE=$COPY/src/state_actions.c
	perl -0pi.orig -e 's/a == RC_ACT_MH \|\| a == RC_ACT_MT\)/a == RC_ACT_MH || a == RC_ACT_MT || a == RC_ACT_MW)/' "$FILE" ;;
m25)
	# review mutation m25: S30 once never re-armed by a new recording
	FILE=$COPY/src/state_actions.c
	perl -0pi.orig -e 's/\t\tsm->s30_warned = false;\n//' "$FILE" ;;
m29)
	# review mutation m29: row 3 guard drops the battery test
	FILE=$COPY/src/state_table.c
	perl -0pi.orig -e 's/return !f->open_flag && !f->vbus && f->batt < RC_BATT_B5;/return !f->open_flag \&\& !f->vbus;/' "$FILE" ;;
r4b)
	# correction R4b undone: row 12 no longer needs the open flag clear
	FILE=$COPY/src/state_table.c
	perl -0pi.orig -e 's/return !f->open_flag && f->batt < RC_BATT_B5 && !f->storage_full && !f->sign_not_drawn;/return f->batt < RC_BATT_B5 \&\& !f->storage_full \&\& !f->sign_not_drawn;/' "$FILE" ;;
m33r1)
	# review 1 mutation m33: timers injectable through rc_core_event
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/ev == RC_EV_TIMER_5S \|\| ev == RC_EV_TIMER_60S \|\| //' "$FILE" ;;
sign_ignored)
	# step 6: the answer of the sign hook is ignored: row 12 is taken when the hook refuses
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/c->facts\.sign_not_drawn = \(c->sign_fn\(c->sign_ctx, t\) != 0\);/(void)c->sign_fn(c->sign_ctx, t);/' "$FILE" ;;
sign_hook_twice)
	# step 6: the hook is called twice for one long press
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/c->facts\.sign_not_drawn = \(c->sign_fn\(c->sign_ctx, t\) != 0\);/(void)c->sign_fn(c->sign_ctx, t);\n\t\tc->facts.sign_not_drawn = (c->sign_fn(c->sign_ctx, t) != 0);/' "$FILE" ;;
sign_before_b5)
	# step 6: the hook is called at B5 too (the battery test is missing from the condition of the call)
	FILE=$COPY/src/core.c
	perl -0pi.orig -e 's/(c->sign_fn != NULL && !c->facts\.open_flag &&\n)\t    c->facts\.batt < RC_BATT_B5 && !c->facts\.storage_full\) \{/$1\t    !c->facts.storage_full) {/' "$FILE" ;;
*)
	echo "unknown mutation $M"
	exit 2 ;;
esac

echo "change applied (diff of the copy against its original):"
diff "$FILE.orig" "$FILE"
if [ $? -eq 0 ]; then
	echo "the change did not apply"
	exit 2
fi

if [ "${RING_BROKEN_APPLY_ONLY:-0}" = 1 ]; then
	echo "copy made at $COPY (apply only)"
	exit 0
fi

NAMED=$(awk -v m="$M" '$1 == m { print $2 }' "$BROKEN_DIR/named_cases.txt")
if [ -z "$NAMED" ]; then
	echo "no named case for $M in named_cases.txt"
	exit 2
fi
LOG=$OUT_BASE/copy-$M/host-run.log
HOST_BUILD_DIR=$OUT_BASE/copy-$M/build sh "$FW_DIR/tests/core/host/run_host_tests.sh" "$COPY" > "$LOG" 2>&1
grep -E '^(FAIL|RESULT|suites=|generated table)|assert failed' "$LOG"
if [ "$NAMED" = "-" ]; then
	if grep -q '^RESULT PASS' "$LOG"; then
		echo "EQUIVALENT MUTATION: the tests pass on $M, as documented (no case can tell it from the original)"
		exit 0
	fi
	echo "EQUIVALENT MUTATION FAILED: $M was documented as equivalent but a case failed"
	exit 1
fi
if grep -q "^FAIL $NAMED\$" "$LOG"; then
	echo "BROKEN COPY CAUGHT: the tests fail on mutation $M, named case $NAMED failed"
	exit 0
fi
echo "BROKEN COPY NOT CAUGHT BY ITS NAMED CASE: $NAMED did not fail on mutation $M"
exit 1
