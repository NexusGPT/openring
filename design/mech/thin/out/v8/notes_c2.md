### c.2 Which pairs involve a ribbon

The pair test of check_thin.py (item 1) tests every pair of parts: sub-solid against sub-solid, a finding when the common volume is over 0.001 mm3. A ribbon is the part `band_flex_thumb` (FLEX1) or `band_flex_away` (FLEX2). At 47 parts (US 7, 8, 9) the pairs with a ribbon are 2 x 46 - 1 = 91; at 46 parts (US 10 to 13, no motor window seal) they are 2 x 45 - 1 = 89 (the pair of the two ribbons counted once). Every one of them is inside the `pairs=` count of the last line of the size's log and none printed a COLLISION line (each log ends `check_thin: 0 findings, 0 errors`). The groups asked for, with the check's own lines (section 13 and the older section "least free space"):

- ribbon to motor: `RIBBON-CLEARANCE ... to vibration_motor` and the older line `free space vibration_motor to band_flex_thumb`;
- ribbon to cell and to the protection circuit: `RIBBON-CLEARANCE ... to cell`, `... to cell_protection`;
- ribbon to body: `RIBBON-CLEARANCE ... to outer_body` (channel walls and slot walls; rule 0.10 added in v8);
- ribbon to slot wall, measured on the body at the slot: `band circuit ... slot X ... free to the ends` (rule 0.15, from the old line `ribbon X ... in the slot`);
- ribbon to the joystick parts: `RIBBON-CLEARANCE ... to joystick_frame, joystick_cap, joy_sw_*, joystick_dam`; the head sits on the switch bases (0.0000 by design: older line `switch ...: base to the flat ribbon head`, rule 0.005);
- foot and lands to the board parts above: `RIBBON-CLEARANCE ... to main_board` (board underside) and `band circuit ...: 8 board lands ... least land to foot`. The lands are not parts of the model (the model's main board has no J_BAND lands); the test places the 8 land boxes of band-interface.md section 2 (0.30 x 0.55 x 0.02 at Z 1.430 to 1.450) over the foot and measures them against the foot.

