# Screen, controls and feedback parts: datasheet facts

Legend. [F] = read from the maker's own document: a PDF page I viewed as an image, or a maker web page fetched through WebFetch. [S] = search-result text or distributor/reseller listing only, not a page I opened. "not in the pages read" = not read. Page numbers are printed page numbers of the saved PDF. Evidence copies: `<scratch>/ui-parts/`.

Caveat on [F] web pages: the WebFetch tool returns a model-written summary of the page, not the raw page text. Values marked [F-web] are as that summary states them and were not checked against raw page text.

## 1. Colour OLED or AMOLED module (active area inside 28 x 18 mm)

| Field | SSD1331 controller, 96RGB x 64 | NHD-0.95-9664G (Newhaven) | E120A390QSR (Panox), 1.19 in |
|---|---|---|---|
| Maker and part number | Solomon Systech "SSD1331", Rev 1.2, Nov 2007, p.1 [F] (copy hosted at people.ece.ubc.ca/edc/7660.jan2018/SSD1331.pdf) | "NHD-0.95-9664G" [S] digikey.com.br/en/products/detail/newhaven-display-intl/NHD-0-95-9664G/9842781 | "E120A390QSR" [S] search link panoxdisplay.com/uploadfile/datasheet/(1.2oled)E120A390QSR.pdf (not opened) |
| Panel outline (mm) | not in the pages read | not in the pages read | not in the pages read |
| Active area (mm) | not in the pages read. 96RGB x 64 dot matrix, p.1 and p.6 [F] | not in the pages read. "0.95" (24.13mm)" is the display size in the listing title; active area not in the pages read [S] | not in the pages read |
| Thickness | not in the pages read | not in the pages read | not in the pages read |
| Resolution | 96RGB x 64 dot matrix panel, p.6 [F] | 96 x 64 [S] | 390 x 390 [S] |
| Driver chip | SSD1331 itself, 288 segment x 64 common, p.6 [F] | SSD1331 [S] | RM69091 [S] |
| Interface | 8/9/16-bit 6800-series and 8080-series parallel, and serial peripheral interface, p.6 [F]. Ordering: SSD1331U1R1 and SSD1331U3R1 are "8 bit or SPI interface", p.6 [F] | parallel 68XX/80XX and 4-wire SPI [S] | QSPI and MIPI/SPI [S] |
| Connector type and pin count, pin-out | COF options: "35mm film, 5 sprocket hole" (U1R1) and "35mm film, 4 sprocket hole" (U3R1), output lead pitch 0.06mm SEG and 0.09mm COM, p.6 [F]. Pin-out: section 6, p.12 (not read). Module connector: not in the pages read | not in the pages read | not in the pages read |
| Supply voltages | VDD = 2.4V to 3.5V (IC logic); VCC = 8.0V to 18.0V (panel driving); VDDIO = 1.6V to VDD (MCU interface), p.6 [F] | logic 3.3V, display 14V [S] | not in the pages read |
| Current or power at stated brightness | not in the pages read. p.6 gives "Segment maximum source current: 200uA" and "Common maximum sink current: 60mA" (driver limits, not module power) [F] | not in the pages read | not in the pages read |
| Sleep current | not in the pages read | not in the pages read | not in the pages read |
| Operating temperature | "-40 to 85 °C", p.6 [F] | not in the pages read | not in the pages read |
| Document status | "Advance Information", p.1 [F] | not in the pages read | not in the pages read |

Not found: a 1.1 in AMOLED 126 x 294 bare panel with flexible cable. Search "1.1 inch AMOLED 126x294 bare panel flexible FPC datasheet SPI QSPI driver IC" returned no datasheet for that size (search results only, no page opened). Module-maker sheets from buydisplay.com and waveshare.com were not opened.

## 2. Miniature joystick or 5-direction navigation switch

