Case design C1 is done: the four deliverables exist, the done command exits 0, and every line of case-bom.csv has a maker part number or an open_action.

**Central choice: ESP32-S3-MINI-1-N8**, one module with Wi-Fi and a USB host (full speed only, DS p.55-56). ESP32-P4 has high-speed USB but no Wi-Fi in the chip, so it needs a second radio chip. With it, a recorded hour takes 3.84 min instead of 6.32, because the ring's SPI storage (2 MB/s) is the limit either way.
- Transfer time per recorded hour: at 12 Mbit/s, 460.8 MB / 1.5 MB/s = 5.12 min. That is a bound. The bulk ceiling is 19 x 64 B per ms = 1.216 MB/s, so **6.32 min**. A 10-hour day takes 63.2 min.

**Other parts:** BQ25895 (charger, power path, 4.998 V boost on PMID, battery ADC), TPS2553 (ring VBUS, 401 mA limit), TPS63802 (3.3 V), ZDSD64GLQEAG-R (8 GB buffer), TPD4E05U06 (ESD on the exposed pins), DNK852338 cell, USB4105-GF-A, 4 Mill-Max 0981 pins, one RGB LED APTF1616SEEZGQBDC. Ring presence uses a touch electrode plus USB attach.

**Findings for the lead and owner:**
1. 500 mAh gives 2.33 ring charges, not 3. The minimum is 644 mAh, so the case uses 700 mAh (3.26 charges, boost efficiency 0.85 assumed).
2. architecture.md section 8 says high-speed USB at 4 min per hour. The case reads at full speed, 6.32 min. Section 8 and the T3 row of section 10 need changing; that file is not mine to edit.
3. The ring's pad order is not written in any ring file. The case uses VBUS, D-, D+, GND from -Y to +Y.
4. Full-speed fallback of the nRF54LM20A USBHS is unverified: Nordic's page could not be read. It is bench item B1.

**Model:** the outer size is 33.6 x 33.4 x 55.2 mm. Pins are compressed 0.700 mm (window 0.349 to 1.048) for both US 5 and US 13. case_check.py checked 594 pairs with 0 failures. Raising the pin board 0.5 mm made it exit 1 with 24 failures, then case.py was restored (cmp identical).

**Not done:**
- Passives, inductors, screws and wires have no maker part numbers (they have an open_action).
- No prices were read.
- The 90-minute ring charge depends on the ring's charger setting.
- The lid swing, screws and wires are not modelled.

**Proof files:**
- design/case/evidence/run_done_final.log, last line: `mar. 10 nov. 2026 15:28:29 CET` (the line before it: `exit 0`)
- design/case/evidence/run_fault_test.log, last line: `52:PINB_TOP = -(PIN["free_h"] - PIN["mid"])  # mid stroke when the block rests on the seat`
- case-notes.md, last line: `RESULT: done, case_check.py exits 0 (594 pairs, 0 failures; it exits 1 on an injected 0.5 mm pin fault) and transfer takes 6.32 min per recorded hour at USB full speed.`

Files, all in design/case/:
- case-architecture.md
- case-bom.csv
- case.py
- case_check.py
- case-notes.md
- CHECKLIST.md
- out/ (STEP, STL, PNG files)
- evidence/

New datasheets are design/datasheets/case_*.pdf. Two of them are HTML error pages (notes O10).

RESULT: done, commit none (lead commits), case_check.py exit 0
