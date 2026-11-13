# UI parts, pass 2: maker datasheet fields

Legend. [F] = read from the maker's document (page given; printed page where the document prints one, otherwise PDF page). [S] = search text or distributor listing only, not opened as a maker PDF. "not in the document" = the document read does not state it.

Files read (in `design/datasheets/`): display_TOH095XVT-01.pdf (18 pp), sgm38042.pdf (17 pp), alps-skrh-catalog.pdf (2 pp), motor_3A-03208B.pdf (9 pp), vybronics-z4-sparkfun.pdf (18 pp; its own page 1 names VZ43FC1B5640007L), kingbright-apa1606surck-official.pdf (4 pp), ti-drv8837c.pdf (23 pp). Downloaded but not usable as PDFs (HTML or empty): `panasonic-EVPAVAA1A.pdf` (16 bytes), `nexperia-PMZ290UNE.pdf` (HTML), `brightek-N0R68S92-0402-topview.pdf` (HTML). Also saved and not read: sgm38042a.pdf (31 pp), alps-chipdip-796.pdf (6 pp, not identified), kingbright-apa1606-ameya.pdf (6 pp, this is APA1606SECK Super Bright Orange, not the red part).

## 1. Display: Tailor Pixels TOH095XVT-01, 0.95 in AMOLED 120 x 240 [F, display_TOH095XVT-01.pdf]

| Field | Value | Page |
|---|---|---|
| Part number | "TOH095XVT-01" | p.1 cover [F] |
| Module outline | "12.8(H) ×27.35(V)×0.8(T)" mm; drawing "0.8±0.1" thickness | p.4 [F]; p.5 drawing [F] |
| Active area | "10.8(H) ×21.6(V)" mm | p.4 [F]; p.5 drawing [F] |
| Resolution | "120RGB x 240" | p.4 [F] |
| Display type / mode | "AMOLED", "Transmissive" | p.4 [F] |
| Driver IC | "SH8501A" | p.4 [F]; p.5 drawing note 4 [F] |
| Interface | "4SPI" | p.4 [F] |
| Colours | "16.7M" | p.4 [F] |
| Operating temperature | "-20～70 ºC" (module table, p.4) and "Top -20 to +60 ºC" (absolute maximum table, p.7). CONFLICT, not resolved in the document | p.4 [F]; p.7 [F] |
| Storage temperature | "-40～80 ºC" (p.4); "Tstg -30 to +70 ºC" (p.7). CONFLICT | p.4 [F]; p.7 [F] |
| Weight | "TBD" | p.4 [F] |
| Luminance on surface | "450 cd/m²" (p.4); typ 450 at If = 20 mA, Ta 25 ºC, VDD 2.8 V (p.8 table 9.1) | p.4 [F]; p.8 [F] |
| Contrast ratio | "30000:1" (p.4); p.8 table lists CR "30000" in the Min column, no typ or max | p.4 [F]; p.8 [F] |
| Frame frequency | "fFR" typ 60 Hz | p.7 [F] |
| Current consumption | Normal display: "Ivdd" in mA, Min/Typ/Max cells blank, shown as "-". Standby: "Ivdd" in uA, cells blank. No current figure in the document | p.7 [F] |
| Supply / logic voltages | VDD absolute range "-0.3 to +5.5 V"; IOVDD min 1.65, typ 1.8, max 3.3 V; VGH 6 / 6.5 / 8 V; VGL -8 / -6 / -5 V; logic levels VIL max 0.3 IOVDD, VIH min 0.7 IOVDD, VOL max 0.2 IOVDD, VOH min 0.8 IOVDD | p.7 [F] |
| ELVDD | "4.55~4.65V" | p.6 pin 2 [F] |
| ELVSS | "-2.3~-2.1V" | p.6 pin 1 [F] |
| VCI / VCC | "VCC2.7~3.6V" (p.6 row "VCI"); drawing names pin 4 "VCC" | p.6 [F]; p.5 [F] |
| IOVCC | "1.65~3.3V" | p.6 pin 5 [F] |
| FPC type | 0.2 mm FPC tail, "0.2±0.03含PI补强" (with PI stiffener), 15 contacts, contact side marked | p.5 [F] |
| Mating connector type | not in the document | - |
| Connector pitch | not in the document as a value. Drawing prints "4.8" beside the pin row; not labelled as pitch | p.5 [F] |
| FPC length | "20" printed on the left vertical dimension; the edge it measures is not labelled | p.5 [F] |
| FPC step | "3.2" printed above the tail step; feature not labelled | p.5 [F] |
| RoHS | "This module uses RoHS material" | p.1 [F] |

