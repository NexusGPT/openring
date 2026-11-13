# Case notes: rejected choices, open points, questions

Tags as in `case-architecture.md` (DS, LIST, CALC). Arithmetic: `evidence/calc_case.log`.

## Rejected choices and the fact that rejected each

| Rejected | Fact | Source |
|---|---|---|
| ESP32-P4 plus a Wi-Fi companion (for example ESP32-C6-MINI-1) | ESP32-P4 has "USB 2.0 High-Speed OTG" but no Wi-Fi: the word appears only in the trademark notice; it needs a second radio chip, a QFN104 10 x 10 mm package and outside flash. The gain is 2.48 min per recorded hour (3.84 against 6.32 min), because the ring's SPI storage read (2 MB/s) limits high speed anyway | DS case_esp32p4_ds.pdf p.1, p.4; evidence/read_p4.log; CALC |
| ESP32-S3-WROOM-1 | Same chip and the same full-speed USB as the MINI-1; larger module | DS case_esp32s3_ds.pdf p.55; size LIST |
| ESP32-C3-MINI-1 (listed in parts/power.md) | No USB OTG host on the C3 (USB Serial/JTAG only) | LIST, not read in a saved document |
| BQ25180 or BQ24074 as the case charger | Their TI pages list no boost output (parts/power.md 6b); the ring needs 5 V from the case cell | parts/power.md section (6) |
| A 500 mAh case cell (for example DNK LP503035, 5 x 30 x 35 mm) | 500 mAh x 3.7 V = 1.85 Wh gives 2.33 ring charges, not 3; 3 charges need 644 mAh | CALC; DNK product page evidence/html/dnk_503035_text.log |
| DNK682624 (26 x 26 x 6.8 mm) | 275 mAh | DS cell_dnk_DNK682624.pdf |
| DNK652545 (6.5 x 25 x 45 mm, 700 mAh) | 45 mm long: the case would be 5 mm taller than with DNK852338 (40.0 mm with PCM) | DS case_cell_dnk652545.pdf, case_cell_dnk852338.pdf |
| Hall switch DRV5032FA plus a lid magnet for lid detection | The only place for the sensor is the pin board, about 15 mm under the lid; a 4 x 2 mm magnet gives about 1.4 mT there (on-axis estimate, LIST), below the 4.8 mT maximum operate point | DS case_drv5032.pdf p.1; estimate LIST |
| Magnets alone holding the lid | The 4 pins push up with 4 x 90 gf = 360 gf; a printed snap latch carries it with no magnet sizing | DS p3_millmax_0981.pdf p.3 |
| Magnetic pogo connectors (EDAC 686 series, listed in parts/power.md) | No dimension or working-height drawing was readable; the Mill-Max 0981 sheet gives height 5.182, stroke 1.397, mid stroke 0.70 | parts/power.md (3); DS p3_millmax_0981.pdf p.1 |
| Mill-Max 0900-8-15-20-76-14-11-0 or Harwin P70-6000045R instead of Mill-Max 0981 (read later by another helper, design/parts/ui-pass3.md lines 167 and 190) | 0900-8: mid stroke 0.495 mm leaves a +-0.25 mm window against +-0.35 mm for the 0981; P70: 0.39 N at 2.10 mm working height, 1 A. Kept as fallbacks if the 0981's 90 gf (4 pins = 360 gf) proves too high for the lid latch (bench B2); the 0981 has a full drawing read [DS] and is already proven in the model | design/parts/ui-pass3.md; DS p3_millmax_0981.pdf |
| Copying straight to Wi-Fi with no case storage | Copy would wait for Wi-Fi each time; with an 8 GB buffer (U4) the ring is free after the copy and the upload runs later | design choice |

## Open points (a bench test or another helper must close)

