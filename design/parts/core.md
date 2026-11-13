# Core electronics candidate parts (datasheet facts)

Checked on 2026-11-10. Tags: [F] = read from the maker's own document (page or section given). [S] = search-result text only, not opened. "not read" = the field was not in a page I opened.

Evidence copies are in `<scratch>/ring-core-evidence/`: `im73d122_en.pdf` (IM73D122V01 EN, Infineon), `im72d128_chipdip_en.pdf` (IM72D128V01 EN, third-party host copy), `xtsd_oneyac_rev2.9.pdf` (XTX Rev V2.9, Oneyac copy), `max77654_rev2.pdf` (MAX77654 Rev 2), `bq25180_c.pdf` (BQ25180), `apollo510_v092.pdf` (Apollo510 v0.9.2). `im72d128_cn.pdf` was fetched but not read.

## 1. Main chip (BLE + 4 PDM mic inputs)

Candidates as columns. Fields in rows.

| Field | nRF5340 | nRF54L15 | nRF54H20 | Apollo510 (datasheet v0.9.2, preliminary) | Apollo4 Blue Plus |
|---|---|---|---|---|---|
| Orderable part number, as printed | not read | not read (product page gives only "nRF54L15") [F] nordicsemi.com/Products/nRF54L15 | not read | AP510NFA-CBR (BGA), AP510NFA-CCR (WLCSP) [F] p.2 Ordering Information | not read in PDF. [S] AMA4B2KP-KXR / AMA4B2KP-KBR (DigiKey listing) |
| Package and size | not read | CSP47 2.45 x 2.25 mm, 47 balls; QFN52 6 x 6 mm, 52 pins; QFN48 6 x 6 mm, 48 pins; QFN40 5 x 5 mm, 40 pins [F] docs.nordicsemi.com/r/bundle/ps_nrf54L15/page/keyfeatures_html5.html (HTML, no page no.) | WLCSP 4.7 x 4.3 mm; ball count not on page [F] nordicsemi.com/Products/nRF54H20 (HTML) | BGA 6.6 x 6.6 mm with 183 GPIO; WLCSP 4.9 x 4.7 mm with 144 GPIO [F] p.2 Package Options. Ball count (not GPIO) not read (p.216 not read) | [S] 4.7 x 4.7 mm, 131-BGA, 81 GPIO, per Rev 1.3.0 datasheet (not opened) [S] search summary |
| Number of PDM interfaces and channels | not read | Up to 2 digital mics, stereo or mono [S] search text from docs.nordicsemi.com/r/bundle/ps_nrf54l15/page/pdm.html (page not opened); keyfeatures HTML only lists PDM [F] | not in pages read | 1x PDM stereo DMIC interface [F] p.2; up to 2 digital mics [F] p.139 | not read |
| PDM clock range | not read | not read | not read | 400 kHz to 3.072 MHz [F] p.139 Features | not read |
| Supply voltage range | 1.7 V to 5.5 V [F] keyfeatures HTML | 1.7 V to 3.6 V (supply and GPIO) [F] keyfeatures HTML | not stated for the SoC [F] nordicsemi.com/Products/nRF54H20 | 1.71 V to 2.20 V (VDDP/VDDA) [F] p.229 Table 35; 1.71 to 2.2 V [F] p.2 | not read |
| CPU run current | not read in pages (datasheet not opened) | ~20 uA/MHz is a CoreMark benchmark on Nordic blog, not datasheet [S]; 2.6 mA CoreMark at 128 MHz [S] | not in pages read | 35.3 uW/MHz (low-power CoreMark, 1.8 V, 96 MHz) and 46.8 uW/MHz (high-perf, 1.8 V, 250 MHz) [F] p.235 Table 40. Units are uW/MHz, not uA/MHz | not read |
| PDM interface current | not read | not read | not read | not read (p.273 PDM interface not opened) | not read |
| Radio TX current | 3.2 mA run current in TX (0 dBm) [F] keyfeatures HTML | 4.8 mA TX at 0 dBm, 3 V [S] Nordic product page via search (not opened) | not in pages read | none, no radio listed in features p.2 [F] | not read |
| Radio RX current | 2.6 mA run current in RX [F] keyfeatures HTML | 3.4 mA RX [S] (search text) | 1.7 mA RX (3 V, DC/DC) [F] nordicsemi.com/Products/nRF54H20 | none | not read |
| Sleep (system off / deep sleep) current | not read | not read | not read | System Sleep mode 1: 750 uW; deep sleep 2 with 160 kB SRAM: 23.8 uW [F] p.235 Table 40 | not read |
| RAM | 512 kB low-leakage RAM (application core) [F] keyfeatures HTML | 256 kB RAM [F] keyfeatures HTML | 1 MB RAM [F] nordicsemi.com/Products/nRF54H20 | 3.75 MB TCM and system RAM; 768 kB TCM [F] p.2 | [S] 2.75 MB SRAM |
| Flash / NVM | 1 MB flash (application core) [F] keyfeatures HTML | 1.5 MB NVM [F] keyfeatures HTML | 2 MB NVM [F] nordicsemi.com/Products/nRF54H20 | Up to 4 MB non-volatile memory [F] p.2 | [S] up to 2 MB MRAM |
| SPI / QSPI / I2C / I2S | SPI up to 5x; I2C up to 4x; QSPI yes; I2S yes [F] keyfeatures HTML | SPI/UART/TWI and high-speed SPI; I2S yes [F] keyfeatures HTML. QSPI not read | not in pages read | 2x SPI manager; 8x I2C/SPI managers; 2x full-duplex I2S; QuadSPI display interface [F] p.2. QSPI on flash not read | not read |
| SDIO / eMMC | no | no | not read | 2x SDIO (SD3.0) / eMMC v4.51 [F] p.2 | not read |
| External parts (crystals, inductors, antenna match) | not read | not read | not read | 48 MHz XTAL, 32.768 kHz XTAL [F] p.2. Voltage-supply external components p.230 not read | not read |
| Pre-certified module (maker, part number, size) | not read | not read | not read | not read | not read |
| BLE | yes [S] Nordic product line, not opened | not verified in pages read (BLE not quoted from the key-features page) | yes (RX sensitivity -99 dBm for BLE 1 Mbps) [F] nordicsemi.com/Products/nRF54H20 | NO BLE in v0.9.2 features [F] p.2. Apollo510B adds BLE 5.4 [S] cnx-software search | yes [S] search text, BLE version conflicting (5.1 or 5.4); datasheet not opened |