### 15-pin table

Pins from the drawing (p.5, page image) and the Module Interface table (p.6, page image). The two differ where marked.

| Pin | Drawing p.5 | Table p.6 | Function, p.6 [F] |
|---|---|---|---|
| 1 | ELVSS | ELVSS | "Negative Power supply for Panel -2.3~-2.1V" |
| 2 | ELVDD | ELVDD | "Positive Power supply for Panel 4.55~4.65V" |
| 3 | MTP | row numbered "4", labelled MTP | "burn pin" |
| 4 | VCC | VCI (row numbered "4") | "Power supply for display driver IC analog system. VCC2.7~3.6V" |
| 5 | IOVCC | IOVCC | "Power supply for display driver IC interface and logic system 1.65~3.3V" |
| 6 | SWIRE | SWIRE | "Swire protocol setting pin of Power IC" |
| 7 | TE | TE | "Tearing effect output pin to synchronize MCU to frame writing, activated by S/W command. When this pin is not activated, this pin is output low" |
| 8 | RESET | RESX | "Display driver reset, must be applied to properly initialize the chip. Signal is active low" |
| 9 | CS | CS | "chip select" |
| 10 | SCL | SCL | "A synchronous clock signal in SPII/F" |
| 11 | RS | RS | "Display data/command selection pin in parallel interface. -This pin is used to be serial interface clock." |
| 12 | SDA | SDA | "Reads strobe signal to write data when RDX is 'Low'" |
| 13 | GND | GND | "Power Ground" |
| 14 | GND | GND | "Power Ground" |
| 15 | GND | GND | "Power Ground" |

Differences and gaps:
- Pin 3 vs 4: the table has no pin 3 (MTP row is numbered 4, VCI row is numbered 4). Drawing gives pin 3 = MTP and pin 4 = VCC.
- Pin 8: drawing "RESET", table "RESX".
- Pins 11 and 12: the RS description mixes parallel-interface and serial-clock wording; SDA's description refers to RDX (a parallel read strobe). The document does not give a data/command (D/C) pin for 4-wire SPI. Not resolved in the document.

### Power-on / power-off sequence

Section 9.2, p.9 (page image, low resolution). Labels legible: IC state "Unknown", "Reset", "Initial setting & Sleep out", "Display on"; "≥10ms", "≥130ms", "≥66.7ms", "10ms", "0ms", "Tdn_dly <400us". The edge each label measures is not legible. The text layer has only the caption "The power on/off sequence is illustrated below" [F].

### Current and power

The document gives no current or power figure for the module beyond luminance: 450 cd/m² (p.4, p.8). Ivdd values are blank (p.7).

### Initialization code

Not in the document. Section 8 "Initialization Code" (p.7) is a heading with no code. The contents list (p.3) points it to p.8, which holds section 9.1. The reference table (p.18) names "SH8501A IC Data sheet" for it. Listing file: `design/parts/display-init.txt`.

## 2. Display driver SH8501A (Sino Wealth) [S]

- Search "SH8501A AMOLED driver IC datasheet Sino Wealth pdf" returned no SH8501A document. Results held other Sino Wealth AMOLED drivers (SH8601A0 on Espressif, SH8601Z0 on Waveshare). Not used.
- SPI write protocol: not found. Sleep-in current: not found. Brightness command: not found. No SH8501A page was opened.
- Status: not found. The module document (p.18) cites the SH8501A data sheet; the vendor, Tailor Pixels, is the likely source.

## 3. AMOLED power supply: SGMICRO SGM38042 [F, sgm38042.pdf]