| Field | SKRHABE010 (Alps Alpine) | SKRHADE010 (Alps Alpine), variant | EVQ-Q5A05K (Panasonic) |
|---|---|---|---|
| Part number | "SKRHABE010", "4-direction Type with Center-push Function (Surface Mount)", SKRH Series [F-web] tech.alpsalpine.com/e/products/detail/SKRHABE010/ | "SKRHADE010" [S] search summary of an Alps catalog copy | "EVQ-Q5A05K" [S] cn.elcodis.com/parts/3726495/EVQ-Q5A05K.html and distyparts.com/product/evq-q5a05k.md (not opened). Panasonic PDF not reached: 70ic.com copy returned HTTP 522 |
| Body dimensions | "7.35×7.5×1.8mm" (W×D×H), Basic information [F-web] | not in the pages read | "9.8 mm diameter", "2.0 mm height" [S] (search summary of EVQQ5 series description) |
| Stem height | not in the pages read (stated only as overall H 1.8 mm; drawing is an image) | not in the pages read | not in the pages read |
| Operating force per direction | 4-direction "1.23±0.69N"; center push "2.35±0.69N" [F-web] | 4-direction "1.2N ±0.69N"; center "2.35N" [S] | "160/320gf" [S] (not stated per direction in the pages read) |
| Travel | 4-direction "0.25mm"; center push "0.15mm" [F-web] | 4-direction 0.25 mm; center 0.15 mm [S] | not in the pages read |
| Rated life (cycles) | "200,000 cycles for each direction" [F-web, Basic information]; center push "200,000 cycles" [F-web, Specifications]. CONFLICT: [S] says 1,000,000 cycles for the SKRHADE010 variant | 1,000,000 [S] | "one million operations in each direction" [S] |
| Circuit (common pin, contacts) | not in the pages read (circuit diagram is an image) | not in the pages read | not in the pages read |
| Waterproof rating | not in the pages read | not in the pages read | not in the pages read |
| Land pattern page | not in the pages read | not in the pages read | not in the pages read |

Notes. The Alps SKRH tables are the only joystick specs read from a maker page; [S] rows come from distributor listings and a search summary. The EVQ-Q5A05K at 9.8 mm diameter is larger than the "under 8 x 8 mm" size in the brief; that is the reported size, not checked against the Panasonic drawing. Panasonic EVQ-Q3AA15 (4-way) is listed obsolete [S]. A third distinct 5-way part from another maker (C&K, E-Switch, CTS) was not searched: not in the pages read.

## 3. Tactile click switch for a side button (under 4 x 3 mm)

| Field | SKTDLDE010 (Alps Alpine) | KXT (C&K) | EVP-AA (Panasonic) |
|---|---|---|---|
| Part number | "SKTDLDE010" [F-web] tech.alpsalpine.com/e/products/detail/SKTDLDE010/ | not in the pages read. ckswitches.com URL redirected to littelfuse.com; not followed | not in the pages read. Not searched |
| Body dimensions | "3.9×2.9×1.55" (mm) [F-web] | not in the pages read | not in the pages read |
| Height | "1.55mm" product height [F-web] | not in the pages read | not in the pages read |
| Operating force | "1.6N" [F-web] | not in the pages read | not in the pages read |
| Travel | "0.15mm" [F-web] | not in the pages read | not in the pages read |
| Life | "200,000 cycles" [F-web] | not in the pages read | not in the pages read |
| IP rating | [F-web] "IP6X equivalent/IPX7"; the page says "IP67-level dust and water resistance is guaranteed for the switch alone and performance may not be guaranteed depending on the mounting conditions and usage" | not in the pages read | not in the pages read |
| Actuator (side or top) | "side push type" [S] (search summary, Alps SKTD description) | not in the pages read | not in the pages read |
| Status | obsolete [S] (ic-direct.com search result); RS "currently unavailable" [S] | not in the pages read | not in the pages read |

Notes. SKTDLDE010 body (3.9 x 2.9 mm) fits the "under 4 x 3 mm" envelope. Its listed status is obsolete [S], which the brief should weigh.

