# Motor unit U6: notes (software step 6)

Files: `modules/ring_motor/src/rmo_logic.[ch]` (pure: pattern table, replace rule, Vibration filter, charge per pulse),
`rmo.c` (thin: k_timer player, pin through `rhw_motor()`, time through `rhw_clock()`), `rmo_hw_real.c` (MOTOR GPIO by
the devicetree alias `ring-motor`; kit build only, NOT PROVEN), `Kconfig`, `CMakeLists.txt`, `zephyr/module.yml`;
tests in `tests/motor/` (suites `motor_player` 11 cases, `motor_charge` 3 cases; `broken_edit.py`, `broken_run.sh`).

## 1. Readings and decisions

1. Soft start (ruling D3): not built. `rmo.h` and `rrec_spec.h` hold no soft-start item (rmo.h line 6 only says it is not
   built; rrec_spec.h line 11 says no constant). No `RING_MOTOR_SOFT_START`, no `motor_soft`, no C35, no copies
   `soft_on_by_default` / `soft_one_step_short`.
2. The pattern times are not constants of `rrec_spec.h` (it holds the ids and the 80 / 175 mA / 10 ms charge numbers
   only; the times are comments at lines 319 to 325). They are a table in `rmo_logic.c` from FW l.320 to l.328.
3. Schedule: each segment boundary is the pattern's start tick plus the cumulative ms (ceil to ticks), so rounding does
   not add up. First MOTOR high is at the call of `rmo_play`.
4. A replacement during an on segment keeps the pin high (no low then high): the old pulse is closed and its charge so
   far reported (elapsed ms x 80 + 1,750 uA.s), the new pulse counts as a new start. In an off gap the pin goes high at
   once. A pulse cut by `rmo_stop` is reported the same way. FW says nothing on this; it is a CHOICE of this unit.
5. Return codes of `rmo_play` are checked in this order: -EINVAL (unknown id), -ECANCELED (Vibration off and MH/MT),
   -EBUSY (replace rule), 0.
6. Callbacks run under the player's spinlock; they must not call back into `rmo_*`.
7. `rmo_init` registers a reboot hook (simulation only) that clears the player's RAM state.

## 2. Rows of the plan that name U6

Log = `build-logs/step6/u6-unit-run1.log` (exit file `u6-unit-run1.exit` = 0; line 520 `RESULT PASS`, line 522 last result
line `UNIT PASS tests/motor`). Green counts of the unbroken suites, 14 of 14 (11 `motor_player` + 3 `motor_charge`):
native_sim line 22 (`14 of 14 executed test cases passed`, PASSED at line 18), nrf54lm20bsim/nrf54lm20a/cpuapp line 44
(PASSED at line 40). A passing case prints nothing in the log, so each row cites those count lines; the broken copies
(section 3) show each named case can fail.

| Row | Case | Evidence |
|---|---|---|
| C26 | `motor_player.test_vibration_off_keeps_the_others` | log lines 22, 44; fails in `vibration_mutes_mw` (lines 189, 228) |
| C28 | `motor_player.test_one_high_per_on_segment` (highs = lows = pulses per pattern, alternating, no other event; MF at 150 ms has one event) | log lines 22, 44; no broken copy of its own (plan names none) |
| C29 | `motor_player.test_every_pattern_pin_times` (each edge within [t, t+1 ms) of its typed time; start at the call) | log lines 22, 44; fails in `m2_gap_100` (lines 274, 316) |
| C30 | `motor_player.test_replace_rules` (all 49 pairs, typed 7x7 table, 8 refused and 41 played asserted), `test_replace_in_gap`, `test_same_pattern_restarts` | log lines 22, 44; fails in `mh_cuts_m1` (lines 94, 133) |
| C31 | `motor_player.test_every_pattern_pin_times`, `test_pattern_table` (totals 80, 280, 480, 40, 25, 60, 800 ms; pulses 1, 2, 3, 1, 1, 1, 2) | log lines 22, 44; `m2_gap_100` fails both (lines 274, 276) |
| C32 | `motor_charge.test_charge_per_pattern` (typed uA.s 8,150 / 16,300 / 24,450 / 4,950 / 3,750 / 6,550 / 51,500; per pulse; reported at the low edge; pure part equal), `test_cut_pulse_charge`, `test_no_charge_without_a_pulse` | log lines 22, 44; fails in `allowance_5ms` (lines 459, 499) |
| C33, U6 part | `motor_player.test_edge_times_reported` (edge callback cycles equal the pin event's time at 1 MHz, one callback per edge; started callback id and ms). `audio_motor.*` is U3's, `recorder_log.test_pattern_start_logged` is J's | log lines 22, 44; fails in `edge_late` (lines 369, 410) |
| P7 | `motor_player.test_pin_low_between_patterns` (M3 sampled mid each of 5 segments; idle, gaps, between patterns, end), `test_stop_pin_low_at_once`. The regulator U11: not provable without hardware | log lines 22, 44 |
| C25 (motor side), C27, C34 | the join plays the patterns; whether MT is felt: not provable without hardware (bench F1) | n/a |
| C35 | dropped by ruling D3 | n/a |

Not provable without hardware: the motor's spin, the felt pulse, the start current (the 10 ms x 175 mA allowance is an
estimate until bench B-M3), U11's 0.55 ms start delay and enable, `rmo_hw_real.c` (compiles in the kit build only).

## 3. Broken copies (each on both targets; "also" = other cases failing with it, from the log)

| Copy | Named case | Named case failed | Also failed |
|---|---|---|---|
| `mh_cuts_m1` | `motor_player.test_replace_rules` | native_sim line 104, bsim line 143 | none (13 of 14 passed, lines 101, 140) |
| `vibration_mutes_mw` | `motor_player.test_vibration_off_keeps_the_others` | line 195, line 234 | none (13 of 14, lines 192, 231) |
| `m2_gap_100` | `motor_player.test_every_pattern_pin_times` | line 289, line 331 | `test_pattern_table`, `test_replace_rules`, `test_vibration_off_keeps_the_others` (10 of 14, lines 286, 328; cases at 274 to 283) |
| `edge_late` | `motor_player.test_edge_times_reported` | line 385, line 426 | `motor_charge.test_charge_per_pattern` (12 of 14, lines 382, 423; it compares the charge callback's clock with the edge cycles) |
| `allowance_5ms` | `motor_charge.test_charge_per_pattern` | line 479, line 519 | `motor_charge.test_cut_pulse_charge` (12 of 14, lines 476, 516) |

Lines 476 and 516 are `allowance_5ms`'s two runs (12 of 14), as the lead noted. No named case passed on any copy. The
two soft start copies of the plan are not built (ruling D3). Short run before the full run: `build-logs/step6/u6-short-run1.log`
(28 of 28 cases, 2 of 2 configurations). Edit check: `u6-editcheck.log` (each edit matched once).

## questions_for_owner

none

RESULT: done, `UNIT PASS tests/motor` on both targets (14 of 14 cases each) and each of the 5 broken copies fails its named case on both targets (log line 522).
