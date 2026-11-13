### P1 per board (Route B: Gerber + drill read-back; field names are those of the results/p1_*.json files)

| board | nets compared (nets) | pads compared (pads) | shorts | opens | missing pads (missing) | refs of its netlist in no fab file | stack-model shorts/opens | route A | P1 |
|---|---|---|---|---|---|---|---|---|---|
| ring | 84 | 359 | 0 | 0 | 0  | BT1, DISP1, RT1 | 0/0 | pads 359, nets 84, joined 0, split 0, coords 362/362 | FAIL |
| case_main | 61 | 272 | 0 | 0 | 0  | BT1 | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| case_pins | 5 | 10 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex1-us7 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex1-us8 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex1-us9 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex1-us10 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex1-us11 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex1-us12 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex1-us13 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex2-us7 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex2-us8 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex2-us9 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex2-us10 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex2-us11 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex2-us12 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex2-us13 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |

### P2 broken copies of the ring board (each exported again with kicad-cli into readback-work/p2/<name>/fab)

| copy | Route B shorts | Route B opens (net) | Route A joined/split | draws read | what the edit was |
|---|---|---|---|---|---|
| control | 0  | 0  | 0 / 0 | 5551 | byte copy, no edit |
| resave | 0  | 0  | 0 / 0 | 5551 | loaded and saved by pcbnew, no edit |
| cut | 0  | 1 {'LCD_SCK': 1} | 0 / 0 | 5550 | one LCD_SCK segment removed |
| join | 1 [['LCD_MOSI', 'LCD_SCK']] | 0  | 0 / 0 | 5552 | one added segment LCD_SCK to LCD_MOSI |

### P3 power paths (R from the pixel mesh of the drawn copper; check = sum of rho L/(w t) on the minimum-resistance track path where the drawn-track graph reached both pads)

| path | from -> to | R mesh (mohm) | R track-sum (mohm) | current | drop (mV) | limit | verdict |
|---|---|---|---|---|---|---|---|
| ring VBAT | J_BAND_B-1 -> U2-D1+U2-D2 | 291.99 | 284.92 | 235mA | 68.62 | REPORT (no written limit) | REPORT |
| ring VBAT | J_BAND_B-1 -> U11-4 | 92.18 | 87.27 | 235mA | 21.66 | REPORT (no written limit) | REPORT |
| ring VBAT | J_BAND_B-1 -> U4-A1 | 310.81 | 299.53 | 235mA | 73.04 | REPORT (no written limit) | REPORT |
| ring VMOT | U11-1 -> J_BAND_A-7 | 205.26 | 170.11 | 175mA | 35.92 | part of the 264 mV sum below | REPORT |
| ring VMOT | U11-1 -> J_BAND_A-7 | 205.26 | 170.11 | 80mA | 16.42 | part of the 264 mV sum below | REPORT |
| ring VBUS | J_BAND_B-4 -> U2-B1+U2-B2 | 206.14 | 188.04 | 15mA | 3.09 | <= 970 mV | PASS |
| ring VBUS | J_BAND_B-4 -> U2-B1+U2-B2 | 206.14 | 188.04 | 100mA | 20.61 | <= 800 mV | PASS |
| ring VBUS (other loads) | J_BAND_B-4 -> U9-4 | 52.45 | 52.01 | 15mA | 0.79 | REPORT (no written limit) | REPORT |
| ring VBUS (other loads) | J_BAND_B-4 -> R1-1 | 162.59 | 152.24 | 15mA | 2.44 | REPORT (no written limit) | REPORT |
| ring VDD_1V8 farthest load | U2-B6 -> TP17-1 | 275.09 | n/a | 200mA | 55.02 | <= 90 mV | PASS |
| ring VDD_SD farthest load | U2-A5 -> C82-1 | 439.70 | 422.49 | 100mA | 43.97 | <= 300 mV | PASS |
| ring VDD_SD farthest load | U2-A5 -> C82-1 | 439.70 | 422.49 | 25mA | 10.99 | <= 300 mV | PASS |

#### band circuits, every size (mohm and mV; motor lines at 175 and 80 mA, cell lines at 227.5 mA)

