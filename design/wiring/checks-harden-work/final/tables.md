
check_wiring.py broken copies (made by make_wiring_fakes.py from the corrected list copies/rebuilt-fixed.csv), final run logs/all-check_wiring.log, one log per copy in logs/cw/

| broken copy (file in W) | result | rejecting line (first, cut at 150 characters) |
|---|---|---|
| honest_fixed_copy (copies/cw/honest_fixed_copy.csv) | as expected |  |
| empty (copies/cw/empty.csv) | as expected | FAIL[terminal-missing] case BT1 pin 1 (net 'BAT') is in no line |
| flood_duplicates (copies/cw/flood_duplicates.csv) | as expected | FAIL[terminal-twice] case BT1 pin 1 is in 4 lines: W059 W059x0 W059x1 W059x2 |
| one_line_covers_all (copies/cw/one_line_covers_all.csv) | as expected | FAIL[terminal-unknown] W001 end B SW1 SW2 SW3 SW4 SW5 J_BAND_A J_BAND_B J1 CP1 CP2 CP3 CP4 P1 P2 P3 P4.3 has no netlist row in its proof |
| no_marking_lead (copies/cw/no_marking_lead.csv) | as expected | FAIL[state-kind] W023 is `specified and landed` but carrier 'lead' has marking '', gauge or model 'AWG32 (Jinlong W0525AB001D lead)', cuts ['1.12', '1 |
| no_cut_lead (copies/cw/no_cut_lead.csv) | as expected | FAIL[lead-length] W023 lead has cut lengths ['1.12', '1.07', '', '1.14', '1.39', '1.44', '1.39'] and no 'not size dependent' |
| wrong_net_both (copies/cw/wrong_net_both.csv) | as expected | FAIL[states-net] W001 end A J_BAND_A.1 states net 'JOY_DOWN', the ring netlist says 'JOY_UP' |
| swap_B_ends (copies/cw/swap_B_ends.csv) | as expected | FAIL[terminal-unknown] W001 end B SW3.3 has no netlist row in its proof |
| wrong_tail_land (copies/cw/wrong_tail_land.csv) | as expected | FAIL[states-tail] W001 join text says FLEX1 tail land 2 but end A is ring main board J_BAND_A.1 |
| wrong_face_W040 (copies/cw/wrong_face_W040.csv) | as expected | FAIL[states-face] W040 end B J1.1 face states 'F.Cu', the board file has ['B.Cu'] |
| wrong_face_W029 (copies/cw/wrong_face_W029.csv) | as expected | FAIL[states-face] W029 end B CP1.1 face states 'F.Cu', the board file has ['B.Cu'] |
| spring_pin_swap (copies/cw/spring_pin_swap.csv) | as expected | FAIL[terminal-unknown] W054 end B P4.1 has no netlist row in its proof |
| case_wire_swap (copies/cw/case_wire_swap.csv) | as expected | FAIL[terminal-unknown] W063 end B W4.1 has no netlist row in its proof |
| motor_colour_swap (copies/cw/motor_colour_swap.csv) | as expected | FAIL[states-colour] W023 source says red, the line says marking 'blue insulation', carrier 'red lead wire AWG32 of the motor' |
| cut_wrong_value_9.99 (copies/cw/cut_wrong_value_9.99.csv) | as expected | FAIL[states-cut] W023 cut length at US 9 is '9.99', the source table says '1.08' |
| proof_text_fake (copies/cw/proof_text_fake.csv) | as expected | FAIL[proof-text] W023 proof_carrier: design/ecad/band/band-interface.md line 123 does not hold 'this sentence is not in the file' |
| row_dropped (copies/cw/row_dropped.csv) | as expected | FAIL[terminal-missing] ring CP2 pin 1 (net 'USB_DN') is in no line |
| net_in_netlist_only (copies/cw/net_in_netlist_only.csv) | as expected | FAIL[states-net] W040 end B J1.1 states net 'ELVDD', the ring netlist says 'ELVSS' |
| end_A_main_face_wrong (copies/cw/end_A_main_face_wrong.csv) | as expected | FAIL[states-face] W001 end A J_BAND_A.1 face states 'B.Cu', the board file has ['F.Cu'] |
| end_A_tail_face_wrong (copies/cw/end_A_tail_face_wrong.csv) | as expected | FAIL[states-face] W001 end A tail land face states 'B.Cu', the flex boards have ['F.Cu'] |
| tail_land_wrong_flex (copies/cw/tail_land_wrong_flex.csv) | as expected | FAIL[states-tail] W001 join text says FLEX2 tail land 1 but end A is ring main board J_BAND_A.1 |
| cut_one_size (copies/cw/cut_one_size.csv) | as expected | FAIL[states-cut] W023 cut length at US 13 is '1.40', the source table says '1.39' |
| cut_case_wire (copies/cw/cut_case_wire.csv) | as expected | FAIL[states-cut] W063 cut length at US 7 is '15.7', the source table says '15.6' |
| cut_thermistor (copies/cw/cut_thermistor.csv) | as expected | FAIL[states-cut] W061 cut length at US 10 is '12', the source table says '10' |
| case_wire_colour (copies/cw/case_wire_colour.csv) | as expected | FAIL[states-colour] W064 source says white, the line says marking 'green insulation', carrier 'wire 30 AWG stranded, white, cut 16.3 mm (path 11.' |
| cell_lead_colour (copies/cw/cell_lead_colour.csv) | as expected | FAIL[states-colour] W059 cell lead 1 marking 'black (-)', the source gives colour 'red' |
| copper_length_changed (copies/cw/copper_length_changed.csv) | as expected | FAIL[states-copper] W001 copper length at US 9 is '11.000', the board gives 11.584 |
| carrier_net_differs (copies/cw/carrier_net_differs.csv) | as expected | FAIL[states-net] W001 carrier net 'JOY_UP2' does not follow its end nets 'JOY_UP' and 'JOY_UP' |
| cr_in_field (copies/cw/cr_in_field.csv) | as expected | FAIL[field-newline] W001 field state_reason holds 1 carriage return and 0 newline characters (first at offset 9) |
| newline_in_field (copies/cw/newline_in_field.csv) | as expected | FAIL[field-newline] W001 field state_reason holds 0 carriage return and 1 newline characters (first at offset 9) |
| rebuild_state_reason (copies/cw/rebuild_state_reason.csv) | as expected | FAIL[rebuild] W001 field state_reason: list says 'all fine, trust me', the generator builds 'both ends in all 7 flex1 board files with net JOY_UP, cop |
| rebuild_join_B (copies/cw/rebuild_join_B.csv) | as expected | FAIL[rebuild] W001 field join_B: list says 'hand solder', the generator builds 'reflow' |
| rebuild_cut_note (copies/cw/rebuild_cut_note.csv) | as expected | FAIL[rebuild] W040 field cut_note: list says 'size dependent', the generator builds 'not size dependent' |
| rebuild_pad_pin_text (copies/cw/rebuild_pad_pin_text.csv) | as expected | FAIL[rebuild] W001 field end_B_pin: list says '4', the generator builds '3' |

check_joints.py broken copies (make_joints_fakes.py), final run logs/all-check_joints.log, one log per copy in logs/cj/

| broken copy (file in W) | result | rejecting line (first, cut at 150 characters) |
|---|---|---|
| real_snapshot_as_it_stands (copies/cj/real_snapshot_as_it_stands.csv) | as expected | R6 weak-check: J-W027-A check names no pass value or pass condition: 'land B3, FACTORY ENTER and T-CHARGE pass at the end of the step; an open NTC lan |
| real_with_W027_check_amended (copies/cj/real_with_W027_check_amended.csv) | as expected |  |
| check_ok (copies/cj/check_ok.csv) | as expected | R6 weak-check: J-W054-A check names no method (what is measured or looked at): 'ok' |
| check_looks_fine (copies/cj/check_looks_fine.csv) | as expected | R6 weak-check: J-W054-A check names no method (what is measured or looked at): 'looks fine, checked by the builder' |
| check_measure_without_pass (copies/cj/check_measure_without_pass.csv) | as expected | R6 weak-check: J-W054-A check names no pass value or pass condition: 'ohmmeter at the foot, optical inspection at 20 times' |
| check_pass_without_method (copies/cj/check_pass_without_method.csv) | as expected | R6 weak-check: J-W054-A check names no method (what is measured or looked at): 'the result is good enough and less than 5 is fine' |
| check_accept_rule_of_missing_step (copies/cj/check_accept_rule_of_missing_step.csv) | as expected | R6 weak-check: J-W054-A check names no pass value or pass condition: 'optical inspection; each joint passes the accept rules of step 99' |
| check_file_line_past_end (copies/cj/check_file_line_past_end.csv) | as expected | R6 weak-check: J-W054-A check names no pass value or pass condition: 'optical inspection; accept rule design/mfg/assembly/process.md:99999' |
| check_file_line_real_accepted (copies/cj/check_file_line_real_accepted.csv) | as expected |  |
| check_file_line_holds_no_pass_value (copies/cj/check_file_line_holds_no_pass_value.csv) | as expected | R6 weak-check: J-W054-A check names no pass value or pass condition: 'optical inspection; accept rule design/mfg/assembly/process.md:100' |
| check_file_line_other_text (copies/cj/check_file_line_other_text.csv) | as expected | R6 weak-check: J-W054-A check names no pass value or pass condition: 'optical inspection; accept rule design/mfg/assembly/process.md:1' |
| check_accept_rule_step_real_accepted (copies/cj/check_accept_rule_step_real_accepted.csv) | as expected |  |
| check_number_unit_accepted (copies/cj/check_number_unit_accepted.csv) | as expected |  |
| heat_hot (copies/cj/heat_hot.csv) | as expected | R7 weak-heat: J-W054-A heat names no value with a unit (C, s, N) and no profile with its file, and is not none with a reason: 'hot' |
| heat_warm_no_value (copies/cj/heat_warm_no_value.csv) | as expected | R7 weak-heat: J-W054-A heat names no value with a unit (C, s, N) and no profile with its file, and is not none with a reason: 'warm enough to melt the |
| heat_value_without_unit (copies/cj/heat_value_without_unit.csv) | as expected | R7 weak-heat: J-W054-A heat names no value with a unit (C, s, N) and no profile with its file, and is not none with a reason: 'iron 340' |
| heat_none_without_reason (copies/cj/heat_none_without_reason.csv) | as expected | R7 weak-heat: J-W054-A heat says none or no heat without a reason after a colon: 'none' |
| heat_profile_without_file (copies/cj/heat_profile_without_file.csv) | as expected | R7 weak-heat: J-W054-A heat names no value with a unit (C, s, N) and no profile with its file, and is not none with a reason: 'P3 profile' |
| heat_profile_missing_section (copies/cj/heat_profile_missing_section.csv) | as expected | R7 weak-heat: J-W054-A heat names no value with a unit (C, s, N) and no profile with its file, and is not none with a reason: 'P9 profile (process.md  |
| heat_value_no_tool_anywhere (copies/cj/heat_value_no_tool_anywhere.csv) | as expected | R7 weak-heat: J-W054-A heat names a value but no tool or process (neither here nor in the tool field): '340 C, 7 s' |
| heat_value_tool_in_tool_field_accepted (copies/cj/heat_value_tool_in_tool_field_accepted.csv) | as expected |  |
| heat_profile_with_file_accepted (copies/cj/heat_profile_with_file_accepted.csv) | as expected |  |
| heat_none_with_reason_accepted (copies/cj/heat_none_with_reason_accepted.csv) | as expected |  |
| rev_check_ok (copies/cj/rev_check_ok.csv) | as expected | R6 weak-check: J-W026-A check names no method (what is measured or looked at): 'ok' |
| rev_heat_hot (copies/cj/rev_heat_hot.csv) | as expected | R7 weak-heat: J-W061-B heat names no value with a unit (C, s, N) and no profile with its file, and is not none with a reason: 'hot' |

check_assembly.py broken copies (make_assembly_fakes.py, from a snapshot of the guide taken at the start of the run), final run logs/all-check_assembly.log, one log per copy in logs/ca/

| broken copy (file in W) | result | rejecting line (first, cut at 150 characters) |
|---|---|---|
| honest_snapshot (copies/ca/honest_snapshot.md) | as expected | no new line against itself |
| G1_reintroduced_both_steps (copies/ca/G1_reintroduced_both_steps.md) | as expected | P1 FAIL step 2 says the ribbon lands get no paste, joints.csv says they get paste: - **The 15 ribbon lands:** J_BAND_A (8 lands) and J_BAND_B (7 lands |
| G1_step2_only_no_paste (copies/ca/G1_step2_only_no_paste.md) | as expected | P1 FAIL step 2 says the ribbon lands get no paste, joints.csv says they get paste: - **The 15 ribbon lands:** J_BAND_A (8 lands) and J_BAND_B (7 lands |
| G1_step14_only_bare_lands (copies/ca/G1_step14_only_bare_lands.md) | as expected | P1 FAIL step 14 Join does not say 'on the solder layer that step 2 put on the 15 lands' |
| ribbon_land_count_wrong_step2 (copies/ca/ribbon_land_count_wrong_step2.md) | as expected | P1 FAIL step 2 gives J_BAND_A as 7, joints.csv has 8 lands; step 2 gives J_BAND_B as 8, joints.csv has 7 lands |
| ribbon_land_total_wrong_step14 (copies/ca/ribbon_land_total_wrong_step14.md) | as expected | P1 FAIL step 14 says step 2 put solder on 14 lands, joints.csv says step 2 and 15 lands |
| ribbon_paste_pass_wrong (copies/ca/ribbon_paste_pass_wrong.md) | as expected | P1 FAIL step 2 does not say PASS 2 for the ribbon lands |
| cell_tabs_swapped (copies/ca/cell_tabs_swapped.md) | as expected | L1 FAIL step 9 puts tab P+ on land 2 (GND), product-wiring.csv has land 1 (VBAT); step 9 puts tab P- on land 1 (VBAT), product-wiring.csv has land 2 ( |
| cell_tabs_NTC_and_Pminus_swapped (copies/ca/cell_tabs_NTC_and_Pminus_swapped.md) | as expected | L1 FAIL step 9 puts tab NTC on land 2 (GND), product-wiring.csv has land 3 (NTC); step 9 puts tab P- on land 3 (NTC), product-wiring.csv has land 2 (G |
| cell_tab_order_wrong (copies/ca/cell_tab_order_wrong.md) | as expected | L1 FAIL step 9 says the tabs in the order P+, NTC, P- lie on lands 1, 2, 3; product-wiring.csv gives lands 1, 3, 2 |
| motor_lead_land_swapped (copies/ca/motor_lead_land_swapped.md) | as expected | L1 FAIL step 7 does not say 'land 1, net VMOT, joined to land 7' (product-wiring.csv) |
| motor_check_lands_swapped (copies/ca/motor_check_lands_swapped.md) | as expected | L1 FAIL step 7 check does not name tail land 7 as (VMOT) (product-wiring.csv); step 7 check does not name tail land 6 as (GND) (product-wiring.csv) |
| motor_red_lead_on_minus (copies/ca/motor_red_lead_on_minus.md) | as expected | L1 FAIL step 7 puts the blue lead on the + land, product-wiring.csv says red |
| disc_lands_swapped (copies/ca/disc_lands_swapped.md) | as expected | L1 FAIL the disc step puts VBUS on land 5, product-wiring.csv has land 4; the disc step puts USB_DN on land 4, product-wiring.csv has land 5 |
| joints_table_tab_land_differs_from_wiring (copies/ca/joints_table_tab_land_differs_from_wiring.md) | as expected | L1 FAIL joints.csv J-W025-B says tab P+ on land 2 (GND), product-wiring.csv has land 1 (VBAT) |
| joints_table_says_no_paste_for_a_ribbon_land (copies/ca/joints_table_says_no_paste_for_a_ribbon_land.md) | as expected | P1 FAIL 1 of 15 J_BAND rows of joints.csv name no paste printed in a pass of a step |
| wiring_list_tab_land_differs_from_guide (copies/ca/wiring_list_tab_land_differs_from_guide.md) | as expected | L1 FAIL joints.csv J-W025-B says tab P+ on land 1 (VBAT), product-wiring.csv has land 2 (VBAT); joints.csv J-W033-B says tab P+ on land 1 (VBAT), prod |
| citation_prose_wrong_line (copies/ca/citation_prose_wrong_line.md) | as expected | TOKEN line 141: design/ecad/band/band-interface.md:3 holds none of GND (it holds: Written 2026-11-13 by the W4 builder. Project root: /Users/a) |
| citation_bom_other_row (copies/ca/citation_bom_other_row.md) | as expected | TOKEN line 159: design/bom.csv:48 holds none of BT1, PRT1, RT1, cell_protection (it holds: Capacitor 10 uF 0402 6.3 V,C83,1,U11 input (C84 at the outp |
| citation_placement_final_other_row (copies/ca/citation_placement_final_other_row.md) | as expected | TOKEN line 21: design/ecad/ring/pcb/placement-final.csv:78 holds none of J1 (it holds: C29,OpenRing:Chip_0402,F,-0.200,-2.850,270,Z12,99.800,97.150) |
| citation_netlist_other_row (copies/ca/citation_netlist_other_row.md) | as expected | TOKEN line 222: design/ecad/ring/netlist.csv:381 holds none of DISP1, ELVDD, ELVSS, J1, VDD_3V0 (it holds: XC2,X1,3,X2,passive) |
| citation_past_end (copies/ca/citation_past_end.md) | as expected | E1 FAIL citations that do not open: design/ecad/band/band-interface.md:9999 (file has 148 lines) |
| step_without_check_field (copies/ca/step_without_check_field.md) | as expected | C1 FAIL step 9 lacks Check |
| no_result_line (copies/ca/no_result_line.md) | as expected | G1 FAIL last line starts with RESULT: () |
| steps_twice (copies/ca/steps_twice.md) | as expected | B1 FAIL step numbers [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| empty_file (copies/ca/empty_file.md) | as expected | S0 FAIL section 2 (between '## 2.' and '## 3.') not found |
