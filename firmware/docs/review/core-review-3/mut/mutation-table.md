| Mutation | Host tests failed (of 202) | Caught | First failing tests | Log |
|---|---|---|---|---|
| r01_b2_entry_check_removed | 7 | yes | test_r1_entry_into_standby_checks_battery_then_storage, test_r10_leaving_case_at_b2_switches_off, test_r12_b2_in_boot_kept_then_off | mut/r01_b2_entry_check_removed/host-run.log |
| r02_b2_entry_skips_mic_fault | 1 | yes | test_r15_walk_every_entry_with_b2_kept_ends_off | mut/r02_b2_entry_skips_mic_fault/host-run.log |
| r03_b2_entry_skips_charger | 1 | yes | test_r15_walk_every_entry_with_b2_kept_ends_off | mut/r03_b2_entry_skips_charger/host-run.log |
| r04_b2_entry_ignores_vbus | 1 | yes | test_r15_with_vbus_b2_does_not_switch_off | mut/r04_b2_entry_ignores_vbus/host-run.log |
| r05_b2_entry_skips_storage_fault_state | 3 | yes | test_r12_b2_in_boot_kept_then_off, test_r15_walk_every_entry_with_b2_kept_ends_off, test_r15b_failed_storage_init_with_b2_kept_goes_off | mut/r05_b2_entry_skips_storage_fault_state/host-run.log |
| r06_rstb_fault_check_dropped | 3 | yes | test_r4b_failed_write_then_case_then_long_press_never_records_over_it, test_r11_storage_fault_survives_the_case, test_row_24 | mut/r06_rstb_fault_check_dropped/host-run.log |
| r07_fault_fact_not_set_on_entry | 2 | yes | test_r4b_failed_write_then_case_then_long_press_never_records_over_it, test_r11_storage_fault_survives_the_case | mut/r07_fault_fact_not_set_on_entry/host-run.log |
| r08_retry_ok_keeps_fault | 7 | yes | test_r1_entry_into_standby_checks_battery_then_storage, test_r3_storage_retried_every_60s_until_success, test_r4b_failed_write_then_case_then_long_press_never_records_over_it | mut/r08_retry_ok_keeps_fault/host-run.log |
| r09_init_done_keeps_fault | 1 | yes | test_r11_fault_cleared_only_by_successful_init | mut/r09_init_done_keeps_fault/host-run.log |
| r10_recovery_entry_clears_open_flag | 3 | yes | test_r4b_failed_write_then_case_then_long_press_never_records_over_it, test_r9_long_press_recovery_keeps_flag_until_scan_done, test_r9_recovery_request_keeps_open_flag | mut/r10_recovery_entry_clears_open_flag/host-run.log |
| r11_clear_open_flag_ignored | 5 | yes | test_r4b_b5_with_open_flag_at_init_done_recovers_first, test_r4b_failed_write_then_case_then_long_press_never_records_over_it, test_r4b_long_press_with_open_flag_runs_recovery_first | mut/r11_clear_open_flag_ignored/host-run.log |
| r12_retry_every_missed_period | 1 | yes | test_r14_one_retry_per_tick_whatever_the_delay | mut/r12_retry_every_missed_period/host-run.log |
| r13_retry_next_in_30s | 2 | yes | test_r3_storage_retried_every_60s_until_success, test_r14_one_retry_per_tick_whatever_the_delay | mut/r13_retry_next_in_30s/host-run.log |
| r14_boot_battery_applied_at_once | 5 | yes | test_r12_b2_in_boot_kept_then_off, test_r12_b5_in_boot_kept_then_recovery_first, test_r15b_failed_storage_init_with_b2_kept_goes_off | mut/r14_boot_battery_applied_at_once/host-run.log |
| r15_boot_battery_level_not_kept | 7 | yes | test_code_c1_battery_fact_both_directions, test_code_c7_repeated_battery_level_does_nothing, test_r12_b2_in_boot_kept_then_off | mut/r15_boot_battery_level_not_kept/host-run.log |
| r16_row8_no_sd_off | 2 | yes | test_r13_row8_turns_sd_off, test_row_08 | mut/r16_row8_no_sd_off/host-run.log |
| r17_row41_no_ship | 2 | yes | test_r10_leaving_case_at_b2_switches_off, test_row_41 | mut/r17_row41_no_ship/host-run.log |
| r18_row41_guard_ge_b5 | 2 | yes | test_r2_vbus_out_with_sfull_and_b5_gives_battery_low, test_row_42 | mut/r18_row41_guard_ge_b5/host-run.log |
| r19_initdone_b2_needs_flag_clear | 1 | yes | test_r4b_b2_with_open_flag_goes_off_without_recovery | mut/r19_initdone_b2_needs_flag_clear/host-run.log |
| r20_init_failed_b2_not_checked_via_state_set | build error, invalid (not counted) | - | - | mut/r20_init_failed_b2_not_checked_via_state_set/host-run.log |
| r21_internal_fault_event_injectable | 0 | **NO** |  | mut/r21_internal_fault_event_injectable/host-run.log |
| r22_row59_open_flag_guard_inverted | 0 | **NO** |  | mut/r22_row59_open_flag_guard_inverted/host-run.log |
