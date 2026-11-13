# U7 sys checklist (started 2026-11-13 05:52 CET, `date`)

Closed as `[x] ... evidence: <saved file>` or `[-] ... not done: <measured limit>`.

## Files and rules
- [ ] 1. modules/ring_sys/src/rsy_logic.c (+ rsy_logic.h): pure part, no kernel call (stdint, stdbool, string, crc32 library only)
- [ ] 2. modules/ring_sys/src/rsy.c: thin part, hardware only through rhw.h (rhw_image, rhw_persist, rhw_retained, rhw_wdt, rhw_clock)
- [ ] 3. modules/ring_sys/src/rsy_hw_real.c: kit build only, not proven (swap, signature, rollback, real watchdog reset stay "not provable without hardware")
- [ ] 4. CMakeLists.txt, Kconfig, zephyr/module.yml of ring_sys (include/ not touched)
- [ ] 5. every number from rrec_spec.h (slot size, 30 s, 8 s, 1 s, 2 s, 30 percent); test expected values typed from design/firmware.md with the line
- [ ] 6. no chip pin by number; no kit or Zephyr text printed into a file or log; no secret; no server address in any file I write
- [ ] 7. no change outside Owns (frozen headers, ring_rhw, ring_time, other modules, app, tools, design untouched)

## Suites (each on native_sim and nrf54lm20bsim/nrf54lm20a/cpuapp)
- [ ] 8. sys_update (cases: test_size_limit, test_data_end_limit, test_writes_only_slot1, test_layout_sums_to_2036_kb, test_sequence, test_end_bad_crc_fw_error, test_self_test_pass_confirms, test_self_test_timeout_reboots, test_self_test_no_mic, test_allowed_rule)
- [ ] 9. sys_time (test_saved_on_ship_and_off, test_guess_is_not_set)
- [ ] 10. sys_persist (test_factory_flag_survives_reboot)
- [ ] 11. sys_crash (test_block_format, test_boot_copies_valid_block_once)
- [ ] 12. sys_wdt (test_feed_only_with_progress)
- [ ] 13. each outside answer the code reads (image write, erase, read, persist save, retained write, wdt start) has a test for empty / fail / normal where the simulation can give it; the rest listed untested

## Broken copies (each fails its named case on both targets; other failing cases listed per copy)
- [ ] 14. size_999425_ok -> sys_update.test_size_limit
- [ ] 15. end_off_by_one -> sys_update.test_data_end_limit
- [ ] 16. writes_slot0 -> sys_update.test_writes_only_slot1
- [ ] 17. selftest_31s -> sys_update.test_self_test_timeout_reboots
- [ ] 18. allowed_at_30 -> sys_update.test_allowed_rule
- [ ] 19. feed_without_progress -> sys_wdt.test_feed_only_with_progress
- [ ] 20. crash_copied_twice -> sys_crash.test_boot_copies_valid_block_once
- [ ] 21. guess_marked_set -> sys_time.test_guess_is_not_set
- [ ] 22. broken_edit.py: each edit matches exactly once (local check saved)
- [ ] 23. red first: each broken copy run before the unit passes (the broken run itself is the red evidence)

## Plan rows to map in sys-notes.md (test case and log line, or NP with reason)
- [ ] 24. C23
- [ ] 25. T4
- [ ] 26. T5
- [ ] 27. T6
- [ ] 28. T8
- [ ] 29. T9
- [ ] 30. T10
- [ ] 31. T11
- [ ] 32. T28
- [ ] 33. T29

## Kit facts
- [ ] 34. K9 answered (count / name listing, no kit lines)
- [ ] 35. K10 answered
- [ ] 36. K11 answered (compile test of the handler signature)

## Rulings applied
- [ ] 37. D12 NOT_ALLOWED (11) for update not allowed
- [ ] 38. D18 saved time is a guess, written once into the event log (by the join), used nowhere else; clock stays not set
- [ ] 39. watchdog fed when both threads reported in last 2 s, or when no recording runs
- [ ] 40. 30 percent rule: allowed only ABOVE 30.0 percent (soc_x10 > 300) or VBUS

## Runs and delivery
- [ ] 41. local check: each broken-copy edit matches once
- [ ] 42. short run of the suites alone (no broken copies), green, saved
- [ ] 43. full unit run `bash tools/unit_run.sh tests/sys` started in background with exit file; last line `UNIT PASS tests/sys`
- [ ] 44. sys-notes.md maps rows, answers K9 K10 K11, lists questions_for_owner, last line `RESULT: <done|blocked>, ...`
- [ ] 45. final audit script over my final reply and notes; output saved
- [ ] 46. leftovers outside my output folder removed or listed (server copy folder, processes)
