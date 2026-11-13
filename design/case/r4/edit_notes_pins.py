import os

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "case-model-r4-notes.md")
s = open(p).read()
i = s.index("\n## questions_for_owner")
add = """
## 12. Added work after 07:19 (pin working height, contact file, transfer figures)

- Pin height (lead 07:19, maker range of P70-6000045R 1.90 to 2.20 mm, design/case/pin-travel.md): case.py now has PIN_H_MIN, PIN_H_MAX = 1.90, 2.20 and PIN_H0 = 2.05 (C5d 2.35); new check test 18 prints "pin working height inside 1.90 to 2.20" and "each pin over its pad, nets paired" per size and pin and writes the contact file. Trial build r4/pins_try (r4/pins_try_check.log, `case_check: PASS, 28 pairs checked, 0 failures, ... (only tests [18])`): heights P2, P3 1.980 (US 13) to 2.118 (US 7), P1, P4 2.039 to 2.042; pairing CP1 VBUS / P1 VRING, CP2 USB_DN / P2 USB_D-, CP3 USB_DP / P3 USB_D+, CP4 GND / P4 GND at every size, tip to pad 0.000 to 0.024 mm.
- Design error found: at those heights the OUTER pins' barrels (1.50 x 1.85) cut the band at every size, 0.0056 (US 13) to 0.0288 mm3 (US 7) (r4/quick_pins.log); scan r4/outer_pin_scan.log: at US 7 the outer pin clears the 0.001 mm3 limit only from 2.18 mm (0.00085), touch-free from 2.25. The outer pads sit about 22 degrees round the bore, so the band face is tilted under the barrel edge. First choice (a) therefore holds for P2, P3 only. Reported to the lead (two messages about 09:05 and 09:07) with options b1 (P70-7000045 on the outer pins, barrel length not in the saved documents) and b2 (outer wing islands turned square to the band); waiting for the ruling. out/ and design/wiring/ring-case-contact.csv are NOT written with the new heights.
- Transfer figures (lead 07:19): case-architecture.md section 1 now follows design/firmware.md line 718 (234.0 MB, 192.4 s = 3.21 min per recorded hour) and requirements.md row P2 (4.3 to 7.8 hours: 13.8 to 25.0 min); 6 lines changed, old and new in r4/edit_transfer.log; check_case_docs after it: r4/docs_after_transfer.log `RESULT PASS (0 findings)`.
"""
s = s[:i] + add + s[i:]
j = s.rindex("\nRESULT: ")
s = s[:j] + "\nRESULT: blocked, the outer spring pins cannot work inside the maker's 1.90 to 2.20 mm without their barrels touching the band (needs the lead's choice of b1 or b2); the board work of round 4 is done and passes.\n"
open(p, "w").write(s)
print("ok")