## 4. Vibration motor (LRA or coin ERM, 8 mm or smaller)

| Field | VG0832012 (Vybronics) | VG0832013D (Vybronics) | VG0825001D (Vybronics) |
|---|---|---|---|
| Part number and source | "VG0832012" [S] digikey.de/en/products/detail/vybronics-inc/VG0832012/7364317 and trace-tec.vn/VG0832012-pe17013.html. Vybronics product page: not in the pages read (the coin-LRA product URL returned HTTP 404; the /products/ page loads but lists no part numbers in text) | "VG0832013D" [S] trace-tec.vn (search summary) | "VG0825001D" [S] digikey.fi listing; marked obsolete [S] |
| Diameter and height | diameter "0.315\" Dia (8.00mm)" [S]; height not in the pages read | 8.00 mm [S]; height not in the pages read | 8 mm per search summary [S]; height not in the pages read |
| Rated voltage | "AC Motor Vibration, LRA (Haptic) 1.8VAC" [S] (title of DigiKey listing) | "Voltage - Rated 1.8VAC" [S] | "Voltage - Rated 1.2VAC" [S] |
| Rated current | not in the pages read | not in the pages read | not in the pages read |
| Resonant frequency | "235 Hz" [S] (distributor description "VIBRATION LRA MOTOR 235HZ 1G") | "235 Hz" [S] (distributor listing) | not in the pages read |
| Acceleration (G) at stated test mass | "1 G" [S]; test mass not in the pages read | "1 G" [S]; test mass not in the pages read | not in the pages read |
| Lead or pad type | "wire leads" [S] (trace-tec.vn search summary) | not in the pages read | not in the pages read |

Maker application note, read as [F]: Vybronics Application Note #022, "Summary of Linear Vibration Motors (LRA)", p.1: "Our LRA's are designed to have a resonant frequency / vibration frequency in the 200 hz range" and "must be driven by an AC signal at the devices resonant frequency" (copy: vybronics.com/wp-content/uploads/2021/12/intro-to-lra-technology.pdf). This states a "200 hz range" in general. It does not give any part's frequency, so it does not confirm or reject the 235 Hz figure above.

Not found: Jinlong and AAC coin motors, and Precision Microdrives C08-005 (precisionmicrodrives.com product URL returned "Page Not Found", not in the pages read). Nidec and TDK were not searched. 4 mm and 6 mm eccentric motors were not searched.

## 5. Haptic driver chip

