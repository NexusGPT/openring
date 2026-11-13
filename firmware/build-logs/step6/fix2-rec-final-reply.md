Fix round 2 is done: R2-01 to R2-08 and R2-10 are fixed, and the R2-11 comment is in. Each of the eight new broken copies fails its named case on native_sim and on the simulated chip. The unit run `tools/unit_run.sh tests/recorder` (`build-logs/step6/fix2-rec-u1.log`, remote exit 0) ends, quoted from l.1201: `UNIT PASS tests/recorder`. It ran 59 of 59 cases on each board (l.22, l.44), and l.1199 `RESULT PASS` covers 26 copies.

| Finding | Change | Copy, lines native_sim / chip |
|---|---|---|
| R2-01 | The retry job is now an empty core step (`rglue_event(RC_EV_COUNT)`). The decision and the unmount happen under the glue's lock, and the counters are written only inside steps. | `retry_outside_lock`, l.871 / 887 |
| R2-02 | The episode's errno is kept and cleared at its end. When the card is wanted again, the end record carries -EBUSY. | `end_errno_stale`, l.920 / 941 |
| R2-03 | One wait per step for the command and one for the unmount; the rails do not try again in the same step. | `rails_tries_again`, l.970 / 986 |
| R2-04 | In ship mode, if the unmount fails: 0x0290 is logged (try 1), USB is closed, the unmount is tried again and logged (try 2), and ship mode goes on. | `ship_storage_before_usb`, l.1014 / 1027 |
| R2-05 | The screen wait is at most `RREC_SHIP_SCREEN_WAIT_MS` 1000u (an addition to `rrec_spec.h`), through a work queue of the join's own. | `screen_wait_forever`, l.1052 / 1064 |
| R2-06 | A latched VBUS job is queued with the event matching the VBUS level read at that moment. | `latched_vbus_stale`, l.1097 / 1117 |
| R2-07 | The T-SIGN case now bounds each recording from above: under 1,150 ms. | `tsign_2s`, l.1141 / 1152 |
| R2-08 | The FW l.179 case now holds the store longer than one 5 s wait. | `abort_no_wait`, l.1181 / 1197; it fails that case alone |
| R2-10 | The citation now reads rrec.c:509 at commit c26ae988. | - |

**Worst-case time one step holds the glue's lock:** about 10 s, from the 5,000 ms command wait plus the 5,000 ms unmount wait, plus the unmount's own card time. That last part has no number that bounds it. Before this round it was about 15 s plus that card time. In run s2 the row 46 step held the lock 10,000 ms.

**First short run failed:** in `fix2-rec-s1.log` two of my new cases failed.
- `test_retry_never_takes_the_card` expected an errno its own scenario cannot give, because a regular step unmounts the card successfully before the recording starts. The errno check moved to a new case.
- `test_one_wait_each_per_step` measured the glue's lock from another thread, and a retry step took the lock first. It now times the step itself.

The next short run, `fix2-rec-s2.log`, passed 59 of 59 on each board.

**Where my cases differ from your wording:**
- The store holder in the R2-04 case is a store call from a test thread, not a USB command. With SHIP_ENTER running, the transfer part answers BUSY to any second command.
- The VBUS part of round 1's latch case moved into the R2-06 case. The old case posted VBUS out while VBUS was present, which the new rule now answers with VBUS in.

**Not run again:** tests/bsim/control, because rdev and the ship path's radio part are unchanged.

**What I could not do:**
- The unmount's card time in the worst-case lock time has no number that bounds it.
- If the screens thread stays stuck, its work item stays pending, and every later ship mode waits its 1,000 ms again.

**Files:** 11 changed (`fix2-rec-diffs.txt`), 0 lines removed from `rrec_spec.h`. The checklist has 15 of 15 ticked.

questions_for_owner: none.

Files (in `firmware/`):
- `docs/recorder-notes.md`, section "Fix round 2"
- `build-logs/step6/fix2-rec-CHECKLIST.md`
- `build-logs/step6/fix2-rec-audit.txt`

RESULT: done, commit none (no git: the lead commits), `tools/unit_run.sh tests/recorder` exit 0