| # | Open point | Who |
|---|---|---|
| B1 | The ring's nRF54LM20A high-speed USB device must enumerate at full speed under the ESP32-S3 host. USB 2.0 requires it (LIST); Nordic's USBHS page was not readable. Test on the nRF54LM20 DK with an ESP32-S3 board before layout | bench, Nordic (S2) |
| B2 | Lid pad force: the 1.0 mm silicone pad compressed to 0.7 mm must push the block down with more than 360 gf; latch strength in PA12 | bench |
| B3 | Ring presence by touch (IO4, electrode E1 under 1.0 mm of PA12): reading change with the ring block present, and Deep-sleep wake on it | bench |
| B4 | LED1 green and blue from 3.3 V: VF typ 3.3 V at 20 mA [DS], so at 3.3 V drive the current is only a few mA; check brightness, else drive the anodes from SYS through a transistor | bench |
| B5 | Boost efficiency at 0.1 to 0.3 A (taken as 0.85); the 3.26 charges depend on it | bench, TI (S5) |
| B6 | Load on PMID while charging from USB-C: chosen because PMID equals VBUS through the input FET; TI to confirm | TI (S5) |
| O1 | Pad order on the ring's contact board is not written in the ring files (evidence/pad_order_search.log). The case uses VBUS at Y -3.81, D- at -1.27, D+ at +1.27, GND at +3.81 | ring mechanics helper, owner |
| O2 | Pads assumed flush with the block underside (Z = 0). A recess of up to 0.35 mm still leaves the pins inside the working window (0.349 to 1.048 mm); a deeper recess needs a raised pad seat | ring mechanics helper |
| O3 | Band modelled as a circle touching the block underside at Y = 0, centred on X = 0, 8 mm wide. The slot takes any band inside radius 13.6 mm and X from -4.6 to 4.6 | ring mechanics helper |
| O4 | `design/architecture.md` section 8 says the case reads "over high-speed USB" with 4 min per hour; this case reads at full speed, 6.32 min per recorded hour. Section 8 and the T3 row of section 10 need the change (file owned by the lead) | lead |
| O5 | Requirement C2 says "500 mAh or more: 3 full charges"; by the arithmetic 500 mAh gives 2.33. The case uses 700 mAh (3.26) | owner |
| O6 | Not modelled in 3D: screws (holes are modelled), wires, passives, the lid's opening swing; the check covers the closed state only | next step |
| O7 | Unit prices: none read; the price column of case-bom.csv is empty for every line | buyer |
| O8 | Case firmware update: USB-C data lines go to the charger's adapter detection only; firmware goes over Wi-Fi or the UART test pads | firmware helper |
| O10 | Two files in design/datasheets/ named .pdf are HTML error pages from blocked downloads: case_cell_dnk503035.pdf, case_cell_eemb_lp503035.pdf (evidence/final_listing.log). out/case_section_pins_US5.png is an earlier drawing (cut at X = -12.6 with US 5, band label misplaced) replaced by case_section_band_US5.png | lead, may delete |
| O9 | Stack tolerance on pin compression: pin length ±0.15 mm [DS Mill-Max standard tolerance], board and print tolerances not measured; the window allows ±0.35 mm around 0.70 | bench |

## Outer size

From `out/case_size.txt` (written by case.py): closed case 33.6 x 33.4 x 55.2 mm including hinge and latch tab. What sets it: the cell standing (40.0 mm with PCM) under the block, the US 13 band (outer 26.2 mm) and the block (30 mm). A flat cell under the band gave a larger box in my estimate (not modelled).

## Proof files

- `evidence/run_after_restore.log` and the final run `evidence/run_done_final.log`: case.py then case_check.py, exit 0.
- `evidence/run_fault_test.log`: pin board raised 0.5 mm, case_check.py found 24 failures and exited 1; case.py restored byte for byte (cmp).

## questions_for_owner

1. Transfer at USB full speed takes 6.32 min per recorded hour (63.2 min for a 10-hour day) with one module (ESP32-S3-MINI-1). A two-chip design (ESP32-P4 plus a Wi-Fi chip) takes 3.84 min. Keep the one-module design?
2. Three full ring charges need at least 644 mAh by the arithmetic. Accept the 700 mAh cell and the case size 33.6 x 33.4 x 55.2 mm?
3. Contact order on the ring: VBUS, D-, D+, GND from -Y to +Y. Confirm, or give the ring's order.

RESULT: done, case_check.py exits 0 (594 pairs, 0 failures; it exits 1 on an injected 0.5 mm pin fault) and transfer takes 6.32 min per recorded hour at USB full speed.
