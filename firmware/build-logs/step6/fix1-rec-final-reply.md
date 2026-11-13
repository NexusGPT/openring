The 0x0290 ruling is in: the join now writes the record at the first failed try of a step and once more when its tries end, never once per try. The recorder's run on the final files ends `UNIT PASS tests/recorder`.

**What changed** (`modules/ring_recorder/src/rrec.c`):
- At the first failed try: errno -EBUSY, try 1.
- When the tries end: errno 0 if the unmount then succeeded, else the last errno; try is the number of tries made.
- The comment of the code in `rrec_spec.h` now says the same (my own added lines; 0 header lines removed, `fix1-rec-headers-check.txt`).
- The case `recorder_unmount.test_failed_unmount_retried_and_reported` now asserts exactly 2 records: the first with errno -EBUSY, try 1, state TRANSFER; the second with errno 0 and 2 or more tries.

**What I ran:**
- Short run `fix1-rec-s5.log`, remote exit 0: 53 of 53 cases on each board; the 2 records printed are try 1, then errno 0 with try 6.
- Unit run `tools/unit_run.sh tests/recorder`, `fix1-rec-u3.log`, remote exit 0:
  - 53 of 53 cases on each board (l.22, l.44).
  - Copy `unmount_result_dropped` still fails its named case on both boards (l.665, 681).
  - l.802 `RESULT PASS` (all 18 copies).
  - l.806 `unmount: record 1: errno -16, state TRANSFER, try 1` and l.807 `unmount: record 2: errno 0, state CHARGING, try 6`.
  - Last result line, quoted: `UNIT PASS tests/recorder` (l.804).
- I did not re-run the full unit run: the change touches only `rrec.c`, the recorder case and a comment in `rrec_spec.h`. The full run u2, `fix1-rec-u2.log`, ended `UNIT PASS tests/recorder tests/store tests/xfer tests/audio tests/motor tests/devices tests/factory tests/screens` (l.7535) on the files from before this ruling.

**Notes and checks:**
- The notes record the ruling, runs s5 and u3, and the earlier one-record-per-try result of u2: 11 tries, l.7579.
- The RESULT line is rewritten.
- The checklist has 36 of 36 ticked.
- 36 files are changed or added (`fix1-rec-diffs.txt`).

questions_for_owner: none.

Files (in `firmware/`):
- `docs/recorder-notes.md`, section "Fix round 1"
- `build-logs/step6/fix1-rec-CHECKLIST.md`
- `build-logs/step6/fix1-rec-audit.txt`

RESULT: done, commit none (no git: the lead commits), `tools/unit_run.sh tests/recorder` exit 0
