| Mutation | Host tests failed (of 214) | Caught | First failing tests |
|---|---|---|---|
| v01_r16_block_removed | 6 | yes | test_r1_entry_into_standby_checks_battery_then_storage, test_r16_b2_row_comes_before_the_vbus_removed_row |
| v02_r16_fires_at_b5_too | 0 | **NO** |  |
| v03_r16_no_row_check | 6 | yes | test_r1_entry_into_standby_checks_battery_then_storage, test_r10_leaving_case_at_b2_switches_off |
| v04_r16_only_storage_fault_state | 4 | yes | test_r1_entry_into_standby_checks_battery_then_storage, test_r16_b2_row_comes_before_the_vbus_removed_row |
| v05_vbus_fact_not_cleared | 5 | yes | test_r1_entry_into_standby_checks_battery_then_storage, test_r4b_failed_write_then_case_then_long_press_never_records_over_it |
| v06_r16_only_with_open_flag_clear | 1 | yes | test_r16_sequences_never_awake_at_b2_without_vbus |
| v07_r16_also_on_vbus_in | 0 | **NO** |  |
| v08_r16_skips_error_charger | 2 | yes | test_r1_entry_into_standby_checks_battery_then_storage, test_r16_b2_row_comes_before_the_vbus_removed_row |
| v09_r16_skips_boot | 0 | **NO** |  |
| v10_r16_skips_recording | 2 | yes | test_r16_sequences_never_awake_at_b2_without_vbus, test_r16_walk_every_state_vbus_present_b2_then_vbus_out_ends_off |
| v11_c10_fault_set_injectable_r21 | 1 | yes | test_c10_refuses_storage_fault_set |
| v12_c10_timer60_injectable | 2 | yes | test_code_c3_timers_refused_from_event_entry, test_c10_refuses_timer_60s |
| v13_r16_b2_event_when_state_has_row_but_vbus_stays_set_r15_entry_off | 3 | yes | test_r15_with_vbus_b2_does_not_switch_off, test_r16_recovery_read_error_in_case_then_vbus_out_goes_off |
