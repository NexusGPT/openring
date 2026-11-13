# U8 factory: checklist (started 2026-11-13 06:47 CET by `date`; closed items name their saved evidence)

Evidence folder: `firmware/build-logs/step6/` (files named `u8-*`). "F/" = `firmware/`.

- [x] 1. Brief has Owns, Must not touch, Writes to, Done when, and the quality reference (pattern of tests/sys and tests/motor).
- [x] 2. Contract read in full first: plan 1.3, row C20, row X17, 2.6 (T1 to T29), section 3 rules and U8, section 5, K13, D6, D7, all rulings; rhw-notes 2 and 3; rfa.h, rrec_spec.h, rhw.h, rhw_sim.h; the five finished units' headers and notes.
- [x] 3. Suite `factory_cmd` passes on native_sim.
- [x] 4. Suite `factory_cmd` passes on nrf54lm20bsim/nrf54lm20a/cpuapp.
- [x] 5. Suite `factory_mic` on both targets.
- [x] 6. Suite `factory_input` on both targets.
- [x] 7. Suite `factory_motor` on both targets.
- [x] 8. Suite `factory_sign` on both targets.
- [x] 9. Suite `factory_store` on both targets.
- [x] 10. Suite `factory_radio` on both targets.
- [x] 11. Suite `factory_charge` on both targets.
- [x] 12. Suite `factory_xtal` on both targets.
- [x] 13. Suite `factory_ship` on both targets.
- [x] 14. Suite `factory_screen` on both targets (stand-in case in scenario ring_factory.sim, real screens part in scenario ring_factory.screen).
- [x] 15. Two-device test `tests/bsim/factory/run.sh` passes.
- [x] 16. Its `--broken` run fails each of its two copies on the named scanner check (and ends RESULT PASS = every copy caught).
- [x] 17. Broken copy `flag_ignored` fails `factory_cmd.test_flag_rules` on both targets.
- [x] 18. Broken copy `x11_accepted` fails `factory_cmd.test_0x11_bad_arg` on both targets.
- [x] 19. Broken copy `run_999` fails `factory_mic.test_rms_and_runs` on both targets.
- [x] 20. Broken copy `mic_without_sign` fails `factory_mic.test_no_screen_no_mic` on both targets.
- [x] 21. Broken copy `centre_records` fails `factory_input.test_centre_reported_never_records` on both targets.
- [x] 22. Broken copy `vbat_read_at_0` fails `factory_motor.test_reads_and_timing` on both targets.
- [x] 23. Broken copy `store_lba_4097` fails `factory_store.test_area_write_read` on both targets.
- [x] 24. Broken copy `type2_left` fails `factory_store.test_test_recordings_deleted` on both targets.
- [x] 25. Broken copy `beacon_connectable` fails `factory_ship.test_beacon_name` on both targets.
- [x] 26. Broken copy `beacon_after_ship` fails `factory_ship.test_beacon_window` on both targets.
- [x] 27. For each broken copy the other cases that fail with it are listed (notes section 4).
- [x] 28. Each broken-copy edit matches exactly once (local check saved).
- [x] 29. Runner `broken_run.sh` and `broken_edit.py` in tests/factory (pattern of tests/sys and tests/motor).
- [x] 30. Targeted run `tools/unit_run.sh tests/factory` ends `UNIT PASS tests/factory` (exit 0).
- [x] 31. Row C20 mapped to its case and log line.
- [x] 32. Row T11 mapped.
- [x] 33. Row T12 mapped.
- [x] 34. Row T13 mapped.
- [x] 35. Row T14 mapped.
- [x] 36. Row T15 mapped.
- [x] 37. Row T16 mapped.
- [x] 38. Row T17 mapped.
- [x] 39. Row T18 mapped.
- [x] 40. Row T19 mapped.
- [x] 41. Row T20 mapped.
- [x] 42. Row T21 mapped.
- [x] 43. Row T22 mapped.
- [x] 44. Row T23 mapped.
- [x] 45. Row X17 (factory half) mapped.
- [x] 46. K13 answered with file names and counts only (no kit line printed).
- [x] 47. Notes list what the join must call.
- [x] 48. Standing rule: pure part makes no kernel call (search saved); thin part reaches hardware only through rhw.h and other units' headers (search saved); the real beacon file compiles on the simulated chip with the simulated drivers off (bsim ring_app) and is not proven on the kit.
- [x] 49. Standing rule: no factory command starts or stops a recording; test recordings (type 2) go through the normal path and are deleted by T-STORE (cases named in notes).
- [x] 50. Standing rule: every number from rrec_spec.h; expected values typed from design/firmware.md with the line; numbers not in rrec_spec.h are listed.
- [x] 51. Standing rule: no chip pin by number, no other company name in a string, no kit or Zephyr text printed, no secret or server address in a file (searches saved).
- [x] 52. D7 call `rscr_factory_frame` used for factory_screen (present in the tree; no report needed).
- [x] 53. Battery sampling "recording states" include FACTORY_TEST during a test recording: noted for the join (power-notes reading 1).
- [x] 54. Files written only inside Owns; the brief's frozen headers untouched.
- [x] 55. Every look at results before the final one is reported (notes run list).
- [x] 56. Final audit of the reply and notes run; output saved.
- [x] 57. Notes end with `questions_for_owner` and the RESULT line.
- [x] 58. Clean up: nothing made outside the output folder and Owns except the server copy `/root/ring-os/src-u-factory` and run folders under `/ws/out` (listed in notes).

All items closed. Evidence: suites and per-case lines `u8-cases.console` / `u8-case-lines.txt`; unit run `u8-full1.console` (line 1464 `UNIT PASS tests/factory`); broken copies `u8-full1.console` lines 129 to 1461; two-device `u8-bsim-final.console`, `u8-bsim-broken-final.console`; K13 `u8-k13.console`; searches `u8-searches.log`; audit `u8-audit.log` (96 claims, 0 mismatches); edit checks `u8-editcheck2.log`.
Item 14: the real-screens case runs only in scenario ring_factory.screen. Item 48: the real beacon file is not compiled for the development kit (marked not done: no kit build made; limit: none measured, out of scope of this run).
