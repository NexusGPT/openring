# MCU, storage, power and microphone facts for the AI ring recorder

Checked 2026-11-10 by the researcher helper. Tags: [F] = read from the maker's document (file, page, line or URL given). [F-summary] = maker's page read only through a summarizing fetch, quoted text is the fetch output, not a saved copy. [S] = search-result text only, page not opened. "not read" = not found in any page opened.

Saved copies: `design/datasheets/` (new files this run: `nrf54lm20a_szlcsc.pdf` is a Seeed board datasheet, not Nordic; `nrf54lm20_paaa_ref_schematic_0_6.pdf`; `nrf54lm20x_caaa_ref_schematic_0_2.pdf`; `nrf54lm20x_caaa_ref_pcb_0_2.pdf`; `nrf54lm20_dk_pca10184_schematic_0_5_4.pdf`; `sdnand_zetta_family_atta.pdf`; `sdnand_mk_atta.pdf` (MK family for MKDV1G/2G/4G, wrong part, see section 3); `mic_infineon_im73d122v01_en.pdf`; `npm1300_ps_v1_0.pdf` (HTML, not a PDF); `sdnand_zetta_zdsd64glgeag_r_lcsc.pdf` and `sdnand_mk_mkdv64gcl_sth_lcsc.pdf` (HTML, not PDFs). The three HTML files are failed downloads the owner should delete.
Text copies (scratchpad): `<scratch>/mcu-research/` (`paaa_schematic.txt`, `caaa_schematic.txt`, `dk_schematic.txt`, `im73.txt`, `zetta_family.txt`, `mk_family.txt`, `bom_paaa.txt`, `bom_caaa.txt`).

Key finding: the nRF54LM20A Nordic datasheet PDF was not obtained. Nordic's datasheet is HTML only at docs.nordicsemi.com (bundle ps_nrf54lm20a); the HTML body is 371,314 characters and the fetch tool returns summaries. The ball tables below come from Nordic's reference-design schematics (PDF, page 1 each), which name every ball. They are [F] reference-design facts, not the datasheet pin table.

## 1. Nordic nRF54LM20A (main chip)

### 1a. Orderable part numbers
- CSP61 (WLCSP, 61 balls): device name "nRF54LM20x-CAAA", package "WLCSP-61" in the Nordic reference BOM [F] `/…/datasheets/nrf54lm20x_caaa_ref_schematic_0_2.pdf` (BOM file `bom_caaa.txt` row U1, line 26). Package code CAAA: [F-summary] Nordic `chapters/mec_spec.html-csp61_package` page title "CSP61 (CAAA) package" (https://docs.nordicsemi.com/r/bundle/ps_nrf54lm20a/page/chapters/mec_spec.html-csp61_package?contentId=~zBrAf~tRTCM1U3DomCLTA).
- CSP98 (FCCSP, 98 balls): device name "nRF54LM20A-PAAA", package "FCCSP-98" in the Nordic reference BOM [F] `bom_paaa.txt` row U1 (line 28). Package code PAAA: [F-summary] Nordic page "CSP98 (PAAA) package" (https://docs.nordicsemi.com/r/bundle/ps_nrf54lm20a/page/chapters/mec_spec.html-csp350_package?contentId=3D1IRTFSlT91faVWUfAzxA).
- Exact orderable strings (with -R / -R7 tape suffix): not read on a Nordic page. [S] DigiKey listings: NRF54LM20A-CAAA-R7 (61-XFBGA, CSP) and NRF54LM20A-QGAA-R (listing text says 98-WFBGA) (https://www.digikey.dk/en/products/detail/nordic-semiconductor-asa/NRF54LM20A-QGAA-R/27685500 ; https://www.digikey.dk/en/products/detail/nordic-semiconductor-asa/NRF54LM20A-CAAA-R7/29209036).
- CONFLICT (open): [F-summary] Nordic `mec_spec` page lists "QFN52 (QGAA) package" (https://docs.nordicsemi.com/r/bundle/ps_nrf54lm20a/page/chapters/mec_spec.html-qfn52_package?contentId=8ZeijEW4cfe7fogtHMVlRg), while the DigiKey text tags QGAA-R as 98-WFBGA. The owner must confirm which package the QGAA code means before ordering. Owner's package choice CSP98 "PAAA" and CSP61 "CAAA" is consistent with Nordic's reference designs.

### 1b. Ball maps (CSV files, one line per ball)
- CSP61: `design/parts/nrf54lm20a-csp61-pins.csv`: 61 rows, 40 GPIO (P-named). Source per row: [F] Nordic CAAA reference schematic, U1 symbol, page 1 (`caaa_schematic.txt`, lines with U1A..U1F symbol blocks).
- CSP98: `design/parts/nrf54lm20a-csp98-pins.csv`: 98 rows, 66 GPIO (P-named). Source per row: [F] Nordic PAAA reference schematic, U1 symbol, page 1 (`paaa_schematic.txt`).
- Counts match the brief (61/40 and 98/66). Every ball in each package has a name in the reference symbol; no ball is marked "not read". CSP98: D3 and E2 have no name in the symbol. The 98 named positions equal the 98-ball count, so they are read as not balls; this is an inference from the count, not a Nordic statement.
- Limit: these are reference-design symbol labels, not the datasheet pin tables (datasheet pin figures not read: `chapters/pin.html` page names no ball rows in the summary [F-summary]).
- Alternative-function labels in the CSVs (for example "P1.05/AIN5/ASO[0]", "P1.13/CK") are printed on the PAAA schematic symbol. What "CK" and "ASO/ASI" mean is not defined in any page read: not read.

### 1c. Pin rules (what the reference schematics and Nordic pages say)
- High-speed port: "P2 is High speed port" [F] `paaa_schematic.txt` line 183; "P2 is a high speed port" [F] `caaa_schematic.txt` line 152. The P2 balls are listed in the CSV files (CSP61: 6 balls P2.00 to P2.06 region, see CSV; CSP98: P2.00 to P2.10, see CSV).
- PDM clock and data: no PDM-labelled ball in either reference symbol. PDM pin function not read (PDM electrical spec sub-page is an empty shell [F-summary] https://docs.nordicsemi.com/r/bundle/ps_nrf54lm20a/page/elspec.html-unique_6376536?contentId=QJJOutGutUQa0UtJd~McfA).
- Serial peripherals must use pins from the same port; peripherals must use GPIO pins in their own domain: [F-summary] Nordic `pin.html` (https://docs.nordicsemi.com/r/bundle/ps_nrf54lm20a/page/chapters/pin.html?contentId=GDvGIJaHX9mbw2X7e8EutQ). The dedicated clock pin list is on a linked "Clock pins" page, not read.
- USB data: CSP61 D- H6, D+ H7 (CAAA symbol); CSP98 D- K4, D+ K5 (PAAA symbol) [F] both schematics, page 1.
- Antenna: CSP61 ANT C1; CSP98 ANT E1 [F] both schematics.
- 32 MHz crystal: CSP61 XC1 A2, XC2 A1; CSP98 XC1 A2, XC2 B1 [F] both schematics.
- 32.768 kHz crystal: CSP98 P1.20/XL1 at C6, P1.21/XL2 at C7 [F] `paaa_schematic.txt` lines 371-372. CSP61 XL1/XL2 balls: the CAAA symbol does not label them (P1.20 at B6, P1.21 at B7 unlabelled): not confirmed.
- SWD: CSP61 SWDCLK D5, SWDIO E4; CSP98 SWDCLK G1, SWDIO G2 [F] both schematics.
- nRESET: CSP61 E2; CSP98 F2 [F] both schematics.
- Supply pins: CSP61 VDD at A4, E10, see CSV; CSP98 VDD at A3, A4, A9, G10, H1 (see CSV) [F] both schematics.
- Full USB/QFN reference: CSP98 also has DECUSB K6, VBUS K7; CSP61 DECUSB H8, VBUS H9 [F] both schematics.

### 1d. Reference circuit parts (from the Nordic reference BOMs, [F] `bom_caaa.txt`, `bom_paaa.txt`)
Tolerance and package as printed in the BOM description column.

| Ref | Value | Part number (Manufacturer) | Description as printed | Package | CSP61 ref design | CSP98 ref design |
|---|---|---|---|---|---|---|
| X1 | 32 MHz | CX2016DB32000D0WZRC1 (Kyocera) | XTAL SMD 2016, 32 MHz, Cl=8 pF, Tot ±40 ppm | XTAL_2016 | yes | yes |
| X2 | 32.768 kHz | 9HT11-32.768KDZC-T (TXC) | XTAL SMD 2012, 32.768 kHz, 9 pF, ±20 ppm | XTAL_2012 | yes | yes |
| L1 | 4.7 µH | MLZ1608M4R7WT000 (TDK) | Inductor, 120 mA, ±20%, 0.65 R | 0603 | yes (DC/DC) | yes (DC/DC) |
| L2 | 3.6 nH | LQP03HQ3N6B02 (Murata) | Inductor, 500 mA, ±0.1 nH, 170 mOhm | 0201 | yes | yes |
| L3 | 4.7 nH | LQP03HQ4N7H02 (Murata) | Inductor, 400 mA, ±3%, 250 mOhm | 0201 | yes | yes |
| L4 | 3.3 nH | LQP03HQ3N3B02 (Murata) | Inductor, 500 mA, ±0.1 nH, 170 mOhm | 0201 | yes | yes |
| L5 | 1.0 nH | LQP03TN1N0C02D (Murata) | Inductor, 750 mA, ±0.2 nH | 0201 | no | yes |
| C3 | 1.2 pF | GJM0335C1H1R2WB01D (Murata) | Capacitor NP0, ±0.05 pF, 50 V | 0201 | yes | yes |
| C8 | 1.0 pF | GJM0335C1E1R0WB01 (Murata) | Capacitor C0G/NP0, 25 V | 0201 | no | yes |
| C12 | 0.5 pF (CAAA) / 1.5 pF (PAAA) | GJM0335C1ER50WB01D (CAAA) / GJM0335C1E1R5WB01 (PAAA) (Murata) | C0G, ±0.05 pF, 25 V (PAAA: high Q) | 0201 | yes | yes |
| C1, C2, C5 | 100 nF | N.A. | Capacitor X7R ±10% 10 V | 0201 | yes (3x) | yes (3x) |
| C4 | 10 µF | N.A. | Capacitor X6S ±20% 6.3 V | 0402 | yes | yes |
| C6 | 4.7 µF | GRM035R60J475ME15J (Murata) | X5R ±20% 6.3 V | 0201 | yes | yes |
| C7, C14 (CAAA C7 2.2 µF; PAAA C7 not mounted) | 2.2 µF | GRM033D80E225ME47D (Murata) | X6T ±20% 2.5 V | 0201 | yes | yes (C14) |
| C10 | 2.2 µF | GRM033R61A225KE47 or GRM033D80E225ME47D (Murata) | X6T ±20% 2.5 V | 0201 | yes | yes |
| C11 | 4.7 µF | GRM155R61A475MEAAD (Murata) | X5R 10 V | 0402 | yes | yes |
| C13 | N.C. (not mounted) | N.A. | Not mounted | 0201 | yes | yes |
| FB1 | 120 R at 100 MHz, 0.2 A | BLM03AG121SN1D (Murata) | Ferrite bead, 500 mOhm max | 0201 | yes | yes |
| R1 | 2.2 ohm | N.A. (CAAA) / RES 2.2 ohm 1% 1/10 W (PAAA) | Resistor | 0603 | yes | yes |
| R2 | 220 R (CAAA) / 200 R (PAAA) | N.A. | Resistor ±1% 0.05 W | 0201 | yes | yes |

Designator-to-net mapping for the USB supply caps (which cap sits on VDD_USB_3V3 or DECUSB) is not read at designator level in the text copy: not read.
Source files: `bom_caaa.txt` lines 11-28; `bom_paaa.txt` lines 11-30.

### 1e. Stack-up and land pattern
- Not found. The reference PCB PDF (`nrf54lm20x_caaa_ref_pcb_0_2.pdf`) is a picture, text layer has no stack-up or pad dimensions (`caaa_pcb.txt`, 2 KB). The Altium PcbDoc files are binary and were not parsed. The datasheet "Table 1. Package dimensions" (CSP61) and "Table 2" (CSP98) are summarized by fetch only: CSP61 nominal D about 3.017 mm, E about 2.431 mm, ball diameter nominal about 0.325 mm; CSP98 nominal D 3.67 mm, E 3.85 mm, e 0.35 (not labelled), b 0.22 (not labelled) [F-summary] (CSP61 and CSP98 mec_spec pages above). Land pattern and solder mask values: not read.

### 1f. Electrical specification
- Not found. The current-consumption, PDM, USBHS, SPIM and regulator sub-pages are empty shells in the fetch [F-summary] (elspec pages via https://docs.nordicsemi.com/r/bundle/ps_nrf54lm20a/page/elspec.html?contentId=WEqIr4EWeY_Qfff_2KNTPA). The full table is in the HTML body not reachable by the summarizing fetch. Supply range, CPU current from NVM, PDM current, SPI/USB current, radio TX/RX current, System ON idle, System OFF and GRTC sleep current: not read.
- Board-level only (not chip): Seeed XIAO nRF54LM20A datasheet states 4.76 uA deep sleep under BAT power and 3.87 mA average with TX +8 dBm, measured on a board with nPM1300 [F] `/…/datasheets/nrf54lm20a_szlcsc.pdf` page 3. Not a chip figure.

### 1g. High-speed USB supply
- The reference schematics show VBUS (CSP61 H9, CSP98 K7), DECUSB (H8, K6) and a net VDD_USB_3V3 with the note "VDD:nRF supplied by 1.8 V to 3.6 V, DC/DC Enabled" [F] `caaa_schematic.txt` lines 114, 152 and page 1 title block. Whether USB needs its own supply pin and the required VBUS/VDD_USB voltage: not read (USBHS electrical spec sub-page empty [F-summary]).

## 2. Nordic nRF54LM20 DK

- Hardware files page: https://www.nordicsemi.com/Products/Development-hardware/nRF54LM20-DK/Hardware-files [F-summary]. Listed zips: 0_7_0 https://nsscprodmedia.blob.core.windows.net/prod/software-and-other-downloads/dev-kits/nrf54lm20-dk/nrf54lm20-dk---hardware-files-0_7_0.zip ; 0_5_4 https://nsscprodmedia.blob.core.windows.net/prod/software-and-other-downloads/dev-kits/nrf54lm20-dk/nrf54lm20-dk---hardware-files-0_5_4.zip ; 0_3_4 (same pattern, 0_3_4). The page says the schematics, layout, BOM and Gerber files are inside those zips.
- Downloaded 0_5_4 (board PCA10184). Schematic PDF: `design/datasheets/nrf54lm20_dk_pca10184_schematic_0_5_4.pdf` (19 pages, from zip path "Schematic_Layout pdf files/PCA10184_Schematic_And_PCB.pdf"). Compatibility: 0.3.4 and 0.5.4 use nRF54LM20A; 0.7.0 uses nRF54LM20B [S] (search summary of docs.nordicsemi.com compat matrix). Version 0.7.0 is the B part, not used.
- Crystal and inductor values from the schematic text (`dk_schematic.txt`): 32 MHz crystal (line 429), 32.768 kHz crystal (line 241), 4.7 µH (line 233), antenna match 3.6 nH, 4.7 nH, 3.3 nH (lines 387-391), 1.0 nH (line 716).
- Part numbers of the two crystals, the DC/DC inductor and the antenna match parts: not read. The DK BOM (`nRF54LM20-DK_BOM.xls`, in the zip folder BOM/) is an Excel 97 file and the design venv has no xlrd; the BIFF string extraction did not return the part rows. Not installed (no packages added). Next step: parse the xls with an installed reader.

## 3. SD NAND, 64 Gbit (8 GB), LGA-8

Note: 64 Gbit = 8 GB (correct).

### 3a. Zetta ZDSD64GLGEAG-R
- Datasheet read: Zetta ZDSD08G/16G/32G/64G family, 16 pages (`sdnand_zetta_family_atta.pdf`). The family list names ZDSD64GLQEAG-R, package LGA8x2 9x10 mm (line 79). ZDSD64GLGEAG-R is not in this datasheet: not found in this document. [S] LCSC lists ZDSD64GLGEAG-R as LGA-8 (6.2x8) 2.7 V to 3.6 V (https://www.lcsc.com/product-detail/C5277948.html).
- Package drawing and pad dimensions: not read for the GEAG part.
- Pin table: SD mode and SPI mode pin names read (page 4, lines 116-130; numbers are in an image, not read as text). Pin numbers: not read.
- Supply range: VDD 2.7 V to 3.6 V (DC characteristics, lines around 254-256). NAND area VCC 3.3 V required (line 51-52).
- Standby current: ICC1 0.17 mA typ, 0.2 mA max at VDD = 3.3 V, clock stopped, 25 C (lines 289-296). Read current and write current: TBD in the datasheet (ICC2 "TBD", lines ~298-305).
- Bus modes: SD 1-bit/4-bit ("Support 1/4 bit mode", line 97) yes; SPI mode yes (section 6.2.2, lines 224-229: enters SPI on CS low during CMD0; returns to SD only by power cycle).
- Maximum clock: 200 MHz on SD3.0 interface for 32Gb and 64Gb (line 96); 50 MHz on SD2.0 interface for 8Gb and 16Gb (line 105).
- Speed class: class 4, 6, 8, 10 supported (line 99).

### 3b. MK-Founder MKDV64GCL-STH
- Datasheet: the saved file `sdnand_mk_atta.pdf` (21 pages) is "MK SD NAND Product Datasheet", product list MKDV1GCL-ABB, MKDV2GCL-ABB, MKDV4GCL-ABB (page 1, Rev 1.4 2023/05/10). It does NOT cover MKDV64GCL-STH. Not used for values.
- Second source: sekorm copy of a combined MKDV32GCL-STH / MKDV64GCL-STH datasheet https://en.sekorm.com/doc/527569136.html returned HTTP 457 to the fetch tool: not read.
- [S] LCSC: MKDV64GCL-STH, 2.7 V to 3.6 V, 208 MHz, 64 Gbit, LGA-8 (6x8) (https://www.lcsc.com/product-detail/C5444290.html). [S] search text of a Chinese copy: LGA-8 package, 1.8 V/3.3 V IO, up to 208 MHz, SD protocol, SPI mode, HW ECC (https://datasheet.lcsc.com/lcsc/2304071000_MK-MKDV64GCL-STH_C5444290.pdf, not opened; saved copy is HTML).
- SPI mode for MKDV64GCL-STH: [S] only (search text). Not read in a maker document.
- Package drawing, pin table, read/write/standby current, speed class: not read.

## 4. Power chip (nPM1300, nPM1304)

- Datasheet PDF link https://infocenter.nordicsemi.com/pdf/nPM1300_PS_v1.0.pdf returned HTML (5,772 bytes), saved as `npm1300_ps_v1_0.pdf` (not a PDF). Not read.
- [S] search summary (https://docs.nordicsemi.com/r/bundle/ps_npm1300/page/product_overview.html and https://www.nordicsemi.com/nPM1300?ref_d=ps), not opened:
  - Linear charger current 32 to 800 mA (charge current range); termination voltage 3.5 V to 4.45 V.
  - Two buck regulators, 1.0 to 3.3 V in 100 mV steps, 200 mA each, auto or forced PWM.
  - LDO 50 mA; load switch 100 mA.
  - Ship mode quiescent 370 nA; battery quiescent 600 nA or 800 nA depending on the version (versions conflict).
- Not found: charge current step size, nPM1300 CSP (3.07 x 3.07 mm) and QFN (5 x 5 mm) drawings and pin tables, fuel gauge function details, reference circuit inductor values, nPM1304 (not searched in this run).
- Only package reference seen: NPM1300-CAAA-R7 listed as WLCSP-35 (2.4 x 3.1) [S] https://www.lcsc.com/product-detail/C25346894.html. This does not confirm the 3.07 mm CSP.
- Open conflict: the battery quiescent current differs between versions (search text) and must be checked in the latest datasheet.

## 5. Infineon IM73D122V01 PDM microphone (datasheet already in core.md, copy: `mic_infineon_im73d122v01_en.pdf`, text `im73.txt`)

- Pin table: Table 9 "IM73D122V01 pin configuration" (`im73.txt` line 857): pin 1 DATA (PDM data output), pin 2 VDD (power supply), pin 3 CLOCK (PDM clock input), pin 4 LR (PDM left/right select), pin 5 GND (ground). [F]
- Land pattern dimensions: not read. Figure 13 "IM73D122V01 footprint and stencil recommendation" (page 12) is a drawing; no numbers in the text layer. Pads are solder-mask defined per the text (`im73.txt` lines 887-900). [F]
- Sound port hole: "A PCB sound port size of radius 0.4 mm (diameter 0.8mm) is recommended" [F] `im73.txt` line 889-890.
- Clock modes and PDM clock ranges [F] (`im73.txt` lines 536-575):
  - Standby mode: fclock up to 350 kHz (line 541-542).
  - Low Power mode: 450 / 768 / 850 kHz (min/typ/max) (lines 546-547).
  - Normal mode: 1.2 / 1.536 / 1.65 MHz (line 553).
  - High Performance mode: 2.0 / 2.4 / 2.6 MHz and 2.9 / 3.072 / 3.3 MHz (lines ~557-565).
  - Ultrasonic mode: 4.56 / 4.8 / 5.04 MHz (line 572).
- Current at each PDM clock mode [F] (`im73.txt` lines 648-672; values printed as two numbers per row, the text layer does not show which column each sits in: column assignment not read):
  - Clock off (CLOCK low): Iclock_off 1 uA (line 648-649).
  - Standby mode, no load on DATA: Istandby 25 and 50 uA (lines 653-654).
  - fclock 768 kHz: IDD 280 and 310 uA, no load on DATA (line 659 onward; one line each for 768 kHz, 1.536 MHz, 2.4 MHz, 3.072 MHz, 4.8 MHz).
  - Other printed pairs: 1.536 MHz 690 and 770 uA; 2.4 MHz 750 and 945 uA; 3.072 MHz 980 and 1120 uA; 4.8 MHz 900 and 1000 uA (<5 pF load on DATA, lines 660-672).
  - Column ambiguity: the datasheet lists Min/Typ/Max; the text layer drops one column. Verify the column with the PDF page 9 before using a value.
- Left or right select rule: the LR pin (pin 4) selects the channel; "data is transmitted alternately according to the L/R pin status of each microphone" [F] `im73.txt` line 818. Polarity (which LR level is left) is in a timing figure not read in text. Test conditions state "select pin grounded" (line 330). Stereo configuration with two mics on one bus, same power mode for both (line 816-820).

## Not found (summary)
- Nordic datasheet pin tables, PDM pin function, dedicated clock pin list, electrical specification (all current tables), USB supply rule: not read (datasheet HTML sub-pages summarized as empty).
- Land pattern and stack-up for the CSP61 and CSP98: not read.
- DK crystal, inductor and antenna part numbers: not read (xls not parsed).
- nPM1300 package drawings, pin table, reference inductor values: not read. nPM1304: not searched.
- Zetta ZDSD64GLGEAG-R package drawing and pin numbers: not read.
- MKDV64GCL-STH datasheet: not read (only LCSC and search text).

## questions_for_owner
1. Which package does the QGAA code mean (QFN52 per Nordic mec_spec page, 98-WFBGA per DigiKey text)? Check before ordering.
2. Accept the reference-design ball maps (CSV) as the ball source until the Nordic datasheet PDF is obtained? The datasheet is HTML only in this run.
3. Should the SD NAND be the GEAG (LGA-8 6.2x8 per LCSC) or the family LQ (9x10 mm) part? Datasheet only covers the LQ part.

RESULT: done, sections 1, 2, 3, 5 partly read and section 4 search-only; the CSV ball maps and reference BOM are from Nordic reference designs, and the datasheet electrical tables, nPM1300 datasheet and MK 64 Gbit datasheet were not read.
