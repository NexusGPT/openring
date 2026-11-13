U0 `rhw` is done: the final targeted run ends `UNIT PASS tests/rhw`, exit 0. Full notes: firmware/docs/rhw-notes.md.

**Runs** (`RING_REMOTE_SRC=/root/ring-os/src-u-rhw sh firmware/tools/remote.sh u-rhw "bash tools/unit_run.sh tests/rhw"`; logs copied to firmware/build-logs/step6/):
- Run 1, u0-20261113-043354-u-rhw.log, exit 1. Cause: the devicetree had no vendor prefix `ring`. Fixed by adding vendor-prefixes.txt.
- Run 2, u0-20261113-043605-u-rhw.log, exit 1. Cause: native_sim's coarse tick broke the timing cases, and two expected values I had typed were wrong. Fixed with 0.1 ms ticks on native_sim and corrected values.
- Run 3 (final), u0-20261113-044107-u-rhw.log, exit 0, last result line `UNIT PASS tests/rhw`.

**Tests:**
- Suite `rhw_sim`: 42 of 42 cases pass on native_sim and 42 of 42 on nrf54lm20bsim/nrf54lm20a/cpuapp. It has one case per fault of plan section 5, one for the event log's order and time, and `test_reboot_keeps_card_settings_retained`.
- Broken copies: each of the 4 fails its own named case on both boards, and only that case (`failed cases listed: 1`):
  - `disk_fault_late` fails `test_disk_write_fault_at_n`
  - `cut_keeps_tail` fails `test_disk_cut_after_sector`
  - `reboot_wipes_card` fails `test_reboot_keeps_card_settings_retained`
  - `mic_no_block_ignored` fails `test_mic_stop_delivering`
- Red first did not hold: the suite and its broken copies were written together and first ran together in run 1.
- Runner: `tools/unit_run.sh` takes any number of folders. It ends with `UNIT PASS <folders>` or `UNIT FAIL <folders> <parts>` and exits 1 on failure.
- Headers: each of the 11 public headers compiles alone in its own file `tests/rhw/src/hdr_*.c`, checked by `test_headers_compiled`.
- I did not run the full run.

**Kit facts:**
- K14 holds on the simulated chip: `sys_clock_hw_cycles_per_sec 1000000`, and `k_cycle_get_32` advanced 100100 cycles in 100 ms.
- K15 holds: the full disk pool of 2097152 bytes and 3 chunks fit on that target.
- K16 is only partly settled. Twister's documentation names `extra_configs` (3 hits); the two-scenario case was never run because the soft start was dropped (ruling D3). The targeted run took 4 min 39 s.

**For the lead:**
1. FACTORY_EXIT has no sub-command number in the specification; I proposed 0x02 in rrec_spec.h.
2. The event log code list (D13), `enum rrec_log_code` in rrec_spec.h, is ready to copy into the specification's section 9.4.
3. Two readings are open: which states "recording states" means for battery sampling (FW l.928), and whether the watchdog may be fed when no recording runs (FW l.1065).
4. Close order: FW l.125 writes the CLOSE record and superblock before stopping the PDM, while l.463 stops the PDM first. rau.h splits the stop into `rau_cut` and `rau_halt` so the join can keep the l.125 order.
5. READ_RANGE needs the CRC of every chunk before the first byte is sent; noted in rxf.h.
6. I dropped U5's "set a rail" so that each rail has one path.
7. CHARGE_CURRENT stays in ring_power (rule P2), not in rrec_spec.h.

Function map: 287 functions; the 102 without a FW line serve plan rules (27 getters and register calls, 75 test controls in rhw_sim.h). Spec check: 196 of 223 numbers are literally on their cited line; the other 27 are unit or size conversions I read.

questions_for_owner: none

RESULT: done, commit none (the lead commits), unit_run.sh tests/rhw exit 0