Source: `design/datasheets/sgm38042.pdf` (https://www.sg-micro.com/rect/assets/57e54a56-00a0-44f6-bc1c-53eda42ca59c/SGM38042.pdf), JANUARY 2021, REV. A.3 (p.1).

| Field | Value | Page |
|---|---|---|
| Part number | "SGM38042", ordering "SGM38042-0YG/TR" to "SGM38042-12YG/TR" | p.1, p.2 [F] |
| Lifecycle | Web product page: "SGM38042 is not recommended for new designs"; replacement "SGM38045" (web page, not the PDF) | [S] sg-micro.com/product/SGM38042 |
| Function | "Single Inductor Triple Output AMOLED Display Power Supply" | p.1 [F] |
| Package | "WLCSP-1.51×2.10-15B", 15 balls, pitch 0.4 mm, ball diameter "0.270±0.020" | p.1, p.15 [F] |
| Package body | "2.095±0.025" x "1.505±0.025" mm; side view "0.585±0.038" overall height; "0.040±0.005", "0.350±0.013", "0.195±0.020" printed on the side view, features not labelled in the text | p.15 drawing [F] |
| Input voltage | "2.7V to 5.5V" | p.3 [F] |
| Positive output VCPO (pin CPO) | programmable "2.4V ~ 6.4V" in 100 mV steps | p.1, p.7 [F] |
| Negative output VCNO (pin CNO) | programmable "-2.4V ~ -6.4V" | p.1, p.5 [F] |
| -2.2 V output | not in the document. Lowest negative setting is -2.4 V ("VCNO Voltage Range -6.4 to -2.4 V") | p.5 [F] |
| Auxiliary CVO | fixed "2.8V or 1.8V", LDO 50 mA; "When VIN ≥ 3.0V, VCVO = 2.8V" | p.1 [F]; p.11 note 1 [F] |
| Default models | SGM38042-3: VCPO +4.6 V, VCNO -2.4 V, VCVO 2.8 V. SGM38042-1: +4.6 / -3.5. SGM38042-5: +3.3 / -3.0. Full list | p.3 [F] |
| Output current | "40mA Output Current for VCPO and VCNO" | p.1 [F] |
| Quiescent current | "Supply Current with No Load IQ": typ 0.5 mA, max 0.7 mA (VIN 3.7 V, no switching) | p.5 [F] |
| Shutdown current | "IOFF": typ 0.4 µA, max 1 µA (VIN 3.7 V, CVO_EN = 1W = P2N = GND) | p.5 [F] |
| Efficiency | Plot only ("Efficiency vs. Output Current", VIN 2.8 / 3.7 / 4.2 V, VCPO +4.6 V, VCNO -3.0 V, L 4.7 µH), axis 50 to 90 %. No numeric table | p.10 [F] (figure) |
| Switching frequency | "fSW" typ 1.6 MHz (1.5 to 1.7) | p.5 [F] |
| Inductor (typical application) | "L 4.7μH"; recommended "4.7μH/SLF7055T-4R7N3R1-3PF" | p.1 Figure 1 [F]; p.8 [F] |
| Capacitors (typical application) | CIN 10 µF, CV 10 µF, CPR 10 µF, CNR 10 µF, CP 10 µF, CN 10 µF. Recommended "10μF/08055C106KAT2A". Range "4.7μF ~ 47μF", Z5U, X7R or X5R | p.1 Figure 1 [F]; p.8 [F]; p.12 [F] |
| Output accuracy | VCPO at 4.6 V ±45 mV; at 3.5 V ±60 mV. VCNO at -2.4 V ±45 mV; at -3.5 V ±55 mV (VIN 3.7 V, 25 ºC) | p.5 [F] |
| Logic inputs (CVO_EN, P2N, 1W) | VIL max 0.35 V; VIH min 1.05 V | p.5 [F] |
| Control | 1-Wire interface on pin 1W (A3); timing p.6. Counts 1 to 42 set VCNO, counts 43 to 83 set VCPO; count 41 = -2.4 V; count 42 = "VCNO_X - 0.05V" | p.6, p.7 [F] |
| Active discharge | DISP and DISN pins, discharge time 10 ms | p.5, p.12 [F] |
| Start-up order | P2N pin: VIN starts positive first, AG starts negative first, 1W starts both together | p.4 pin B1, p.12 [F] |
| Temperature | ambient "-40℃ to +85℃"; junction "-40℃ to +125℃" | p.3 [F] |

Fit to the display rails (section 1):
- ELVDD 4.55 to 4.65 V (display p.6). VCPO accuracy ±45 mV at 4.6 V (p.5). SGM38042-1, -3, -7 and -9 default to +4.6 V (p.3).
- ELVSS -2.3 to -2.1 V (display p.6). The SGM38042 VCNO range ends at -2.4 V (p.5). -2.2 V is outside the listed range.
- Control: display uses SWIRE (display p.6); SGM38042 uses 1W (p.4). Different protocols. Compatibility is not stated in either document.

## 4. Joystick: Alps Alpine SKRH series, 4-direction with centre push [F, alps-skrh-catalog.pdf]

Source: https://tech.alpsalpine.com/cms.media/product_catalog_mu_02_skrh_en_34aeb8c2e3.pdf (`design/datasheets/alps-skrh-catalog.pdf`, 2 pp). This is the maker's catalog. Note 1 states "This catalog shows only outline specifications. When using the products, please obtain formal specifications for supply." (p.1). The circuit diagram, dimension and land drawings are on pp.1 to 2 as images (Drawing No.1 to No.4); the text layer does not carry them.

Product list (p.1) [F]:

| Part | 4-dir force (N) | Centre push (N) | 4-dir travel (mm) | Centre travel (mm) | Life | Contact resistance | Stem | Guide bosses | W x D x H (mm) | Drawing no. |
|---|---|---|---|---|---|---|---|---|---|---|
| SKRHAAE010 | 1.23 | 2.35 | 0.25 | 0.15 | 200,000 each direction | 500 mΩ max | Black | Without | 7.35 x 7.5 x 1.8 | 1 |
| SKRHABE010 | 1.23 | 2.35 | 0.25 | 0.15 | 200,000 each direction | 500 mΩ max | Black | With | 7.35 x 7.5 x 1.8 | 2 |
| SKRHACE010 | 1.2 | 2.35 | 0.25 | 0.15 | 1,000,000 each direction | 100 mΩ max | Natural | Without | 7.45 x 7.5 x 1.85 | 3 |
| SKRHADE010 | 1.2 | 2.35 | 0.25 | 0.15 | 1,000,000 each direction | 100 mΩ max | Natural | With | 7.45 x 7.5 x 1.85 | 4 |

For SKRHABE010 (the part named in the brief):
- Part number and type: "SKRHABE010", "4-direction Type with Center-push Function (Surface Mount)", SKRH Series (p.1) [F].
- Outline: "7.35 x 7.5 x 1.8" mm (p.1) [F].
- Operating force: 4-direction 1.23 N; centre push 2.35 N (p.1) [F]. Tolerances are not in the catalog text.
- Travel: 4-direction 0.25 mm; centre push 0.15 mm (p.1) [F]. Footnote 2: "4-directional operating force and travel are measured at 4.3mm height from the bottom of the switch" (p.1) [F].
- Life: "200,000 for each direction" (p.1) [F]. Product page (WebFetch summary, not raw text): "Operating life (5mA 5V DC)", "200,000 cycles for each direction", centre push "200,000 cycles" [F-web summary].
- Contact resistance: "500mΩ max." (p.1) [F].
- Ratings: "50mA 12V DC/10μA 1V DC" (resistive load), "Operating temperature range: -40℃ to +85℃", "Directional resolution: 4-direction" (p.1) [F].
- Stem colour "Black", guide bosses "With" (p.1) [F].
- Circuit diagram terminal numbering: not in the text layer (image). Land pattern: image only. Stem dimensions: image only. Waterproof / IP rating: not in the document.
- 3D CAD zip and reference drawings are linked from the product page (cms.media/product_3dcad_skrhabe010_en_cddb240b17.zip). Not downloaded in this pass.
- Smaller alternative under 6 x 6 mm: not searched in this pass; not in the document read.

## 5. Side-push tactile switch under 4 x 3 mm

No maker PDF for a side-push switch was read in this pass. All values are search or listing text [S].

| Field | Alps SKSG (named) | Panasonic EVPAVAA1A (alternative) | Panasonic EVPAK / EVPAE (checked) |
|---|---|---|---|
| Part number | "SKSG" series: product page found, no part-level dimensions [S] | "EVPAVAA1A" [S] (industry.panasonic.com product page, not opened as PDF) | EVPAK discontinued [S]. EVPAE is 4.5 x 2.2 mm, wider than 4 mm [S] |
| Body dimensions | Height 1.4 mm [S] | "2.8 x 2.3 mm" in title; "2.30 mm" excluding push plate; external "2.8 x 2.65 mm" [S] | EVPAK "3.9 x 2.05 mm", height 1.6 mm excluding push plate [S] |
| Operating force | "4N" heavy-operating-force type [S] | 1.6 N (160 gf) [S] | not stated |
| Travel | 0.12 mm [S] | 0.13 mm [S] | not stated |
| Life | not in the text read | 300,000 cycles [S] | not stated |
| Rating | 50 mA 12 V DC [S] | not in the text read | not stated |
| IP rating | not in the document read | not in the document read | not stated |
| Land pattern | not in the document read | not in the document read | not stated |
| Production status | not stated on the product page read [S] | not stated in the text read | discontinued [S] |

Notes. The EVPAVAA1A PDF was not reached: the 70ic.com copy saved as `panasonic-EVPAVAA1A.pdf` is 16 bytes. Panasonic EVP-AA is a top-push switch, not side-push [S]. The Alps SKTDLDE010 from pass 1 is listed obsolete [S]. Not found: a maker-stated production status for SKSG or EVPAVAA1A.

## 6. Vibration motor 3A-03208B and reflow-solderable alternative

### 6a. Cylinder motor 3A-03208B [F, motor_3A-03208B.pdf]

| Field | Value | Page |
|---|---|---|
| Model | "KPD3A-03208-05-05D-0"; customer model "3A-03208B" (cover) | p.1, p.2 [F] |
| Maker name as printed | not in the document. The text layer has no company name; the cover has blank customer and company fields | p.1 [F] |
| Terminal type | two lead wires (BOM item 16 "PVC, copper"); drawing shows lead length "50mm". No solder terminal or connector stated | p.8 [F]; p.9 drawing [F] |
| Diameter | "3.2 Diam" (title) | p.2 to p.9 [F] |
| Housing length | "8.1±0.1" | p.9 drawing [F] |
| Overall length | "11.6±0.3" | p.9 drawing [F] |
| Free tolerance | "±0.2mm" | p.9 [F] |
| Weight | "0.7±0.2g(APPROX)" | p.4 [F] |
| Rated voltage | "3.0V DC" | p.3 item 2-1 [F] |
| Operating voltage | "2.4～3.6 V DC" | p.3 item 2-2 [F] |
| Rated current | "90mA (MAX)"; shaft-lock "120mA (MAX)" | p.4 items 5-2, 5-3 [F] |
| Rated speed | "30000±5000rpm" | p.4 item 5-1 [F] |
| Starting voltage | "2.4V DC" | p.4 item 5-4 [F] |
| Terminal resistance | "30±20%Ω" | p.4 item 5-6 [F] |
| Operating temperature | "-30～70℃" | p.3 item 2-6 [F] |
| Storage temperature | "-40～80℃" | p.3 item 2-7 [F] |
| Vibration force in G | not in the document | - |
| Life test | 30,000 cycles at 3.0 V DC, "0.5S ON(C.W)、0.5S OFF", 25 ℃ ±2, with counterweight. Pass: rated speed within ±50 % and current within ±30 % of initial | p.5 item 6-1 [F]; p.6 item 7-1 [F] |
| Shock | displacement 1.5 mm (p-p), 10 to 55 Hz, 2 h, x y z | p.5 item 6-2 [F] |
| Drop | 1.5 m, 18 drops | p.6 item 6-7 [F] |

### 6b. Reflow alternative VZ43FC1B5640007L (Vybronics) [F, vybronics-z4-sparkfun.pdf]

The file was saved under the SparkFun name `Z4FC1B1301781`. Its own page 1 reads "VZ43FC1B5640007L", "A/1, 2020.07.01" (`design/datasheets/vybronics-z4-sparkfun.pdf`, 18 pp). Maker per p.1: "www.vybronics.com". Title "圆柱铁芯贴片马达 / Cylindrical core SMT Motor".

| Field | Value | Page |
|---|---|---|
| Rated voltage | "DC3.0V" | p.4 item 2-1 [F] |
| Operating voltage | "DC 2.5~3.4V" | p.4 item 2-2 [F] |
| Rated speed | "10000±2500" rpm at DC 3.0 V | p.5 item 5-1 [F] |
| Rated current | "100 Max" mA | p.5 item 5-2 [F] |
| Starting current | "120 Max" mA | p.5 item 5-3 [F] |
| Starting voltage | "2.3 Max" V | p.6 item 5-4 [F] |
| Terminal resistance | "33±4" Ω, positive to negative | p.6 item 5-5 [F] |
| Insulation resistance | "10Min" MΩ | p.6 item 5-6 [F] |
| Weight | "0.9±0.2g" | p.7 item 6-3 [F] |
| Noise | "50 MAX" dB | p.7 item 6-4 [F] |
| Vibration strength | "Grms 0.65 MIN" and "Gp 0.91 MIN" (100 g jig) | p.8 item 6-5 [F] |
| Response time | 40 ms to 50 % vibration; 90 ms to 100 % | p.8 item 6-6 [F] |
| Diameter | "Φ4.1 DC Cored motor" | p.4 item 1-1 [F] |
| Outline | Drawing on p.15 (page image, rotated). Printed values: "4.5±0.2", "4.3±0.2", "12 MAX" (including end play), "0.3 MAX" end play, "4.9" counterweight to PCB, "R2.1±0.1", "3±0.1", "2-1.7±0.1", "1.4" (terminal). Feature each value applies to is not labelled reliably at this resolution | p.15 [F] |
| Terminal type | "焊锡端子 / Terminal" (solder terminal), "黄磷铜 / Yellow phosphorus copper" | p.16 BOM item 5 [F] |
| Reflow | "Peak temperature: 245℃ ±10℃, ≤5sec"; "Above 220℃ holding time: 30±10sec"; "Pre-heat time: 70±20sec"; ramp 2 to 4 ℃/sec and 1 to 4 ℃/sec | p.18 (page image) [F] |
| Life test | 96 h at 3.0 V, 2 s ON / 1 s OFF cycle, at room temperature; 48 h at 55 ℃ and 48 h at -20 ℃. Life in cycles not stated | p.11 items 8-1 to 8-3 [F] |
| Operating temperature | "-30℃~+70℃" | p.4 item 2-4 [F] |
| Storage temperature | "-40℃～+85℃" | p.5 item 4-1 [F] |
| Vibration test | 10 to 55 Hz, total amplitude 1.5 mm, 30 min total | p.9 item 7-5 [F] |
| Drop | 1.5 m, 12 drops | p.10 item 7-6 [F] |
| IP rating, land pattern | not in the document | - |

## 7. Haptic driver for a 90 mA, 3 V cylinder motor

Neither part was read from a maker PDF in this pass.

| Field | Nexperia PMZ290UNE (MOSFET option) | TI DRV8837C (driver option) [F] |
|---|---|---|
| Source | Nexperia PDF URL returned an HTML page, not a PDF. Search text only [S] | `design/datasheets/ti-drv8837c.pdf` (SLVSD61A, July 2016, 23 pp) |
| Part number | "PMZ290UNE" [S] (distributor variants "PMZ290UNE2YL", "PMZB290UNE,315") | "DRV8837C" [F] p.1 |
| Package | "DFN1006-3 (SOT883)" [S] | "WSON (8)", body "2.00 mm × 2.00 mm" [F] p.1 |
| On-resistance | "0.32 Ω" max, gate voltage for that figure not stated [S]. Sibling PMZB290UNE: 380 mΩ at 4.5 V, 500 mA [S]. At 1.8 V: not found | "HS + LS 1 Ω" [F] p.1. Test condition "VVM = 5 V; VCC = 3.3 V; IO = 200 mA; TJ = 25°C" [F] p.5. H-bridge has no gate-drive pin, so a gate voltage does not apply |
| Maximum current | "1.2 A" drain current [S] | "1-A Maximum Drive Current" [F] p.1 |
| Supply | not applicable | Motor supply VM "0- to 11-V Operating Supply-Voltage Range" [F] p.1; VCC "Logic power-supply voltage 1.8" recommended [F] p.4; logic on "1.8-V to 5-V rails" [F] p.1 |
| Sleep current | not applicable | "Low-Power Sleep Mode With 120-nA Maximum Sleep Current" [F] p.1 |
| Flyback diode | not applicable | not in the pages read |
| Lifecycle | "Obsolete" [S] (findchips listing) | not checked |

Notes. The DRV8837C is 2.0 x 2.0 mm, larger than the SOT-723 or DFN1006 options the brief asked for. It is listed because it is the TI part named. Not found: PMZ290UNE on-resistance at 1.8 V in any document read.

## 8. Red LED: side-view (right angle) and top-view 0402

### 8a. Side-view red: Kingbright APA1606SURCK [F, kingbright-apa1606surck-official.pdf]

Source: `design/datasheets/kingbright-apa1606surck-official.pdf` (Spec DSAF0543 / 1203000476, Rev V.20A, 03/07/2025, 4 pp), from https://www.kingbrightusa.com/images/catalog/SPEC/APA1606SURCK.pdf.

| Field | Value | Page |
|---|---|---|
| Part number | "APA1606SURCK" | p.1 [F] |
| Colour | "Hyper Red (AlGaInP)", water clear | p.1 selection guide [F] |
| Package | "right angle SMD LED"; features say "1.6 x 1.2 x 0.6 mm"; title says "1.6 x 0.6 mm". Drawing: 1.6 (0.063) long, 1.2 (0.047) wide, 0.6 (0.024) high, lens 1.1 (0.043), tolerance ±0.1 | p.1 [F] |
| Pad layout | 0.9 mm pads, 1.6 mm pad span, units mm | p.1 [F] |
| Forward voltage | typ 1.95 V, max 2.5 V at IF 20 mA | p.2 [F] |
| Luminous intensity | min 200 mcd, typ 250 mcd at 20 mA (first row). A second row shows "*55" min and "*80" typ with no condition printed beside it | p.1 selection guide, p.2 [F] |
| Viewing angle | 2θ½ 110° | p.1 [F] |
| Peak wavelength | typ 645 nm at IF 20 mA | p.2 [F] |
| Dominant wavelength | typ 630 nm at IF 20 mA | p.2 [F] |
| Max DC forward current | 30 mA | p.2 [F] |
| Power dissipation | 75 mW | p.2 [F] |
| Operating temperature | -40 to +85 ºC | p.2 [F] |
| Reflow | "Reflow soldering is recommended"; max 2 reflow passes | p.3 [F] |

### 8b. Top-view 0402 red

Not found as a maker PDF in this pass. Search text only [S]: Brightek N0R68S92 (0.50 mm thick 0402 top-view; typ Vf 2.0 V, max 2.4 V at 20 mA; typ 112.5 mcd at 20 mA; 120° to 128°). Its tme.eu PDF link returned HTML, not a PDF. Lumex SML-LX0402SIC-TR: 140 mcd, 636 nm, 120° at 20 mA [S]. Kingbright KPG-1005SURC-TT: 2.4 V, 631 nm, 0.2 mm thick [S]. No Kingbright 0402 top-view datasheet found.

## Not found (summary)

- SH8501A driver datasheet: not found (section 2).
- Display initialization code: not in the document (section 1; display-init.txt).
- Display current or power figures beyond luminance: not in the document (section 1).
- Side-push switches: no maker PDF read; production status for SKSG and EVPAVAA1A not stated by the maker in any text read (section 5).
- PMZ290UNE on-resistance at 1.8 V: not found (section 7).
- Top-view 0402 red maker PDF: not found (section 8b).
- Motor vibration force in G: not in the document (section 6a).

## questions_for_owner

- The display's SWIRE pin (display p.6) and the SGM38042's 1W pin are different protocols. Should the successor SGM38045 be checked next? Its datasheet was not read.
- ELVSS target -2.3 to -2.1 V (display p.6) is outside the SGM38042 negative range (-2.4 to -6.4 V, p.5). Does the lead accept a different supply part?
- The SH8501A datasheet is not in the document set. Should the lead ask Tailor Pixels for it?
- The APA1606SURCK title says 1.6 x 0.6 mm and the features say 1.6 x 1.2 x 0.6 mm (both p.1). Confirm the body size with Kingbright before layout.

RESULT: done, all 8 sections written; SH8501A datasheet not found, side-push production status and PMZ290UNE 1.8 V on-resistance not found, and no top-view 0402 maker PDF read.
