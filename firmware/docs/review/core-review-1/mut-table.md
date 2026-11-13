| # | mutation | file:line changed | failing tests (first 3 of N) | caught | log |
|---|---|---|---|---|---|
| m01 | row 22 drops MH | diff `108d107` | 3: test_c1_short_in_recording_marks_highlight_not_status,test_c4_short_in_recording_screen_off_marks_and_shows_3s,test_row_22 | yes | mut/m01/host-run.log |
| m02 | row 21 swaps close and M2 | diff `103d102` | 1: test_row_21 | yes | mut/m02/host-run.log |
| m03 | row 25 drops charge on | diff `120d119` | 1: test_row_25 | yes | mut/m03/host-run.log |
| m04 | row 31 drops VDD_MIC off | diff `150d149` | 3: test_open_only_into_recording_and_every_exit_turns_mic_off,test_rail_follows_state_on_every_event_from_every_state,test_row_31 | yes | mut/m04/host-run.log |
| m05 | short ceiling 449 (off by one) | diff `78c78` | 2: test_pair_hold_450ms_short,test_sw2_hold_450ms_short | yes | mut/m05/host-run.log |
| m06 | double gap minimum 61 | diff `64c64` | 2: test_pair_gap_60ms_double,test_sw2_gap_60ms_double | yes | mut/m06/host-run.log |
| m07 | warning pulse at 501 ms | diff `109,110c109,110` | 6: test_mw_in_standby_and_recording_only,test_next_tick_follows_deadlines,test_pair_hold_500ms_ignored_warn | yes | mut/m07/host-run.log |
| m08 | release hold-off 29 ms | diff `113c113` | 2: test_next_tick_follows_deadlines,test_release_holdoff_29ms_bounce_same_press | yes | mut/m08/host-run.log |
| m09 | direction window 41 ms | diff `107c107` | 0:  | yes | mut/m09/host-run.log |
| m10 | repeat period 151 ms | diff `145c145` | 8: test_pair_dir_down_hold_repeat,test_pair_dir_left_hold_repeat,test_pair_dir_right_hold_repeat | yes | mut/m10/host-run.log |
| m11 | first repeat at 501 ms | diff `141c141` | 8: test_pair_dir_down_hold_repeat,test_pair_dir_left_hold_repeat,test_pair_dir_right_hold_repeat | yes | mut/m11/host-run.log |
| m12 | long press injectable through rc_core_event | diff `93c93` | 2: test_no_system_event_starts_a_recording,test_press_events_cannot_be_injected | yes | mut/m12/host-run.log |
| m13 | MW only in STANDBY | diff `129c129` | 1: test_mw_in_standby_and_recording_only | yes | mut/m13/host-run.log |
| m14 | highlight time = window close, not CENTRE_DOWN | diff `140c140` | 1: test_highlight_carries_centre_down_time | yes | mut/m14/host-run.log |
| m15 | B15 flag never cleared by VBUS | diff `60d59` | 0:  | NO | mut/m15/host-run.log |
| m16 | screen lock removed | diff `103c103` | 1: test_c4_lock_direction_and_short_only_wake | yes | mut/m16/host-run.log |
| m17 | guard AT_B5 excludes B5 | diff `99c99` | 1: test_row_37 | yes | mut/m17/host-run.log |
| m18 | PAIR: any other switch makes a centre press | diff `208c208` | 0:  | COMPILE-ERROR | mut/m18/host-run.log |
| m19 | roll or bounce does not hold the key down | diff `234d233` | 1: test_release_holdoff_29ms_bounce_same_press | yes | mut/m19/host-run.log |
| m20 | double press never recognised | diff `64c64` | 7: test_c3_centre_action_comes_after_window_and_double_is_dead,test_pair_gap_400ms_double,test_pair_gap_60ms_double | yes | mut/m20/host-run.log |
| m21 | hold released at exactly the mark is not long | diff `94c94` | 0:  | NO | mut/m21/host-run.log |
| m22 | state timers fire one ms late | diff `191c191` | 3: test_row53_open_flag_set_recovery_first,test_row_53,test_row_55 | yes | mut/m22/host-run.log |
| m23 | Vibration off also drops MW | diff `13c13` | 0:  | NO | mut/m23/host-run.log |
| m24 | short press fires at 400 not 401 | diff `114c114` | 13: test_c1_short_in_recording_marks_highlight_not_status,test_c4_lock_direction_and_short_only_wake,test_c4_short_in_recording_screen_off_marks_and_shows_3s | yes | mut/m24/host-run.log |
| m25 | S30 once never re-armed by a new recording | diff `64d63` | 0:  | NO | mut/m25/host-run.log |
| m26 | row 53 always runs recovery | diff `223,225c223` | 1: test_row_53 | yes | mut/m26/host-run.log |
| m27 | row 17 drops status screen | diff `90d89` | 1: test_row_17 | yes | mut/m27/host-run.log |
| m28 | graze limit 40 inclusive | diff `78c78` | 2: test_pair_hold_40ms_short,test_sw2_hold_40ms_short | yes | mut/m28/host-run.log |
| m29 | row 3 guard drops the battery test | diff `87c87` | 0:  | NO | mut/m29/host-run.log |
| m30 | row 12 drops M1 | diff `63d62` | 4: test_c2_long_press_with_screen_on_starts,test_c4_long_press_with_screen_off_starts,test_vibration_off_drops_mh_mt_only | yes | mut/m30/host-run.log |
| m31 | row 15 drops M2 | diff `79d78` | 1: test_row_15 | yes | mut/m31/host-run.log |
| m32 | long press may fire again (no once-per-press) | diff `152d151` | 23: test_c2_long_press_with_screen_on_starts,test_c4_long_press_with_screen_off_starts,test_vibration_off_drops_mh_mt_only | yes | mut/m32/host-run.log |
| m33 | timers injectable through rc_core_event | diff `94c94` | 0:  | NO | mut/m33/host-run.log |
| m34 | row 38 drops charge off | diff `169d168` | 1: test_row_38 | yes | mut/m34/host-run.log |
| m35 | row 29 drops the 30 min message | diff `141d140` | 1: test_row_29 | yes | mut/m35/host-run.log |
| m18b | PAIR: any other switch also makes a centre press | diff `208c208` | 1: test_pair_non_opposite_switch_ignored | yes | mut/m18b/host-run.log |
| m23b | Vibration off also drops M3 | diff `13c13` | 1: test_vibration_off_drops_mh_mt_only | yes | mut/m23b/host-run.log |
| m36 | marks after the release instant still fire during hold-off | diff `94c94` | 6: test_pair_hold_499ms_ignored_no_warn,test_pair_hold_999ms_ignored_warn,test_release_before_mark_in_holdoff_no_long | yes | mut/m36/host-run.log |
| m38 | mic rail not cleared on power loss into BOOT | diff `` | 0: - | NOT-APPLIED | mut/m38/host-run.log |
| m39 | row 5 swaps SD off and charge on | diff `33d32` | 1: test_row_05 | yes | mut/m39/host-run.log |
| m45 | long press at 999 ms | diff `111,112c111,112` | 20: test_c2_long_press_with_screen_on_starts,test_c4_long_press_with_screen_off_starts,test_next_tick_follows_deadlines | yes | mut/m45/host-run.log |
| m52 | after a sent direction other held switches are no longer ignored | diff `224c224` | 1: test_dir_sent_then_others_ignored_until_all_open | yes | mut/m52/host-run.log |
| m53 | up and down swapped on the screen | diff `122c122` | 2: test_screen_on_direction_goes_to_screen_with_mt,test_vibration_off_drops_mh_mt_only | yes | mut/m53/host-run.log |
| m54 | row 35 guard drops the battery test | diff `95c95` | 1: test_row_37 | yes | mut/m54/host-run.log |
| m38b | mic rail not cleared on power loss into BOOT | diff `46d45` | 1: test_rail_follows_state_on_every_event_from_every_state | yes | mut/m38b/host-run.log |
| m55 | second press no longer cancels the pending short press | diff `62c62` | 9: test_c3_centre_action_comes_after_window_and_double_is_dead,test_pair_gap_400ms_double,test_pair_gap_60ms_double | yes | mut/m55/host-run.log |

rows in tsv 46 applied and compiled 44 caught yes 38 survived NO 6
not applied/compile error: ['m18:COMPILE-ERROR', 'm38:NOT-APPLIED']
survivors: ['m15', 'm21', 'm23', 'm25', 'm29', 'm33']
