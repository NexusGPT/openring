# Ring charging case: architecture (version C1)

Built against `design/architecture.md` version A1 and `requirements.md` section 2.7.
Evidence tags: **DS** = read in the maker's document (file in `design/datasheets/`, text copies in `design/case/evidence/txt/`); **LIST** = listing, search text, a standard not read here, or my assumption; **CALC** = arithmetic in `design/case/evidence/calc_case.py`, output `design/case/evidence/calc_case.log`.

Axes as on the ring: X along the finger (block length 30 mm), Y across (20 mm), Z up. Case origin: centre of the seat plane, which is where the ring block's underside rests.

## 1. Central choice: USB host plus Wi-Fi in one part

| Candidate | USB host | Wi-Fi | Fact that decides | Verdict |
|---|---|---|---|---|
| Espressif ESP32-S3-MINI-1-N8 (module) | "USB 2.0 OTG Full-Speed Interface", "FS and LS data rates", host mode with 8 channels, Bulk supported [DS case_esp32s3_ds.pdf p.55-56] | 802.11b/g/n, "802.11n up to 150 Mbps" [DS case_esp32s3_mini1.pdf p.1] | One module, 15.4 x 20.5 x 2.4 mm [DS mini1 Table 1-1]; SD/MMC host, 4-bit, up to 80 MHz [DS esp32s3_ds p.57]; 3.0 to 3.6 V supply, 0.5 A [DS mini1 Table 6-2] | **Chosen** |
| Espressif ESP32-S3-WROOM-1 | same chip, full speed only | yes | Larger module (not read: LIST); no gain over MINI-1 | rejected, size |
| Espressif ESP32-P4 + ESP32-C6 module | "USB 2.0 High-Speed OTG" [DS case_esp32p4_ds.pdf p.4] | **none in the chip**: "Wi-Fi" appears only in the trademark notice of the 10,450-line text [DS, evidence/read_p4.log] | Needs a second chip for Wi-Fi, QFN104 10 x 10 mm [DS p4 p.1], external flash; saves 2.48 min per recorded hour only | rejected (see notes) |

**Transfer time, stated plainly [CALC, evidence/calc_case.log]:**
- One recorded hour = 16,000 x 2 bytes x 4 channels x 3,600 s = **460.8 MB**.
- At the full-speed line rate of 12 Mbit/s (1.500 MB/s): 460.8 / 1.500 = 307.2 s = **5.12 min**. This is a bound the bus never reaches.
- Full-speed bulk ceiling: 19 packets x 64 bytes per 1 ms frame = 1.216 MB/s (USB 2.0 figure, LIST). 460.8 / 1.216 = 378.9 s = **6.32 min per recorded hour. This is the planning figure for the chosen part.** A 10-hour day: 63.2 min. A full ring (17 hours): 107.4 min.
- High speed through ESP32-P4: the ring's storage read over SPI (2 MB/s, architecture.md section 8) is the limit: 460.8 / 2.0 = 230.4 s = 3.84 min per recorded hour. The gain is 2.48 min per recorded hour.
- In the 90 minutes a ring charge takes, the case copies 14.25 recorded hours.
- Condition: the ring's nRF54LM20A must run its high-speed USB device at full speed when the host does not answer the high-speed handshake. USB 2.0 requires this of every high-speed device (LIST). Nordic's USBHS page was not readable (`design/parts/mcu.md` line 71). Bench item B1.

## 2. Block diagram

```
 USB-C (J1) --VBUS 5 V--> [BQ25895 U2  charger + power path + boost] --BAT--> [cell 700 mAh with PCM, BT1]
   |  CC1, CC2: 5.1 k to GND (R1, R2), sensed by U1 ADC          |  SYS 3.0-4.4 V
   |  D+, D-  : to U2 D+/D- (adapter detect only)                 +--> [TPS63802 U3 buck-boost] --3V3--> U1, U4, LED1
   |                                                              |
   |                             PMID 5.0 V (USB in) / 4.998 V (boost) --> [TPS2553 U5 switch, 401 mA limit] --VRING-->
   |                                                                                                           |
 [ESP32-S3-MINI-1-N8 U1] --USB host D+/D- (IO20/IO19)--> [TPD4E05U06 U6 ESD] -------------------------------+  |
   |-- SD 4-bit --> [ZDSD64GLQEAG-R U4, 8 GB buffer]                                                          v  v
   |-- I2C, INT, OTG, CE --> U2                                         4 spring pins P1-P4 (Mill-Max 0981) on pin board
   |-- EN, FAULT --> U5 ; VRING sense (divider)                            P1 VBUS  P2 D-  P3 D+  P4 GND
   |-- TOUCH4 --> copper electrode under the seat (ring presence)               |
   |-- 3 GPIO --> RGB LED1 behind the light window                       ring pads (X = -12.6, Y = -3.81, -1.27, +1.27, +3.81)
   +-- Wi-Fi 2.4 GHz (module antenna) --> upload
```

