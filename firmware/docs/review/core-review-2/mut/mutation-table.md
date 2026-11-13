| # | Mutation | Host tests failed (of 181) | Caught by host tests | My probes that failed (A/B/C/D) | Log |
|---|---|---|---|---|---|
| 1 | m01_row12_no_battery_guard | 2: test_r1_long_press_at_b5_refused_with_message, test_row_14 | yes | A--D | mut/m01_row12_no_battery_guard/host-run.log |
| 2 | m02_row12_no_storage_guard | 2: test_r1_long_press_at_sfull_refused_with_message, test_row_15 | yes | A--D | mut/m02_row12_no_storage_guard/host-run.log |
| 3 | m03_row12_no_openflag_guard | 3: test_r4b_failed_write_then_case_then_long_press_never_records_over_it, test_r4b_long_press_with_open_flag_runs_recovery_first, test_row_13 | yes | A-CD | mut/m03_row12_no_openflag_guard/host-run.log |
| 4 | m04_row12_b5_allowed | 2: test_r1_long_press_at_b5_refused_with_message, test_row_14 | yes | A--D | mut/m04_row12_b5_allowed/host-run.log |
| - | m05_rstb_no_storage_check | pattern did not apply, the copy ran unmutated (invalid, replaced by m05b) | invalid | - | mut/m05_rstb_no_storage_check/host-run.log |
| 5 | m05b_rstb_no_storage_check | 1: test_r1_entry_into_standby_checks_battery_then_storage | yes | ---- | mut/m05b_rstb_no_storage_check/host-run.log |
| 6 | m06_rstb_storage_before_battery | 1: test_r1_entry_into_standby_checks_battery_then_storage | yes | ---- | mut/m06_rstb_storage_before_battery/host-run.log |
| 7 | m07_rstb_b5_not_checked | 3: test_r1_entry_actions_are_those_of_the_standby_row, test_r1_entry_into_standby_checks_battery_then_storage, test_r4b_b5_with_open_flag_at_init_done_recovers_first | yes | --C- | mut/m07_rstb_b5_not_checked/host-run.log |
| 8 | m08_rstb_skips_mic_fault_entry | 1: test_r1_entry_into_standby_checks_battery_then_storage | yes | ---- | mut/m08_rstb_skips_mic_fault_entry/host-run.log |
| 9 | m09_rstb_skips_transfer_entry | 2: test_r1_entry_actions_are_those_of_the_standby_row, test_r1_entry_into_standby_checks_battery_then_storage | yes | ---- | mut/m09_rstb_skips_transfer_entry/host-run.log |
| 10 | m10_rstb_b2_not_checked | 1: test_r1_entry_into_standby_checks_battery_then_storage | yes | ---- | mut/m10_rstb_b2_not_checked/host-run.log |
| 11 | m11_no_hold_cancel | 2: test_r7_hold_begun_in_charging_never_starts, test_r7_hold_cancelled_by_change_of_state_in_standby | yes | -B-- | mut/m11_no_hold_cancel/host-run.log |
| 12 | m12_hold_cancel_not_into_standby | 1: test_r7_hold_begun_in_charging_never_starts | yes | -B-- | mut/m12_hold_cancel_not_into_standby/host-run.log |
| 13 | m13_hold_cancel_flag_unused | 2: test_r7_hold_begun_in_charging_never_starts, test_r7_hold_cancelled_by_change_of_state_in_standby | yes | -B-- | mut/m13_hold_cancel_flag_unused/host-run.log |
| 14 | m14_hold_cancel_not_warn | 1: test_r7_hold_cancelled_by_change_of_state_in_standby | yes | ---- | mut/m14_hold_cancel_not_warn/host-run.log |
| 15 | m15_retry_one_shot | 1: test_r3_storage_retried_every_60s_until_success | yes | --C- | mut/m15_retry_one_shot/host-run.log |
| 16 | m16_retry_period_30s | 1: test_r3_storage_retried_every_60s_until_success | yes | --C- | mut/m16_retry_period_30s/host-run.log |
| 17 | m17_retry_never_armed | 3: test_core_next_tick_includes_state_timers, test_r3_storage_retried_every_60s_until_success, test_row_56 | yes | --C- | mut/m17_retry_never_armed/host-run.log |
| 18 | m19_open_not_set_by_OPEN | 1: test_r4b_failed_write_then_case_then_long_press_never_records_over_it | yes | --C- | mut/m19_open_not_set_by_OPEN/host-run.log |
| 19 | m20_open_not_cleared_by_CLOSE | 1: test_code_c3_s30_rearmed_by_new_recording | yes | A--- | mut/m20_open_not_cleared_by_CLOSE/host-run.log |
| 20 | m21_open_not_cleared_by_RUN_RECOVERY | 0:  | **NO** | --C- | mut/m21_open_not_cleared_by_RUN_RECOVERY/host-run.log |
| 21 | m22_open_not_cleared_by_CLEAR_OPEN_FLAG | 2: test_r4b_b5_with_open_flag_at_init_done_recovers_first, test_r4b_long_press_with_open_flag_runs_recovery_first | yes | --C- | mut/m22_open_not_cleared_by_CLEAR_OPEN_FLAG/host-run.log |
| 22 | m23_initdone_b5_before_recovery | 1: test_r4b_b5_with_open_flag_at_init_done_recovers_first | yes | --C- | mut/m23_initdone_b5_before_recovery/host-run.log |
| 23 | m24_initdone_b2_needs_open_clear | 1: test_r4b_b2_with_open_flag_goes_off_without_recovery | yes | --C- | mut/m24_initdone_b2_needs_open_clear/host-run.log |
| 24 | m25_initdone_no_battery_read | 2: test_r4b_b2_with_open_flag_goes_off_without_recovery, test_r5_init_done_reads_battery_first | yes | --C- | mut/m25_initdone_no_battery_read/host-run.log |
| - | m26_charge_on_r8_removed | build error (mutation does not compile, not counted) | invalid | - | mut/m26_charge_on_r8_removed/host-run.log |
| 25 | m26b_charge_on_r8_never_added | 1: test_r8_charge_on_at_every_vbus_appearance | yes | --C- | mut/m26b_charge_on_r8_never_added/host-run.log |
| - | m27_charge_on_duplicated | build error (mutation does not compile, not counted) | invalid | - | mut/m27_charge_on_duplicated/host-run.log |
| 26 | m27b_charge_on_always_added_duplicate | 9: test_r8_charge_on_at_every_vbus_appearance, test_row_01, test_row_02 ... | yes | --C- | mut/m27b_charge_on_always_added_duplicate/host-run.log |
| 27 | m28_charge_on_not_in_boot | 1: test_r8_charge_on_at_every_vbus_appearance | yes | --C- | mut/m28_charge_on_not_in_boot/host-run.log |
| 28 | m29_charge_on_not_in_recovery | 1: test_r8_charge_on_at_every_vbus_appearance | yes | --C- | mut/m29_charge_on_not_in_recovery/host-run.log |
| 29 | m30_charge_on_not_in_error_states | 1: test_r8_charge_on_at_every_vbus_appearance | yes | --C- | mut/m30_charge_on_not_in_error_states/host-run.log |
| 30 | m31_batt_repeat_event_on_equal | 0:  | **NO** | ---D | mut/m31_batt_repeat_event_on_equal/host-run.log |
| 31 | m32_batt_upward_fires | 3: test_code_c1_battery_fact_both_directions, test_row20_m3_once_per_discharge, test_row29_m3_once_per_discharge | yes | --CD | mut/m32_batt_upward_fires/host-run.log |
| 32 | m33_batt_fact_after_event | 0:  | **NO** | ---- | mut/m33_batt_fact_after_event/host-run.log |
| 33 | m34_batt_fact_never_lowered_only_raised | 4: test_code_c1_battery_fact_both_directions, test_code_c3_b15_rearmed_by_vbus, test_row20_m3_once_per_discharge ... | yes | --C- | mut/m34_batt_fact_never_lowered_only_raised/host-run.log |
| 34 | m35_batt_invalid_level_accepted | 0:  | **NO** | --C- | mut/m35_batt_invalid_level_accepted/host-run.log |
| 35 | m36_long_press_injectable | 2: test_no_system_event_starts_a_recording, test_press_events_cannot_be_injected | yes | ---D | mut/m36_long_press_injectable/host-run.log |
| 36 | m37_row14_at_b5_only_exact | 1: test_r1_long_press_at_b5_and_sfull_battery_message | yes | ---- | mut/m37_row14_at_b5_only_exact/host-run.log |
| 37 | m38_row39_no_battery_guard | 1: test_r2_vbus_out_with_sfull_and_b5_gives_battery_low | yes | ---- | mut/m38_row39_no_battery_guard/host-run.log |
| 38 | m39_row3_open_clear_dropped | 1: test_row_04 | yes | --C- | mut/m39_row3_open_clear_dropped/host-run.log |
| 39 | m40_sfull_event_not_a_fact | 0:  | **NO** | --C- | mut/m40_sfull_event_not_a_fact/host-run.log |
| 40 | m41_cancel_clears_only_when_not_long_fired | 0:  | **NO** | ---- | mut/m41_cancel_clears_only_when_not_long_fired/host-run.log |
| 41 | m42_row57_always_run_recovery | 1: test_row_57 | yes | ---- | mut/m42_row57_always_run_recovery/host-run.log |
| 42 | m43_row57_never_run_recovery | 1: test_row57_open_flag_set_recovery_first | yes | --C- | mut/m43_row57_never_run_recovery/host-run.log |
| 43 | m44_row12_open_before_m1_swapped | 4: test_c2_long_press_with_screen_on_starts, test_c4_long_press_with_screen_off_starts, test_vibration_off_drops_mh_mt_only ... | yes | ---- | mut/m44_row12_open_before_m1_swapped/host-run.log |
| 44 | m45_row3_battery_guard_dropped_F1 | 1: test_code_c2_row3_guard_refuses_b5 | yes | ---- | mut/m45_row3_battery_guard_dropped_F1/host-run.log |
| 45 | m46_b15_flag_not_rearmed_by_vbus_F4 | 1: test_code_c3_b15_rearmed_by_vbus | yes | ---- | mut/m46_b15_flag_not_rearmed_by_vbus_F4/host-run.log |
| 46 | m47_s30_flag_not_rearmed_F4 | 1: test_code_c3_s30_rearmed_by_new_recording | yes | ---- | mut/m47_s30_flag_not_rearmed_F4/host-run.log |
| 47 | m48_timers_injectable_F4 | 1: test_code_c3_timers_refused_from_event_entry | yes | ---- | mut/m48_timers_injectable_F4/host-run.log |
| 48 | m49_dir_window_4000_F7 | 12: test_next_tick_follows_deadlines, test_pair_dir_down_hold_repeat, test_pair_dir_left_hold_repeat ... | yes | ---- | mut/m49_dir_window_4000_F7/host-run.log |