| Field | DRV2605L (TI) | DA7280 (Dialog, now Renesas) | DRV2603 / DRV2625 (TI) |
|---|---|---|---|
| Part number and document | "DRV2605L", "DRV2605L 2- to 5.2-V Haptic Driver for LRA and ERM", SLOS854D, revised March 2018, p.1 [F] (ti.com/lit/ds/symlink/drv2605l.pdf) | "DA7280", "LRA/ERM Haptic Driver", Revision 3.0, 30-Jul-2019, p.1 [F] (copy hosted at cdn.sparkfun.com/assets/a/e/d/1/9/da7280_datasheet_3v0.pdf) | not in the pages read. Not searched |
| Package and dimensions | DSBGA (9): "1.50 mm x 1.50 mm"; VSSOP (10): "3.00 mm x 3.00 mm"; body size (max), Device Information table, p.1 [F] | WLCSP: 12 pins, pin numbers 1-12, p.9 Table 2 [F]. Package body size: not in the pages read. [S] DigiKey lists "12-WLCSP (1.35x1.75)" | not in the pages read |
| Supply range | "Wide Voltage Operation (2 V to 5.2 V)", p.1 [F]. Electrical table p.7 "VDD = 3.6 V" test condition [F] | VDDIO (digital I/O supply) and VDD (haptics supply), p.9 Table 2 [F]. Numeric range: not in the pages read. [S] DigiKey "2.8V ~ 5.5V" | not in the pages read |
| Interface | I2C-controlled digital playback engine, PWM input, hardware trigger input, p.1 [F] ("1.8-V Compatible, VDD-Tolerant Digital Interface") | I2C and PWM input streaming, three GPI pins for up to six haptic sequences, p.1 [F] | not in the pages read |
| Quiescent current | "I(Q) Quiescent current", typ 0.5 mA, max 0.65 mA; test "VEN = 1.8 V, STANDBY = 0, no signal", p.7 Table 6.5 [F] | "IQ = 0.36 µA" in IDLE state; "low quiescent current state (typically 0.36 µA) between playbacks", p.1 [F]. Electrical table: not in the pages read | not in the pages read |
| Standby current | "I(standby) Standby current", typ 4.1 µA, max 7 µA; test "VEN = 1.8 V, STANDBY = 1", p.7 [F] | "Ultra-low latency (0.15 ms) wake-up from STANDBY state, IQ = 0.8 mA", p.1 [F] | not in the pages read |
| Shutdown current | "I(SD) Shutdown current", typ 4 µA, max 7 µA; test "VEN = 0 V", p.7 [F] | not in the pages read | not in the pages read |
| External parts | Recommended components table and Table 32 not in the pages read. Revision notes: "Changed the typical value of C(VDD) in Table 32 From: 0.1 µF To: 1 µF", p.2 [F]; "Changed C(REG) from 0.1 to 1 µF in Figure 60", p.3 [F] | "Small solution footprint requiring only one decoupling capacitor in both WLCSP and QFN", p.1 [F]. Pull-ups: nIRQ and SDA "connect to VDDIO via external pull-up resistor", p.9 Table 2 [F]. Optional "External Boost up to 5.5V" on VDD, p.2 Figure 1 [F] | not in the pages read |

Reading note. DRV2605L p.7 Table 6.5 values are read from the page image at TA = 25 °C, VDD = 3.6 V. The DA7280 electrical characteristics table was not reached; its only current values are the p.1 features.

## 6. Indicator LED (0603 or smaller, red or RGB)

| Field | KP-1608SRC-PRV (Kingbright) | KPT-1608LVSYCK (Kingbright) | KPTD-1608LVSECK (Kingbright) |
|---|---|---|---|
| Part number and source | "APT1608SRCPRV / KP-1608SRC-PRV" [S] (RS listing rs-online.com/web/p/leds/4663728; datasheets.com/kingbright/apt1608srcprv) | "KPT-1608LVSYCK-J3-PRV" [S] buerklin.com listing | "KPTD-1608LVSECK-J3-PF" [S] buerklin.com listing |
| Package dimensions | "1608 (0603) SMD" [S] (title; size not in the pages read) | "1608" [S]; dimensions not in the pages read | "1608" [S]; dimensions not in the pages read |
| Colour | red, 640 nm [S] | not in the pages read | not in the pages read |
| Forward voltage | 1.85 V [S] (RS listing) | not in the pages read | "on-state voltage of 1.8 V at 2 mA" [S] |
| Luminous intensity at stated current | 100 mcd at 20 mA [S] (datasheets.com and RS listings) | "20 mcd to 0.025 cd" [S]; test current not in the pages read | not in the pages read |
| Viewing angle | 120° [S] | 120° [S] | 60° [S] |
| Light-pipe guidance | not in the pages read | not in the pages read | not in the pages read |

Notes. No maker PDF was opened for any LED. RGB parts were not searched. Side-view or top-view was not determined for any part. Values are distributor-listing text only.

## Not found (summary)