## 3. Fixed parts, one per function

| Ref | Function | Maker, part number | Key facts | Tag |
|---|---|---|---|---|
| U1 | Main chip: USB host, Wi-Fi, SD host, touch input | Espressif ESP32-S3-MINI-1-N8 | 8 MB flash, no PSRAM, 15.4 x 20.5 x 2.4 mm [Table 1-1]; 3.0-3.6 V [Table 6-2]; Wi-Fi TX peak 355 mA at 802.11b 20.5 dBm, RX 95 mA [Table 6-4]; Deep-sleep with ULP sensor-monitored pattern 18 µA typ [Table 6-7 p.30] | DS |
| U2 | Case cell charger, power path, 5 V boost, battery voltage ADC | TI BQ25895RTWR (BQ25895, RTW WQFN-24 4 x 4 mm) | Input 3.9-14 V; boost 4.55-5.51 V in 64 mV steps, default 5.126 V, up to 3.1 A; boost output on PMID; boost needs "no input source detected at VBUS"; ADC battery range 2.304-4.848 V, 20 mV steps; ILIM pin; inductor 1 µH [DS case_bq25895.pdf p.1, Table 6-1, p.10-11, section 9.2.2] | DS (order suffix RTWR: LIST) |
| U3 | 3.3 V rail from SYS | TI TPS63802DLAR | Buck-boost, input 1.3-5.5 V, 2 A at VO 3.3 V, 11 µA IQ, VFB 0.5 V, R2 at most 100 k [DS case_tps63802.pdf p.1, p.19] | DS |
| U4 | Recording buffer, 8 GB | Zetta ZDSD64GLQEAG-R | 64 Gb, LGA8x2 9 x 10 mm, SD3.0, 1/4-bit, speed class 10 supported, 3.3 V [DS sdnand_zetta_family_atta.pdf p.3] | DS |
| U5 | Ring VBUS switch with current limit | TI TPS2553DBVR | SOT-23-6, EN active high, 2.5-6.5 V, 85 mΩ, adjustable 75-1700 mA, reverse-voltage protection, FAULT open drain; IOSmin = 25230 / RILIM^1.016 [DS case_tps2553.pdf p.1, Figure 5-1, section 9.2.1.2] | DS (DBVR suffix: LIST) |
| U6 | ESD on the exposed pins D+, D-, VBUS | TI TPD4E05U06DQAR | 4 channels, 0.42-0.5 pF, IEC 61000-4-2 ±12 kV contact, breakdown 6.5 V min, USON-10 [DS case_tpd4e05u06.pdf p.1] | DS |
| BT1 | Case cell | DNK Power DNK852338 (LP852338) | 700 mAh, 3.7 V, 2.59 Wh, charge 4.2 V, max charge 0.5C, PCM over-charge 4.275 V, over-discharge 2.5 V, 40.0 x 23 x 8.5 mm with PCM, 11.7 g [DS case_cell_dnk852338.pdf] | DS |
| J1 | USB-C receptacle | GCT USB4105-GF-A | 8.94 x 7.35 x 3.31 mm top mount, VBUS 5 A, 20,000 cycles, CC1 A5, CC2 B5 [DS case_usb4105.pdf drawing rev B4] | DS |
| P1-P4 | Spring pins | Mill-Max 0981-0-15-20-87-14-11-0 | SMT, initial height 5.182 mm, stroke 1.397 mm, mid stroke 0.70 mm, plunger 1.06 mm, flange 2.11 mm, 90 gf, 20 mΩ max, 100,000 cycles at mid stroke [DS p3_millmax_0981.pdf p.1, p.3] | DS |
| LED1 | One light, RGB | Kingbright APTF1616SEEZGQBDC | 1.6 x 1.6 x 0.7 mm; VF at 20 mA: red 2.0 typ, green 3.3 typ, blue 3.3 typ [DS case_kb_aptf1616.pdf p.1-2] | DS |
| E1 | Ring presence | copper electrode 6 x 3 mm on the pin board, read by U1 TOUCH4 (IO4) | no extra part; confirmed by USB attach | CALC / bench B3 |
| R1, R2 | CC pull-downs | 5.1 kΩ 1 % 0402 | USB-C sink | LIST |
| H1 | Lid hold | printed hinge + 1.0 mm steel pin + printed snap latch; silicone pad presses the ring on the pins | | LIST |

