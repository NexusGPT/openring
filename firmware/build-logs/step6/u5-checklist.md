# U5 power: checklist (opened 2026-11-13 05:00 CET by the builder)

Rows of the plan that name U5, then the brief's own requirements. `[x] ... evidence: <file>`, `[-] ... not done: <measured limit>`.

- [ ] 1. C2 `power_levels.test_soc_edges` (16, 15, 6, 5, 3, 2 %), `test_voltage_edges` (3.451, 3.450, 3.301, 3.300 V), `test_mean_of_ten_in_recording`
- [ ] 2. C6 `power_charger.test_charge_on_twice_writes_once`, `test_charge_off`
- [ ] 3. C22 `power_charger.test_on_at_every_vbus` (every state, BOOT and RECOVERY included)
- [ ] 4. C39 (U5 part): values for SCR_CHARGING come from `rpw_values()` (`power_report`)
- [ ] 5. P2 `CHARGE_CURRENT` 15,000 in one place; five build assertions; broken copies `cc_unset`, `cc_17601`, `cc_3999`, `cc_100500`, `cc_15250` each fail the BUILD with their own message
- [ ] 6. P3 `power_charger.test_disable_write_enable_order`
- [ ] 7. P8 `power_gauge.test_motor_charge_added` (one MF 51.50 mA.s in 1 s adds 51.5 mA)
- [ ] 8. P9 `power_sample.test_period_per_state`, `test_ilim_read_with_every_sample`
- [ ] 9. P11 `power_levels.test_report_on_change_both_ways`
- [ ] 10. P12 `power_ship.test_entry_order_without_vbus`, `test_waits_for_vbus_removed`, `test_retry_once_after_1s`
- [ ] 11. P13 `power_ship.test_off_never_waits`
- [ ] 12. P14 `power_reset.test_causes_logged_then_cleared` (each of the 7 bits)
- [ ] 13. P17 `power_cfg.test_no_vbus_output_call`
- [ ] 14. P18 `power_ilim.test_first_active`, `test_again_with_screen_off`
- [ ] 15. P19 `power_cfg.test_pof_untouched`
- [ ] 16. X13 `power_report.test_charge_state_codes` (+ layout)
- [ ] 17. K5 answered in notes with file listing / counts (no kit lines printed)
- [ ] 18. K6 answered in notes (function names, sign, host build)
- [ ] 19. Suites on both targets: power_levels, power_charger, power_gauge, power_sample, power_ship, power_reset, power_ilim, power_cfg, power_report
- [ ] 20. Broken copies, each fails its named case only, both targets: voltage_ignored, mean_of_5, report_down_only, charge_on_rewrites, write_while_enabled, motor_charge_subtracted, ship_no_strobe, ship_no_wait, ilim_plays_m3, causes_not_cleared
- [ ] 21. Run ends `UNIT PASS tests/power`
- [ ] 22. Pure part (rpw_logic.c) has no kernel call (search saved); thin part reaches hardware only through rhw.h (search saved)
- [ ] 23. No pin by number in any source; no kit/Zephyr text copied; no key/address in files (searches saved)
- [ ] 24. Reading of the rulings: no rail call; no motor soft start; sampling class = RECORDING (FACTORY_TEST while a test recording runs: the join passes the RECORDING value)
- [ ] 25. Notes file `power-notes.md` maps rows, answers K5/K6, ends with RESULT line, lists `questions_for_owner`
- [ ] 26. Final audit script output saved; final reply saved