- Panel outline, active area, thickness, connector pin-out, sleep current for every colour OLED candidate: not in the pages read. The module-maker sheets (buydisplay, waveshare, displaymodule, panelook) were not opened.
- Joystick: circuit diagram, waterproof rating, land pattern for SKRHABE010: not in the pages read (image-only or not reached). EVQ-Q5A05K Panasonic PDF not reached (HTTP 522).
- Tactile KXT and EVP-AA: not read (C&K URL redirected to littelfuse.com; Panasonic EVP-AA not searched).
- Vibration motors: Vybronics VG0832012 maker datasheet not reached; Jinlong, AAC, Nidec, TDK, Precision Microdrives not reached.
- Haptic: DRV2603 and DRV2625 not searched; DA7280 electrical table not reached.
- LED: no maker PDF opened; RGB LEDs and light-pipe guidance not searched.

## Conflicts

- SKRH life: [F-web] 200,000 cycles for SKRHABE010 vs [S] 1,000,000 cycles for SKRHADE010. Different variant codes; not resolved.
- VG0832012 frequency: distributor 235 Hz [S] vs Vybronics AN #022 "200 hz range" [F] (general statement, not a part value). Not resolved.
- DRV2605L quiescent current: 0.5 mA (typ, p.7) [F]; some third-party listings also say 0.5 mA [S]. No conflict.

## questions_for_owner

- Several cells are [S] (search or distributor text) because the maker PDFs were blocked (HTTP 522, 404, redirects). Is [S] acceptable for the non-read candidates, or should the lead assign a second pass for those PDFs?
- Which colour OLED size should be the primary target? The 1.1 in AMOLED 126 x 294 had no datasheet found.

## 1a. Screen addendum: total thickness and outline with bent FPC

Deciding figures per the lead. Every candidate is listed; nothing below was read from a maker outline drawing.

| Candidate | Total module thickness | Outline incl. bent FPC | Driver chip | Connector pin-out |
|---|---|---|---|---|
| SSD1331 controller (96RGB x 64) | not applicable: a driver die or COF package, not a module. COF film "35mm film" with 4 or 5 sprocket holes, p.6 [F] | not in the pages read | SSD1331 itself, p.6 [F] | not in the pages read (pin description is section 6, p.12, not read) |
| NHD-0.95-9664G (Newhaven) | not in the pages read | not in the pages read | SSD1331 [S] | not in the pages read |
| E120A390QSR (Panox, 1.19 in, 390 x 390) | not in the pages read | not in the pages read | RM69091 [S] | not in the pages read |
| 1.1 in 126 x 294 AMOLED band-type panel | NOT FOUND. Two searches returned no datasheet for this size: "1.1 inch AMOLED 126x294 bare panel flexible FPC datasheet SPI QSPI driver IC" and "1.1 inch AMOLED 126x294 band type display datasheet pin definition FPC thickness outline driver" | NOT FOUND (same searches) | NOT FOUND | NOT FOUND |

Notes. The search summary says vendor AMOLED sheets give outline as width x height x thickness for "cell+foam" and gives one 1.2 in example, "33.22 (H) x 33.75 (V) x 0.656(T)" [S]. That example is a different panel and is not used for this band-type module. It also names driver ST7801N for one 1.2 in sheet [S]; not applicable to the 126 x 294 target.

## 4a. Narrow vibration motors (strip 3.5 mm wide, 3.5 mm tall)

