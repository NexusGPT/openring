import os

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "case-model-r4-notes.md")
s = open(p).read()
i = s.index("\n## questions_for_owner")
add = """
## 13. Pin heights, as delivered (09:14 build of out/)

- Lead's ruling b2 (outer pins radial) was not built: radial outer pins put the P1 land centre 1.654 mm from the P2 land centre (r4/radial_pins.log), less than the 1.70 mm land, so the islands cannot both exist without changing the pin board. Reported 09:16.
- Cause of the barrel contact was the model, not the pin: the maker's drawing (P70-6000045R sheet 2) has a flange 1.50 x 0.40 at the board and a 1.06 mm body to 1.85; C5d modelled 1.50 x 1.85. case.py `PIN` and `make_pin` now follow the drawing. With it, the outer pin clears the band from 2.10 mm at US 7 (r4/outer_pin_scan_fine.log: 2.09 gives 0.00009 mm3, 2.10 gives 0.00002 mm3, only the tip; r4/outer_pin_scan_maker_body.log).
- Heights (case.py PIN_H0 2.05 for P2, P3 and PIN_H0_OUT 2.15 for P1, P4, at US 10): working heights per size (r4/pins_out_check18.log, design/wiring/ring-case-contact.csv):

| Size | P1 (CP1 VBUS / VRING) | P2 (CP2 USB_DN / USB_D-) | P3 (CP3 USB_DP / USB_D+) | P4 (CP4 GND / GND) |
|---|---|---|---|---|
| US 7 | 2.139 | 2.118 | 2.118 | 2.139 |
| US 8 | 2.146 | 2.096 | 2.096 | 2.146 |
| US 9 | 2.149 | 2.073 | 2.073 | 2.149 |
| US 10 | 2.150 | 2.050 | 2.050 | 2.150 |
| US 11 | 2.149 | 2.027 | 2.027 | 2.149 |
| US 12 | 2.146 | 2.003 | 2.003 | 2.146 |
| US 13 | 2.142 | 1.980 | 1.980 | 2.142 |

  All inside the maker's 1.90 to 2.20; left over: P2, P3 +-0.08 mm, P1, P4 +-0.05 mm (2.10 body clearance to 2.20), below the lead's +-0.07 target for the outer pins. Tip to pad centre 0.000 to 0.024 mm. Pin against ring at every size: largest common volume 0.000151 mm3 (r4/pins_out_quick.log), no part pair of pins, holder, post, islands, liner, shell intersecting.
- Contact file design/wiring/ring-case-contact.csv: written by case_check test 18 from out/ (header + 28 lines, 28 `yes`); pairing from coordinates: CP1 VBUS / P1 VRING, CP2 USB_DN / P2 USB_D-, CP3 USB_DP / P3 USB_D+, CP4 GND / P4 GND at every size. Ring names: band-interface.md lines 37, 38, 80, 81; case names: the pin board file.
- Broken copies of test 18: two middle pins swapped (CASE_PIN_SWAP=1): r4/broken_pin_swap_check.log `FAIL 18 US 7: CP2 USB_DN under P3 USB_D+ offset 0.001`, `case_check: FAIL, 28 pairs checked, 14 failures, ...`; old heights 2.35 (CASE_PIN_H0 and CASE_PIN_H0_OUT 2.35): r4/broken_pin_high_check.log `FAIL 18 US 7: P1 height 2.339`, `case_check: FAIL, 28 pairs checked, 28 failures, ...`.
- Builder's depth-gauge and shim step: case-architecture.md section 7 (nominal free tip stand-out 1.170 mm for P2, P3 and 1.021 mm for P1, P4, r4/pin_gauge.log; shim 0.025 / 0.05 / 0.10 mm behind an island, or lap the lug face).
- Documents: case-architecture.md lines 60, 104, 123, 219 (two sentences), 256; case-notes.md lines 42 (M4), 58 (A3), 88; case-bom.csv line 16; old and new in r4/edit_pins_docs.log (source file names in r4/edit_srcname.log). check_case_docs: r4/docs_after_pins.log `RESULT PASS (0 findings)`.
- Full check of this model: r4/pins_full_check.log (running at the time of writing; exit code in r4/pins_full_check.done).
"""
s = s[:i] + add + s[i:]
j = s.rindex("\nRESULT: ")
s = s[:j] + "\nRESULT: blocked, the full case check of the 09:14 model with the corrected pin heights (r4/pins_full_check.log) has not ended yet; test 18, the pin collision check and the doc check pass.\n"
open(p, "w").write(s)
print("ok")
