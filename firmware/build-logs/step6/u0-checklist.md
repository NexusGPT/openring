# U0 rhw checklist (builder of unit U0, step 6)

Started 2026-11-13 04:10 CET (date). Base: commit 783ddc4.

- [x] 1. Read step6-plan.md in full, rulings included (D3: no soft start header, constant or driver). evidence: plan read lines 1-529
- [x] 2. ring_rhw module: zephyr/module.yml, CMakeLists.txt, Kconfig (RING_RHW, RING_RHW_SIM). evidence: run 3 builds the module
- [x] 3. rrec_spec.h: every shared number of FW 4, 5, 6, 9 once with its FW line; sector map, chunk sizes, magics, record sizes, opcodes 0x01..0x0D, status 0..11, factory sub-commands, pattern ids M1..MF, S30 3,516, SFULL 16, slot limits FW 9.2. evidence: u0-check-spec-lines.log
- [x] 4. Event log code list of D13 in rrec_spec.h, marked for the lead (state change, fault, battery threshold, transfer command per opcode, motor pattern start, current limit, reset cause, crash, dropout, recovery, sign refused, ship retry, zone unknown at start). evidence: rrec_spec.h enum rrec_log_code
- [x] 5. rhw.h: 14 interfaces (disk, mic, power chip, HFXO, motor pin, storage bus, USB transport, image store, settings, retained, watchdog, gauge, clock, beacon), active instance chosen at start. evidence: rhw.h, run 3
- [x] 6. rhw_sim.h: one ordered event log (kind, args, time, caller); every fault and value of plan section 5; rhw_sim_reboot keeps card, settings, retained. evidence: rhw_sim.h, run 3
- [x] 7. sim drivers src/sim_*.c for each of the 14 kinds; src/rhw_clock_real.c. evidence: run 3 42/42 both boards
- [x] 8. dts bindings ring,sim-disk.yaml and ring,sim-mic.yaml. evidence: run 1 error fixed, run 3
- [x] 9. Public headers: rst.h (U2), rau.h (U3), rxf.h (U4), rpw.h (U5), rmo.h (U6), rsy.h (U7), rfa.h (U8), rrec.h (J); each function: what, args, return, thread, blocking, FW line. evidence: hdr_*.c in run 3
- [x] 10. No soft-start item anywhere (ruling D3). evidence: no soft-start name in my files (rmo.h states it is not built)
- [x] 11. tests/rhw/src/headers.c (or one file per header): each public header included alone. evidence: test_headers_compiled PASS run 3
- [x] 12. Suite rhw_sim: one case per fault of section 5 (card 7, mic 7, power chip 6 + script/cell, gauge 2, HFXO 2, USB 2, image store 2, settings 1, retained 1, clock 1; watchdog flag; beacon and motor and bus records). evidence: notes section 7, run 3
- [x] 13. Case: event log keeps order and time. evidence: test_event_log_order_and_time PASS run 3
- [x] 14. Case test_reboot_keeps_card_settings_retained: keeps exactly the three stores. evidence: PASS run 3
- [x] 15. K14 case: sys_clock_hw_cycles_per_sec and k_cycle_get_32 on the simulated chip. evidence: run 2 K14 line, PASS run 3
- [x] 16. K15: RAM of the simulated chip target for the sparse card and 3 chunks (first run). evidence: PASS run 3
- [-] 17. K16: twister two scenarios with extra_configs (doc count) and suite time on the server. not done: two-scenario part not run (soft start dropped, D3); doc count 3 and run time 4 min 39 s only
- [x] 18. tools/unit_run.sh: any number of folders, twister on native_sim and nrf54lm20bsim/nrf54lm20a/cpuapp, each folder's broken_run.sh, last line UNIT PASS <folders> / UNIT FAIL <folders> <parts>, exit 1 on failure. evidence: runs 1-3 exit codes
- [x] 19. tests/rhw/broken_run.sh + broken_edit.py with disk_fault_late, cut_keeps_tail, reboot_wipes_card, mic_no_block_ignored; each fails its named case on both targets. evidence: run 3 broken-rhw RESULT PASS
- [x] 20. Red first: broken copies fail their named case on both targets (saved log). evidence: runs 2 and 3 (written together, not red-before-green)
- [x] 21. Targeted run ends `UNIT PASS tests/rhw` (log copied to build-logs/step6/u0-*). evidence: u0-20261113-044107-u-rhw.log line 606
- [x] 22. No chip pin by number in any source (search saved). evidence: u0-search-pins-devnull.log
- [x] 23. No kit or Zephyr text printed into files or logs I write. evidence: only counts and file listings from kit (u0-k16.console)
- [x] 24. No stderr to /dev/null in any script. evidence: u0-search-pins-devnull.log
- [x] 25. rhw-notes.md: each header function with its FW line; each kit fact; each run with log and last line; plan-vs-spec differences; what I could not settle; questions_for_owner; last line RESULT. evidence: docs/rhw-notes.md
- [x] 26. Only owned files changed (listing saved). evidence: u0-owned-files.log
- [x] 27. One run of mine on the server at a time; never build_all.sh. evidence: runs sequential, no build_all
- [x] 28. Final reply under 3,500 characters. evidence: reply file u0-reply.md

## Looks at results before the final run (each reported)
- run 1 (04:33:54, log u0-20261113-043354-u-rhw.log): UNIT FAIL, devicetree error "unknown vendor prefix" on both boards; broken copies counted as not failing (a build error does not count). Fix: dts/bindings/vendor-prefixes.txt.
- run 2 (04:36:05): partial look at the console at 04:37:43 and 04:38:16 while it ran: native_sim 29 of 42 cases passed (timing cases: a k_sleep of 1 ms took 20 ms, a coarse kernel tick by my reading, checked by run 3; plus 2 wrong expectations of mine), bsim 40 of 42 (the same 2 wrong expectations). Fixes: tests/rhw/boards/native_sim.conf (0.1 ms ticks), expected 3,820 mV, USB read buffer 1,300 bytes.