The full list with passives: `case-bom.csv`.

## 4. Power tree [values from section 3 rows; CALC lines from calc_case.log]

| Rail | Source | Voltage | Load |
|---|---|---|---|
| VBUS_IN | USB-C J1 | 5.0 V (USB) | U2 VBUS, input limit 500 mA by register (USB default), 1.5 A when CC shows a 1.5 A source |
| BAT | BT1 | 2.5 (PCM cut) / 3.0 (firmware stop) to 4.2 V | U2 BAT |
| SYS | U2 | 3.0-4.4 V on battery (BAT minus BATFET); with USB in, held above the minimum system voltage, default 3.5 V [DS section 8] | U3, VRING divider |
| PMID | U2 | 5.0 V from USB when plugged; 4.998 V boost (BOOSTV code 7 = 4.55 + 0.064 x 7) when on battery | U5 IN |
| VRING | U5 OUT | same as PMID minus 85 mΩ x I; limit 401 mA min (RILIM 59.0 kΩ) | pin P1 to ring VBUS |
| 3V3 | U3 | 3.300 V (R1 560 kΩ, R2 100 kΩ) | U1 (355 mA peak), U4, LED1, pull-ups |
| REGN | U2 internal | for TS divider (RT1 5.21 k, RT2 29.87 k, 103AT NTC) [DS section 8] | |

Ring charge: the case supplies at least 401 mA at 4.998 V, about 2.0 W. The ring's charger draws about 135 mA x 4.40 V = 0.59 W at 1C. The case does not set the ring's 90-minute charge time; the ring's charger setting does (ring side, unchanged).

Cell sizing [CALC]: one ring charge takes 0.520 Wh in the ring cell (135 mAh x 3.85 V, nominal voltage of a 4.40 V cell: LIST). The ring's charger is linear: 3.85 / 4.998 = 0.770. Boost efficiency taken as 0.85 at light load (datasheet gives 93 % at 1 A). Case energy per ring charge = 0.794 Wh; 3 charges = 2.381 Wh. A 500 mAh cell gives 2.33 charges and does not meet C2. Minimum 644 mAh. Chosen 700 mAh: 3.26 charges.

Cell current: on battery the case keeps Wi-Fi off while VRING is on (boost plus ring is about 0.35 A from the cell; Wi-Fi peak adds about 0.38 A; the cell allows 1C = 700 mA continuous).

## 5. Sequence, step by step