Notes for chip 1:
- Apollo510 v0.9.2 is preliminary (p.1 "DATASHEET - Preliminary and subject to change"). It has no radio in the features list (p.2), so it does not meet the BLE requirement as written.
- The Apollo510 PDM count in search snippets differs (Mouser, CNX say two PDM DMIC interfaces). The datasheet itself says one stereo PDM interface (p.2).
- nRF5340 and nRF54L15 power numbers from the datasheet PDFs were not read. Only the HTML key-features pages were read. A full datasheet table read is still needed.

## 2. Storage 8 GB or more, smallest package

Important: 8 Gbit = 1 GB. Both the XTX and MK parts below are 8 Gbit, which is 1 GB, not 8 GB. Neither meets the 8 GB requirement.

| Field | XTX XTSD08GLGEAG (SD NAND) | MK-Founder MKDV8GIL-AS (SD NAND) | SPI NAND (up to 8 Gbit) | eMMC (153-ball or smaller) |
|---|---|---|---|---|
| Part number as printed | XTSD08GLGEAG and XTSD08GCLGEAG [F] Rev V2.9 p.3 Product List | MKDV8GIL-AS [S] LCSC/distributor listings; datasheet not opened | not read (the brief gives only "up to 8 Gbit", which is 1 GB) | not read |
| Capacity | 8 Gb = 1 GB [F] p.3 Product List (8Gb row) | 8 Gbit [S] distributor listings | up to 8 Gbit = 1 GB | not read |
| Package and dimensions | LGA8, 8 x 6 mm; A 0.85/0.90/0.95 mm; D 7.95/8.00/8.05 mm; E 5.95/6.00/6.05 mm [F] p.3 and p.12 | LGA-8 (6 x 8) [S] | not read | not read |
| Interface | SD 2.0, 1-bit/4-bit SD mode and SPI mode, up to 50 MHz [F] p.3 Features and p.4 pin table | SD / SPI mode; 50 MHz [S] | not read | not read |
| Supply voltage | 2.7 V to 3.6 V [F] p.8 Table 6.3 DC Characteristics. p.3 says "3.3V supply voltage is required" | 2.7 V to 3.6 V [S] | not read | not read |
| Read current | Operation current 30 mA max, read [F] p.8 (3.6 V / 25 MHz, 50 MHz) | not read | not read | not read |
| Write current | Operation current 30 mA max, write [F] p.8 | not read | not read | not read |
| Standby current | 0.2 mA max at VDD 3.0 V, clock stop [F] p.8. 20 mA max with CLOCK 25 MHz, VDD 3.6 V [F] p.8 | not read | not read | not read |
| Write speed | Write speed up to class 8 [F] p.3 | class 6 [S] (one search summary) | not read | not read |
| Datasheet revision | Rev V2.9, Oct 23 2018 [F] p.1 (Oneyac copy). Newer Rev 1.0 Mar 2026 exists [S] search summary, not opened | | | |