| Field | VZ3TH8B171700L (Vybronics, rectangular SMD) | VZ30C1T8219732L (Vybronics, rectangular SMD) | VLV041235L (Vybronics, X-axis LRA) | NFP-ELV080935 (NFP-Motor, X-axis LRA) |
|---|---|---|---|---|
| Part number and source | "VZ3TH8B171700L" [S] digikey.cn/en/products/detail/vybronics-inc/VZ3TH8B171700L/15220808 | "VZ30C1T8219732L" [S] digikey.com/en/products/detail/vybronics-inc/VZ30C1T8219732L/15220804 | "VLV041235L" [S] pr.com/press-release/629353 (press release) | "NFP-ELV080935" [S] e2e.ti.com cfs-file ...haptic_2D00_feedback_2D00_vibration_2D00_motors_2D00_NFP_2D00_ELV080935.pdf (search summary; not opened) |
| Maker datasheet read [F] | not in the pages read | not in the pages read | not in the pages read | not in the pages read |
| Width x height x length (mm) | 3.80 x 2.90 x 4.17 [S] (rectangular) | 4.40 x 3.40 x 3.75 [S] (rectangular) | 4 x 12 x 3.5 [S] (listed as "4 mm x 12 mm x 3.5 mm") | height 3.5 +/-0.05 mm [S]; width and length not in the pages read |
| Fits 3.5 mm wide strip? | No: 3.80 mm wide is more than 3.5 mm [S] | No: 4.40 mm wide is more than 3.5 mm [S] | No: 4 mm wide is more than 3.5 mm [S]; height 3.5 mm fits 3.5 mm tall | Not determined: width not in the pages read |
| Rated voltage | 2.7 VDC [S] | 2.7 VDC [S] | drive test at 1.8 Vrms [S] | 0.9 Vrms AC sine wave [S] |
| Rated current | not in the pages read | not in the pages read | not in the pages read | "Rated Current Max 145mArms" [S] |
| Resonant frequency | not in the pages read | not in the pages read | 180 Hz [S] | "rated frequency is 170 Hz", tolerance 170 +/-10 Hz [S] |
| Acceleration (G) at test mass | not in the pages read | not in the pages read | "more than 1.0 G at 1.8 Vrms" [S]; test mass not in the pages read | "Minimum acceleration is 0.52 Grms at 0.9 Vrms" [S]; test mass not in the pages read |
| Lead or pad type | not in the pages read | "solder tab termination" [S] | not in the pages read | not in the pages read |
| Drive type | not in the pages read. Series title is "Brushed DC Motor Vibration, ERM (Haptic)" [S] (the VZ30C1T8219732L DigiKey title) | ERM (brushed DC), 2.7 VDC [S] | LRA, X-axis [S] | LRA, X-axis [S] |

Notes.
- Vybronics SMD/SMT series overview [S] (digikey.fr/en/product-highlight/j/jinlong/smd-smt-reflow-solderable-vibration-motors-series): operating voltage 2.3 to 3.6 VDC, current 57 to 87 mA, 9,000 to 15,000 RPM. The series is described as reflow solderable and "not completely sealed". These are ERM (brushed) motors, not LRAs.
- Round candidates in the same series (cylindrical, not the strip shape): VZ30C1T8460002L, 4.00 mm diameter, 2.7 VDC [S]; VZ30C1T9870088L, 4.20 mm diameter, 2.3 VDC [S]. Their lengths are not in the pages read, so the 8 to 12 mm length target is not checked.
- Conflict: VZ43FC1B5640005L rated 1.3 VDC in a distributor listing [S], but a Jinlong overview gives 0.91 G peak at 3 VDC [S]. This part is 4.50 x 4.30 mm, too wide for the strip. Not resolved.
- A search summary claimed VZ30C1T8460001 is 3 mm thick and "the lowest profile". No cited line in the saved results gives that figure, so it is not used.
- Not found: a Vybronics VZ datasheet was not reached (not in the pages read). No narrow motor found fits both 3.5 mm width and 3.5 mm height with a stated rated voltage and resonant frequency.
- Not searched in this pass: 4 mm and 5 mm coin motors; Nidec and TDK narrow parts.

## questions_for_owner (addendum)

- No narrow part found meets the 3.5 mm width with a read datasheet. Should the lead accept the 4 x 12 x 3.5 mm VLV041235L (4 mm width is over 3.5 mm), or widen the strip?
- The 1.1 in 126 x 294 AMOLED band-type panel has no datasheet in search. Can the owner supply the panel's part number or the module maker's name?

RESULT: done, 6 tables and 2 addenda written; maker-page values are [F] with page or URL, distributor and search values are [S], and unreached fields say "not in the pages read" (no narrow motor fits 3.5 mm width confirmed; 1.1 in band AMOLED not found).
