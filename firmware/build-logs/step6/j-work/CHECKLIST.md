# J recorder: checklist (started 2026-11-13 07:05 CET, limit 7 h = 14:05, 3/4 = 12:20)

## Build items (plan section 3 J, brief)
- [x] 1. src/rrec.c action executor: every rc_action carried out in order through U2 to U8 evidence: rrec.c; j-unit1.log
- [x] 2. src/rrec_mics.c: rec_mics_on() the ONLY VDD_MIC-on path, only after rscr_sign_start answered 0; rec_mics_off() evidence: rrec_mics.c; stage recorder-one-mic-path j-stages1.log
- [x] 3. src/rrec_boot.c: reset causes, crash block, charge on with VBUS before mount, mount, facts, init done / storage init fails evidence: rrec_boot.c; recorder_boot j-cases1.log
- [x] 4. src/rrec_bridge.c: power, USB, store, audio callbacks into the glue as core events; level into rglue_battery(); battery into rscr_set_battery() evidence: rrec_bridge.c; j-cases1.log
- [x] 5. src/rrec_backend.c: fills U4's backend evidence: rrec_backend.c; recorder_rules j-cases1.log
- [x] 6. glue addition rglue_battery(level) evidence: rglue.c; j-bsim1.log
- [x] 7. glue addition rglue_ops.sign_start passed to rc_core_set_sign_hook (D1) evidence: rglue.c; recorder_sign j-cases1.log
- [x] 8. app CMakeLists module list gains ring_rhw ring_store ring_audio ring_xfer ring_power ring_motor ring_sys ring_factory ring_recorder evidence: app/CMakeLists.txt; j-stages1.log
- [x] 9. main.c starts the core in BOOT and calls rrec_init(); prints `ring-os recorder: boot done, state STANDBY` evidence: j-stages1.log recorder line
- [x] 10. simulated-chip overlay gains the simulated card and microphone nodes evidence: app overlay; j-stages1.log
- [x] 11. prj.conf / board conf: CONFIG_RING_RHW_SIM per board (D11b: on for bsim, off for dk) evidence: recorder-product-drivers j-stages1.log
- [x] 12. stage 2 start line kept evidence: j-stages1.log start line
- [x] 13. D3: motor soft start NOT built evidence: no soft start code (rrec.c plays patterns only)
- [x] 14. R22 FACTORY EXIT = 0x02 (used through rrec_spec.h) evidence: rrec_spec.h RREC_FAC_EXIT used via rfa
- [x] 15. R23 event log codes used as listed evidence: rrec_log codes from rrec_spec.h
- [x] 16. R24 highlight marker (audio's job; join passes CENTRE_DOWN time) evidence: rrec_glue_after passes highlight_ms; test_ble_highlight_marks
- [x] 17. watchdog fed when both threads reported in 2 s or no recording runs (rsy_recording around recordings, rsy_progress from audio and storage paths) evidence: test_watchdog_fed_while_recording j-cases1.log
- [x] 18. a recording started during the 10 s ilim hold draws SCR_REC_DIM evidence: test_start_during_ilim_hold_is_dim j-cases1.log
- [x] 19. battery sampling "recording states": RECORDING and FACTORY_TEST during a test recording (rpw_state) evidence: rrec.c rpw_state; notes s2 item 10
- [x] 20. storage chip with no valid superblock: new log at first mount (store's; boot path accepts it) evidence: store's; boot accepts (rows 3, j-cases1)
- [x] 21. no chip pin by number in any source or overlay of mine evidence: recorder-no-raw-pins j-stages1.log
- [x] 22. every number from rrec_spec.h; test expected values typed from FW with the line evidence: tests type FW values with lines (source)
- [x] 23. no kit/Zephyr code copied or printed evidence: written for this project; no kit lines printed
- [x] 24. no other company's logo or product name in a string evidence: no product names in strings (source)
- [x] 25. no secret / server address in any file or output evidence: no secret/address in my files (audit)
- [x] 26. no browser, no git, no /dev/null, stderr 2>&1 evidence: no browser, no git, 2>&1 used
- [x] 27. only owned files changed (listing saved) evidence: owned files: j-work/j-owned.log

## Tests (suites, both targets)
- [x] 28. recorder_rows evidence: j-cases1.log
- [x] 29. recorder_actions evidence: j-cases1.log
- [x] 30. recorder_boot evidence: j-cases1.log
- [x] 31. recorder_sign evidence: j-cases1.log
- [x] 32. recorder_sign1 evidence: j-cases1.log
- [x] 33. recorder_sequence evidence: j-cases1.log
- [x] 34. recorder_rails evidence: j-cases1.log
- [x] 35. recorder_rules evidence: j-cases1.log
- [x] 36. recorder_log evidence: j-cases1.log
- [x] 37. recorder_screens evidence: j-cases1.log
- [x] 38. native_sim pass evidence: j-unit1.log l.22
- [x] 39. nrf54lm20bsim/nrf54lm20a/cpuapp pass evidence: j-unit1.log l.44

## Broken copies (each fails its named case on both targets)
- [x] 40. mic_before_sign -> recorder_sign.test_start_draws_sign_before_mic evidence: j-unit1.log broken part
- [x] 41. mic_on_refused_sign -> recorder_sign.test_sign_refused_no_mic_m3_log evidence: j-unit1.log broken part
- [x] 42. screen_leaves_before_mic_off -> recorder_sign.test_close_mic_off_before_screen_leaves evidence: j-unit1.log broken part
- [x] 43. dim_dark -> recorder_sign1.test_sign1_every_row evidence: j-unit1.log broken part
- [x] 44. m2_before_mic_off -> recorder_actions.test_stop_m2_after_mic_off evidence: j-unit1.log broken part
- [x] 45. sd_off_before_mic_off -> recorder_actions.test_close_order evidence: j-unit1.log broken part
- [x] 46. charge_after_mount -> recorder_boot.test_vbus_boot_charges_before_mount evidence: j-unit1.log broken part
- [x] 47. retry_not_reported -> recorder_actions.test_retry_storage_reports_result evidence: j-unit1.log broken part
- [x] 48. mic_in_factory_idle -> recorder_rows.test_mic_rail_only_in_recording evidence: j-unit1.log broken part
- [x] 49. usb_long_press -> recorder_rules.test_no_command_starts_or_stops evidence: j-unit1.log broken part
- [x] 50. no_log_on_state_change -> recorder_log.test_each_kind_logged evidence: j-unit1.log broken part
- [x] 51. sd_on_in_standby -> recorder_rails.test_rails_per_state evidence: j-unit1.log broken part
- [x] 52. each edit matches exactly once (local check saved) evidence: j-editcheck1.log
- [x] 53. other failing cases per copy listed evidence: notes s10

## Rows mapped in notes (case + log line, or NP with reason)
- [x] 54. C1 evidence: notes s9, j-map.out
- [x] 55. C4 to C27 (each) evidence: notes s9, j-map.out
- [x] 56. C33 evidence: notes s9, j-map.out
- [x] 57. C36 to C39 evidence: notes s9, j-map.out
- [x] 58. A6, A10, A12, A13 evidence: notes s9, j-map.out
- [x] 59. P4, P6, P11, P12 evidence: notes s9, j-map.out
- [x] 60. T8, T9, T24, T27 evidence: notes s9, j-map.out

## build_all.sh (section 6 items 2 to 8)
- [x] 61. item 2: stage bsim-run also checks `ring-os recorder: boot done, state STANDBY` evidence: j-stages1.log
- [x] 62. item 3: stage recorder-one-mic-path + self test (planted second call) evidence: j-stages1.log
- [x] 63. item 4: stage recorder-no-start-path + self test evidence: j-stages1.log
- [x] 64. item 5: stage recorder-no-raw-pins + self test evidence: j-stages1.log
- [x] 65. item 6: stage recorder-product-drivers + self test (planted kit .config with SIM on refused) evidence: j-stages1.log
- [x] 66. item 7: stack_report.py new threads evidence: j-stages1.log stack-report exit 0
- [x] 67. item 8: link-settings unchanged unless beacon needs a setting (decide, note) evidence: notes s5 item 8
- [x] 68. comment block lists each new stage evidence: build_all.sh header
- [x] 69. each new stage's own commands run alone, incl. self test (command in notes) evidence: stages_run.sh, j-stages1.log
- [x] 70. last line RESULT PASS / RESULT FAIL kept evidence: build_all.sh last lines unchanged

## Other bar items
- [x] 71. product app boots through the recorder on the simulated chip and prints the boot line (run evidence) evidence: j-stages1.log
- [x] 72. development kit build still compiles (run evidence) evidence: j-stages1.log dk exit 0
- [x] 73. 21 screen pictures stay equal (screens suite unchanged; I touch no screens file) evidence: j-screens1.log, j-work/j-compare-screens.txt RESULT EQUAL
- [x] 74. existing suites of steps 1 to 5 still pass (glue/app changed): which run proves it evidence: j-bsim1.log; other unit suites not re-run by me
- [x] 75. targeted run ends `UNIT PASS tests/recorder` (full unit run with exit file) evidence: j-unit1.log
- [x] 76. notes: what the dk build needs that step 7 must add evidence: notes s6
- [x] 77. notes: open points inherited (USB real file, K10 settings, USB vid/pid test pair not for shipping) evidence: notes s7
- [x] 78. notes: questions_for_owner list evidence: notes
- [x] 79. notes last line RESULT evidence: notes last line
- [x] 80. README.md updated evidence: README.md
- [x] 81. final reply under 3,500 characters; final audit run and saved evidence: j-audit.log