| size | VMOT mohm | VMOT mV 175 / 80 | GND lands 6+8 mohm | GND mV 175 / 80 | GND land 6 only mV 175 | cell VBAT mohm | VBAT mV | cell GND 2+7 mohm | GND mV | GND land 2 only mV |
|---|---|---|---|---|---|---|---|---|---|---|
| US 7 | 38.77 | 6.78 / 3.10 | 55.06 | 9.63 / 4.40 | 9.81 | 46.78 | 10.64 | 50.44 | 11.47 | 12.19 |
| US 8 | 39.16 | 6.85 / 3.13 | 55.42 | 9.70 / 4.43 | 9.87 | 45.98 | 10.46 | 49.64 | 11.29 | 12.01 |
| US 9 | 39.27 | 6.87 / 3.14 | 55.56 | 9.72 / 4.44 | 9.90 | 45.27 | 10.30 | 48.92 | 11.13 | 11.84 |
| US 10 | 42.89 | 7.51 / 3.43 | 59.15 | 10.35 / 4.73 | 10.53 | 46.09 | 10.49 | 49.75 | 11.32 | 12.03 |
| US 11 | 45.00 | 7.88 / 3.60 | 61.29 | 10.73 / 4.90 | 10.90 | 47.71 | 10.85 | 51.36 | 11.69 | 12.40 |
| US 12 | 45.51 | 7.96 / 3.64 | 61.76 | 10.81 / 4.94 | 10.98 | 49.36 | 11.23 | 53.01 | 12.06 | 12.77 |
| US 13 | 47.33 | 8.28 / 3.79 | 63.59 | 11.13 / 5.09 | 11.30 | 51.04 | 11.61 | 54.69 | 12.44 | 13.16 |

Case: VRING main 6.53 mohm (2.61 mV at 0.400 A), pins board 0.44 mohm (0.17 mV); BAT 4.89 mohm (1.71 mV at 0.350 A); GND 1.22 mohm (0.43 mV) at the 50 um raster; VRING at the 50 um raster 6.70 mohm (resolution check).

### P4 and P5 (ring)