1. Ring dropped into the seat, lid closed: the snap latch holds the lid; the silicone pad presses the block down until it rests on the seat; each spring pin is compressed 0.70 mm (mid stroke).
2. U1 sleeps in Deep-sleep with the touch channel IO4 monitored. The ring block over electrode E1 raises the touch reading above the stored empty value: U1 wakes.
3. U1 reads the USB-C state from CC1/CC2 (ADC). No source: U1 sets the OTG pin high and the OTG_CONFIG bit to 1 [DS bq25895 section 8, "OTG pin HIGH and OTG_CONFIG bit =1"], BOOSTV code 7; with a source: no boost, PMID follows USB VBUS.
4. U1 sets U5 EN high: VRING rises at P1. U1 watches VRING sense (IO5) and FAULT (IO16). FAULT low or VRING below 4.5 V after 50 ms: EN low, light red blink (short or wrong object).
5. Ring's charger starts on VBUS. The ring's USB device pulls D+ up: U1, as USB host, sees the attach and enumerates (full speed). No attach within 3 s: EN low, light amber blink 3 times ("turn the ring", the pads are at the other end), back to sleep.
6. U1 asks the ring for its file list and copies new recordings to U4 (SD 4-bit). Light: blue breathing. Speed 1.216 MB/s at most: 6.32 min per recorded hour.
7. After each file: U1 checks the file length and checksum against the ring's list, then tells the ring the file is safe; the ring may delete it.
8. Charging continues while VRING is on. The ring reports its charge state over USB. At full: EN low, OTG off. Light: green steady 10 s, then off.
9. Upload: when Wi-Fi is known and either USB-C is plugged or the ring charge is done, U1 uploads files from U4 over Wi-Fi, then deletes them from U4 after the server confirms. Light: blue slow blink.
10. Case charging: USB-C plugged: BQ25895 charges BT1 at 350 mA (0.5C), input limit from the CC reading. Light: amber steady while charging the case only.
11. Case low (BATV below 3.40 V): no boost, red blink every 5 s while the ring sits in the case.
12. Lid opened and ring lifted: touch reading falls, USB detach: EN low, OTG off, U1 back to Deep-sleep.

## 6. Pin plan of U1 (ESP32-S3-MINI-1-N8, pin numbers from Table 3-1 [DS p.11-12])

| Module pin | Name | Net | Notes |
|---|---|---|---|
| 1, 2, 42, 43, 46-65 | GND | GND | |
| 3 | 3V3 | 3V3 | 10 µF + 0.1 µF at the pin |
| 4 | IO0 | BOOT test pad | strapping pin, 10 kΩ to 3V3, pad to GND for download |
| 5 | IO1 | CC1_SENSE | ADC1_CH0, 100 kΩ series from J1 A5 |
| 6 | IO2 | CC2_SENSE | ADC1_CH1, 100 kΩ series from J1 B5 |
| 7 | IO3 | not connected | left open (chip strapping use not read: LIST) |
| 8 | IO4 | RING_TOUCH | TOUCH4, to electrode E1 on the pin board |
| 9 | IO5 | VRING_SENSE | ADC1_CH4, divider 100 kΩ / 47 kΩ from VRING (5.0 V -> 1.60 V) |
| 10 | IO6 | CHG_OTG | to U2 OTG (pin 8) |
| 11 | IO7 | CHG_INT_N | from U2 INT (pin 7), 10 kΩ to 3V3 |
| 12 | IO8 | I2C_SDA | to U2 SDA (pin 6), 10 kΩ to 3V3 |
| 13 | IO9 | SD_D3 | U4 |
| 14 | IO10 | SD_D2 | U4 |
| 15 | IO11 | SD_CMD | U4, 10 kΩ to 3V3 |
| 16 | IO12 | SD_CLK | U4, 22 Ω series |
| 17 | IO13 | SD_D0 | U4, 10 kΩ to 3V3 |
| 18 | IO14 | SD_D1 | U4, 10 kΩ to 3V3 |
| 19 | IO15 | VRING_EN | to U5 EN (pin 4), 100 kΩ to GND |
| 20 | IO16 | VRING_FAULT_N | from U5 FAULT (pin 2), 10 kΩ to 3V3 |
| 21 | IO17 | I2C_SCL | to U2 SCL (pin 5), 10 kΩ to 3V3 |
| 22 | IO18 | CHG_CE_N | to U2 CE (pin 9), 10 kΩ to GND (charging on by default) |
| 23 | IO19 | USB_D- | USB_D- of the internal PHY, through U6 to P2 |
| 24 | IO20 | USB_D+ | USB_D+ of the internal PHY, through U6 to P3 |
| 25 | IO21 | LED_R | 470 Ω to LED1 red anode |
| 26 | IO26 | not connected | |
| 27 | IO47 | LED_G | 150 Ω to LED1 green anode (bench B4) |
| 30 | IO48 | LED_B | 150 Ω to LED1 blue anode (bench B4) |
| 28, 29, 31-37 | IO33, IO34, IO35, IO36, IO37, IO38, IO39, IO40, IO41 | spare to test pads | |
| 38 | IO42 | spare test pad | |
| 39 | TXD0 | UART test pad | programming and log |
| 40 | RXD0 | UART test pad | |
| 41 | IO45 | not connected | left open (chip strapping use not read: LIST) |
| 44 | IO46 | not connected | strapping pin [DS mini1 "Strapping pin: GPIO0 and GPIO46"] |
| 45 | EN | EN | 10 kΩ to 3V3, 1 µF to GND, test pad; never floating [DS Table 3-1] |