Note: the XTX Rev V2.9 document is from 2018. A 2026 revision (1.8 V and 3.3 V series) exists per search [S] and was not opened.

## 3. Power management for one Li-Po cell

| Field | Nordic nPM1300 | TI BQ25180 | Maxim/ADI MAX77654 (Rev 2) |
|---|---|---|---|
| Part number as printed | nPM1300 [F] docs.nordicsemi.com/r/bundle/ps_npm1300 (HTML) | BQ25180 [F] p.1 | MAX77654 [F] p.1 (Rev 2, 2/20, 19-100560) |
| Package and size | not read | DSBGA-8, body 1.6 mm x 1.1 mm [F] p.1 Device Information | 6.52 mm2 WLP, 30-bump, 0.4 mm pitch, 6x5 array [F] p.1 |
| Charge current range and step | not read (charger spec not in pages read) | 5 mA to 1000 mA fast-charge current regulation range [F] p.7 Table 7.5 (I_CHG_RANGE). Step not in pages read | Fast-charge 7.5 mA to 300 mA [F] p.1 Benefits and Features. Step not read |
| Battery regulation voltage | not read | 3.5 V to 4.65 V, 10 mV steps [F] p.7 (V_REG_RANGE) | 3.6 V to 4.6 V [F] p.1 |
| Termination current | not read | 10% of charge current, 2.7 to 3.3 mA at 30 mA [F] p.7 | 0.375 mA to 45 mA [F] p.1 |
| Buck outputs (voltage, max current) | Two BUCKs referenced in the quiescent-current rows [F] HTML sys-el-spec; their voltage and max current not read; LDO count not read | None (linear charger, no buck or LDO in features p.1) | 3x SIMO buck-boost, 0.8 V to 5.5 V; max current not read [F] p.1 |
| LDO outputs | not read | none listed in p.1 | 2x LDO or load switch, each 100 mA max [F] p.1 |
| Quiescent current | Ship mode 370 nA [F] nordicsemi nPM1300 system electrical spec (HTML). Battery operation, all BUCKs and LDOs disabled 600 nA. One BUCK Auto 800 nA. Both BUCKs Auto 1100 nA. One BUCK PWM 4.0 mA. Both BUCKs PWM 7.1 mA (VOUT 1.8 V). LDO quiescent not read | Battery quiescent 3 uA typ, 3.5 uA max (25 C) [F] p.6 Table 7.5 (I_Q_BAT). 4 uA typ, 5 uA max (0 to 85 C) [F] p.6 | Operating 6 uA typ with 3 SIMO + 2 LDO enabled, low-power mode [F] p.1. Shutdown 0.3 uA [F] p.1 |
| Ship mode current | 370 nA [F] nPM1300 system electrical spec (HTML) | 3.2 uA typ, 4.5 uA max (button enabled, 0 to 85 C) [F] p.6 I_BAT_SHIP. Shutdown 15 nA [F] p.6 | Ship mode below 200 nA IQ [F] p.1 |
| Fuel gauge | not read | Not in pages read | Not in pages read |
| External parts in reference circuit | not read | Simplified schematic on p.1 shows 1 uF input, 10 uF SYS, 1 uF BAT caps and an NTC (values from figure) [F] p.1. Reference design on p.41 not read | 1.5 uH inductor, bypass caps and TBIAS resistor per block diagram [F] p.2 |
| Source and revision | Nordic product spec (HTML) | SLUSE99C, revised Jan 2023 [F] p.1 | Rev 2 (2/20), not latest. Search text reports Rev 8 (9/21) with the same ship mode and 6 uA numbers [S] |

Notes: BQ25180 is a linear charger only. It has no buck or LDO outputs, so it cannot supply the rails by itself. MAX77654 is the Rev 2 (2020) document; figures may differ in newer revisions. TI BQ25120A and nPM1304 were not read.

## 4. Microphones