| id | item | figure | limit | verdict | results field |
|---|---|---|---|---|---|
| P2.control | control copy (byte copy and re-saved copy) | shorts/opens/missing(local) 0/0/0; refs in no fab file ['BT1', 'DISP1', 'RT1'] | passes P1 | FAIL | p1_ring_p2_control.json, p1_ring_p2_resave.json |
| P2.cut | cut copy | opens 1 {'LCD_SCK': 1}, shorts 0 | exactly one open on LCD_SCK, nothing else | PASS | p1_ring_p2_cut.json |
| P2.join | joined copy | shorts 1 [['LCD_MOSI', 'LCD_SCK']], opens 0 | exactly one short LCD_SCK-LCD_MOSI, nothing else | PASS | p1_ring_p2_join.json |
| P2.routeA | Route A on cut and join copies (expected: not detected) | cut joined/split 0/0, join 0/0 | REPORT (written expectation: not detected) | REPORT | routeA fields |
| P3.VMOT.sum.175mA | VMOT total at 175mA: ring VMOT 35.92 + band US13 VMOT 8.28 + band US13 GND (lands 6+8) 11.13 | 55.33 mV | <= 264 mV (2.964 - 2.7) | PASS | p3_ring.json VMOT, p3_band.json us13 |
| P3.VMOT.sum.80mA | VMOT total at 80mA: ring VMOT 16.42 + band US13 VMOT 3.79 + band US13 GND (lands 6+8) 5.09 | 25.30 mV | <= 264 mV (2.964 - 2.7) | PASS | p3_ring.json VMOT, p3_band.json us13 |
| P3.ring.VBUS.15mA | ring VBUS land to U2 B1+B2 at 15mA | 3.09 mV | <= 970 mV | PASS | p3_ring.json VBUS |
| P3.ring.VBUS.100mA | ring VBUS land to U2 B1+B2 at 100mA | 20.61 mV | <= 800 mV | PASS | p3_ring.json VBUS |
| P3.ring.VDD_1V8.200mA | ring VDD_1V8 source to farthest pad TP17-1 at 200mA | 55.02 mV | <= 90 mV | PASS | p3_ring.json VDD_1V8 |
| P3.ring.VDD_SD.100mA | ring VDD_SD source to farthest pad C82-1 at 100mA | 43.97 mV | <= 300 mV | PASS | p3_ring.json VDD_SD |
| P3.ring.VDD_SD.25mA | ring VDD_SD source to farthest pad C82-1 at 25mA | 10.99 mV | <= 300 mV | PASS | p3_ring.json VDD_SD |
| P3.VMOT.sum.us7.175mA | VMOT total US 7 at 175mA (ring VMOT + band VMOT + band GND) | 52.34 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us7.80mA | VMOT total US 7 at 80mA (ring VMOT + band VMOT + band GND) | 23.93 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us8.175mA | VMOT total US 8 at 175mA (ring VMOT + band VMOT + band GND) | 52.47 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us8.80mA | VMOT total US 8 at 80mA (ring VMOT + band VMOT + band GND) | 23.99 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us9.175mA | VMOT total US 9 at 175mA (ring VMOT + band VMOT + band GND) | 52.52 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us9.80mA | VMOT total US 9 at 80mA (ring VMOT + band VMOT + band GND) | 24.01 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us10.175mA | VMOT total US 10 at 175mA (ring VMOT + band VMOT + band GND) | 53.78 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us10.80mA | VMOT total US 10 at 80mA (ring VMOT + band VMOT + band GND) | 24.58 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us11.175mA | VMOT total US 11 at 175mA (ring VMOT + band VMOT + band GND) | 54.52 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us11.80mA | VMOT total US 11 at 80mA (ring VMOT + band VMOT + band GND) | 24.92 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us12.175mA | VMOT total US 12 at 175mA (ring VMOT + band VMOT + band GND) | 54.69 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us12.80mA | VMOT total US 12 at 80mA (ring VMOT + band VMOT + band GND) | 25.00 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.band.us13.vmot | band US13 VMOT at 175mA | 8.28 mV (stated 8.7 mV) | <= 9.57 mV (1.10 x stated, band-interface.md lines 132/133) | PASS | p3_band.json us13.vmot |
| P3.band.us13.gnd6 | band US13 motor GND (land 6 only, the stricter) at 175mA | 11.30 mV (stated 12.9 mV) | <= 14.19 mV (1.10 x stated, band-interface.md lines 132/133) | PASS | p3_band.json us13.gnd6 |
| P3.band.us13.vbat | band US13 cell VBAT at 227.5mA | 11.61 mV (stated 11.0 mV) | <= 12.10 mV (1.10 x stated, band-interface.md lines 132/133) | PASS | p3_band.json us13.vbat |
| P3.band.us13.cell_gnd2 | band US13 cell GND (land 2 only, the stricter) at 227.5mA | 13.16 mV (stated 12.5 mV) | <= 13.75 mV (1.10 x stated, band-interface.md lines 132/133) | PASS | p3_band.json us13.cell_gnd2 |
| P3.case.VRING | case VRING U5 OUT -> W1 (case_main) 2.61 mV + WP1 -> P1 (case_pins) 0.17 mV at 0.400 A | 2.79 mV | <= 901 mV | PASS | p3_case.json vring_main, vring_pins |
| P3.case.BAT | case BAT U2 13+14 -> W5 at 0.350 A | 1.71 mV | no written limit | REPORT | p3_case.json bat |
| P3.case.GND | case GND U2 25 -> W6 at 0.350 A (50 um raster) | 0.43 mV | no written limit | REPORT | p3_case.json gnd_50um |
| P4.1 | antenna feed Z0 (width 0.120 mm, Hammerstad-Jensen + Wheeler, er 4.1) | 49.31 ohm | 45 to 55 ohm | PASS | p4p5.json P4_1.Z0 |
| P4.2 | antenna L1 clearance to other-net copper (whole line; excluding 1.0 mm at U1 ball C1: 0.1950 mm) | 0.1250 mm at [102.283, -99.548] (copper of DECA) | >= 0.200 mm | FAIL | p4p5.json P4_2.min_clear_mm |
| P4.3 | antenna reference: share of line pixels over L2 GND (L2 other-net copper under the line: 0 px) | 96.647 percent (3101 px uncovered) | 100 percent and no other-net L2 copper | FAIL | p4p5.json P4_3 |
| P4.4 | USB Zdiff at the min / median / modal drawn gap (0.0778 / 0.1387 / 0.175 mm), width 0.100 mm | 92.10 / 101.90 / 104.70 ohm | 81 to 99 ohm at all three (stricter reading, stated) | FAIL | p4p5.json P4_4 |
| P4.usb.other | USB pair (both legs) nearest other-net L1 copper | 0.0900 mm (copper of (no netlist pad in that copper)) | plan: 0.200 mm class gap (d.2 "0.200 to other copper") REPORT | REPORT | p4p5.json P4_usb_other |
| P4.usb.ref | USB pair reference L2 GND coverage | 16.877 percent (96705 px uncovered; 19144 px of other-net L2 copper under the pair) | plan d.2: reference L2 solid; REPORT | REPORT | p4p5.json P4_3u |
| P4.5 | USB leg mismatch (shortest paths 14.075 / 14.075 mm; total drawn 14.523 / 14.493 mm, mismatch 0.030) | 0.000 mm | <= 0.10 mm | PASS | p4p5.json P4_5 |
| P4.len | antenna line length, sum of legs | 16.125 mm | plan 16.4 mm, no tolerance written | REPORT | p4p5.json P4_len |
| P4.near.L1 | nearest other-net copper to the antenna line on L1 | 0.1250 mm (copper of DECA) | REPORT | REPORT | p4p5.json P4_per_layer |
| P4.near.L2 | nearest other-net copper to the antenna line on L2 | 0.0000 mm (copper of GND) | REPORT | REPORT | p4p5.json P4_per_layer |
| P4.near.L3 | nearest other-net copper to the antenna line on L3 | 0.0000 mm (copper of SWDIO) | REPORT | REPORT | p4p5.json P4_per_layer |
| P4.near.L4 | nearest other-net copper to the antenna line on L4 | 0.0000 mm (copper of GND) | REPORT | REPORT | p4p5.json P4_per_layer |
| P5.XL1.len | XL1 length (shortest drawn path pad to pad; all drawn copper 8.897 mm) | 9.697 mm | <= 9.0 mm | FAIL | p4p5.json P5.XL1 |
| P5.XL2.len | XL2 length (shortest drawn path pad to pad; all drawn copper 7.751 mm) | 7.391 mm | <= 9.0 mm | PASS | p4p5.json P5.XL2 |
| P5.XC1.len | XC1 length (shortest drawn path pad to pad; all drawn copper 4.956 mm) | 4.956 mm | <= 6.0 mm | PASS | p4p5.json P5.XC1 |
| P5.XC2.len | XC2 length (shortest drawn path pad to pad; all drawn copper 4.926 mm) | 4.926 mm | <= 6.0 mm | PASS | p4p5.json P5.XC2 |
| P5.XC.match | |XC1 - XC2| | 0.030 mm | <= 0.5 mm | PASS | p4p5.json P5 |
| P5.XL1.gap | XL1 nearest other-net copper on its layers (L2 0.0873) | 0.0873 mm on L2 (copper of U1_VBUS) | >= 0.20 mm | FAIL | p4p5.json P5.XL1.clear |
| P5.XL2.gap | XL2 nearest other-net copper on its layers (L1 0.0990; L2 0.0919; L4 0.0939) | 0.0919 mm on L2 (copper of PMIC_SDA) | >= 0.20 mm | FAIL | p4p5.json P5.XL2.clear |
| P5.XC1.gap | XC1 nearest other-net copper on its layers (L3 0.1050) | 0.1050 mm on L3 (copper of SPARE_P3_04) | >= 0.20 mm | FAIL | p4p5.json P5.XC1.clear |
| P5.XC2.gap | XC2 nearest other-net copper on its layers (L3 0.1030) | 0.1030 mm on L3 (copper of SPARE_P3_03) | >= 0.20 mm | FAIL | p4p5.json P5.XC2.clear |

Verdict counts: {'FAIL': 18, 'PASS': 28, 'REPORT': 25}; per pass line: {'P1': {'FAIL': 9, 'PASS': 8}, 'P2': {'FAIL': 1, 'PASS': 2, 'REPORT': 1}, 'P3': {'REPORT': 17, 'PASS': 12}, 'P4': {'PASS': 2, 'FAIL': 3, 'REPORT': 7}, 'P5': {'FAIL': 5, 'PASS': 4}}