Other pins: U2 STAT (pin 4) not used (status read over I2C), 10 kΩ to 3V3; U2 DSEL (pin 24) not connected; U2 QON (pin 12) to a test pad; U2 D+/D- (pins 2, 3) to J1 A6/B6 and A7/B7 for adapter detection; U2 ILIM (pin 10): 260 Ω to GND gives 355 / 260 = 1.37 A typ cap [DS KILIM 320-390], register sets the working limit.

Spring pin order along Y on the pin board (case side), matching the ring pads: P1 VBUS at Y = -3.81, P2 D- at -1.27, P3 D+ at +1.27, P4 GND at +3.81. The ring's pad order is not written in the ring files (search saved in evidence/pad_order_search.log); this order is a proposal to align with the ring's contact board (question 1 in case-notes.md).

## 7. Mechanical layout (built in case.py, checked by case_check.py)

- Ring seat: pocket 30.6 x 20.6 mm, 10.2 mm deep (block 9.5 mm plus 0.7 mm compressed silicone pad). The block sits flat on the 1.0 mm seat floor. A slot 2.4 x 10.4 mm in the seat floor at X = -12.6 lets the 4 plungers through.
- Band slot under the seat: 9.2 mm wide in X (band 8 mm plus 0.6 mm each side), round bottom of radius 13.6 mm, holds the US 13 band (outer 26.2 mm); smaller bands hang higher in the same slot. The block, not the band, sets the height, so every size meets the pins the same way.
- Left compartment (X -15.3 to -5.6): pin board 4.0 x 16.4 x 0.8 mm hanging under the seat floor on 2 standoffs and 2 M1.2 screws, top face at Z = -4.482 (mid stroke); main board 1.0 mm thick standing in the YZ plane, in grooves of the side walls, U1 facing the end wall, J1 and the power parts facing the band slot. The USB-C mouth opens in the +Y wall.
- Right compartment (X 5.6 to 15.3): the cell standing, 8.5 mm along X with 0.6 mm swelling room each side.
- Light: 1.5 mm window in the -X end wall at Z = -9, filled with clear epoxy, in front of LED1.
- Lid: 1.5 mm plate on a hinge along X at the -Y edge, snap latch on the +Y side.
- Outer size, closed, from out/case_size.txt: 33.6 x 33.4 x 55.2 mm including the hinge knuckle and the latch tab; the box without them is 33.6 x 30.2 x 54.9 mm (Z from -43.2 to 11.7). The cell sets the height (40.0 mm standing) and the US 13 band plus the block set the footprint.
- Drawings in out/: case_top.png, case_section_pins.png, case_section_pins_detail.png, case_section_Y0.png, case_section_band_US5.png, case_section_band_US13.png. 3D: case_assembly_US13.step, case_assembly_US5.step, case_body.stl, case_lid.stl, case_base.stl, one STEP per part in out/parts/.

## 8. Items only a supplier can close

| # | Item | Who | What to ask |
|---|---|---|---|
| S1 | Cell with the leads, connector and PCM side for this layout | DNK Power | DNK852338 with 40 mm flying leads from the PCM end, NTC 10 k 103AT optional, UN38.3 report, 20 samples |
| S2 | Full-speed fallback of the ring chip's high-speed USB | Nordic | confirmation that nRF54LM20A USBHS enumerates at full speed with a full-speed host |
| S3 | Exact package drawing and pad layout of ZDSD64GLQEAG-R | Zetta | LGA8x2 9 x 10 mm drawing and package height |
| S4 | Spring pin force at mid stroke and life with gold pads 1.6 mm | Mill-Max | force curve for 0981-0-15-20-87-14-11-0 (the sheet gives 90 gf without stroke point) |
| S5 | Boost efficiency at 0.1-0.3 A, PMID load in charge mode | TI | confirmation that a load on PMID is allowed while charging from VBUS |
| S6 | Production housing | tooling partner | material and process for body, lid, latch and hinge |