| Field | Infineon IM73D122V01 | Infineon IM72D128V01 |
|---|---|---|
| Part number and ordering code | IM73D122V01, ordering code SP005675385, marking I73D19, package PG-LLGA-5-3 [F] p.1 Table 1. DigiKey listing gives IM73D122V01XTMA1 [S] | IM72D128V01, ordering code SP005567257, marking I72D07, package PG-LLGA-5-3 [F] p.1 Table 1 (copy hosted by chipdip.ru; content is Infineon datasheet v1.00, 2022-02-22) |
| Package size | 4 mm x 3 mm x 1.2 mm [F] p.1 Features | 4 mm x 3 mm x 1.2 mm [F] p.1 Features |
| Pin-out | DATA 1, VDD 2, CLOCK 3, LR 4, GND 5 [F] p.11 Table 9 | not read (p.11 not opened) |
| Supply range | 1.62 V to 3.6 V (typ 1.8 V) [F] p.7 Table 5 | 1.62 V to 3.6 V (typ 1.8 V) [F] p.7 Table 5 |
| Current, standby | Standby 25 uA typ, 50 uA max [F] p.8 Table 6 | Standby 25 uA typ, 50 uA max [F] p.8 Table 6 |
| Current, clock off | 1 uA max, CLOCK pulled low [F] p.8 Table 6 | 1 uA max [F] p.8 Table 6 |
| Current, by PDM clock | 768 kHz: 280 typ / 310 max uA; 1.536 MHz: 690 / 770 uA; 2.4 MHz: 750 / 945 uA; 3.072 MHz: 980 / 1120 uA; 4.8 MHz: 900 / 1000 uA [F] p.8 Table 6 | 768 kHz: 280 / 310 uA; 1.536 MHz: 690 / 770 uA; 2.4 MHz: 820 / 945 uA; 3.072 MHz: 980 / 1120 uA; 4.8 MHz: 900 / 1000 uA [F] p.8 Table 6 |
| PDM clock range per mode | Standby up to 350 kHz; low power 450 to 850 kHz; normal 1.2 to 1.65 MHz; high performance 2.0 to 2.6 MHz and 2.9 to 3.3 MHz; ultrasonic 4.56 to 5.04 MHz [F] p.7 Table 5 | Same mode table as IM73 [F] p.7 Table 5 (read from the copy) |
| Start-up time | 20 ms max (+/-0.5 dB accuracy), 50 ms max (+/-0.2 dB) [F] p.8 Table 6 | 20 ms max (+/-0.5 dB), 50 ms max (+/-0.2 dB) [F] p.8 Table 6 |
| Mode switch time | 20 ms max / 50 ms max [F] p.8 Table 6 | 20 ms max / 50 ms max [F] p.8 Table 6 |
| Sensitivity, SNR, AOP | -26 dBFS typ (-27 to -25) [F] p.6 Table 3; SNR 73 dB(A) at 3.072 MHz; AOP 122 dBSPL [F] p.6 | -36 dBFS typ (-37 to -35) [F] p.6 Table 3; SNR 72 dB(A) at 3.072 MHz; AOP 128 dBSPL [F] p.6 |
| Recommended sound port hole | PCB sound port radius 0.4 mm (diameter 0.8 mm) [F] p.12 Section 5 | not read (p.12 not opened) |
| Recommended land pattern | Pad figure on p.12 Figure 13: pad spacing 1.7 mm and 0.85 mm, pad 0.75 mm, 0.45 mm (read from figure labels) [F] p.12 | not read (p.12 not opened) |
| Select pin (L/R) | LR pin 4. GND = channel DATA1 (drives on falling edge). VDD = channel DATA2 (drives on rising edge) [F] p.10 Table 8 and p.11 Table 9 | Not read (p.10 and p.11 not opened) |

## Not found / gaps
- Apollo4 Blue Plus: only search text [S] was read. Datasheet v1.3.0 or v1.7.0 not opened.
- nRF5340 and nRF54L15: datasheet PDFs not opened. Only HTML key-features pages were read. Current tables, pre-certified modules and crystals were not read.
- eMMC: not searched. No eMMC candidate read.
- SPI NAND: not searched. The brief's "up to 8 Gbit" is 1 GB.
- nPM1304, TI BQ25120A: not read.

## questions_for_owner
1. Storage: 8 GB is 64 Gbit. Every SD NAND or SPI NAND part listed here is at most 8 Gbit (1 GB). Should eMMC at 64 Gbit (8 GB) be the target?
2. Apollo510 v0.9.2 shows no BLE in its features list (p.2). Does the ring require the Apollo510B variant, or should Apollo510 be dropped for chip 1?
3. BQ25180 has no buck or LDO outputs. Do you want a PMIC with rails (nPM1300 or MAX77654) as the single power source?

RESULT: done, 4 tables filled with datasheet-read fields for 3 to 5 candidates per function. Storage has a capacity mismatch, and many chip-1 and PMIC current fields are marked not read.
