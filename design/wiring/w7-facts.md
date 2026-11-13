# W7 facts: eleven open items of the ring recorder circuit

Run: started 23:42:45 CET on 2026-11-12 (date command). Last check 23:51 CET.
Page numbers are PDF page numbers, read from text copies or rendered pages. Scratch text copies sit in `<scratch>/w7/`.

Web fetches made in this run (all maker sites, no login, no form, no name in the request):
- Nordic `docs.nordicsemi.com` USB pins page (WebFetch, 4 windows). Raw page not saved: curl returned HTTP 403.
- Knowles `knowles.com/docs/default-source/model-downloads/spk0641ht4h-1-rev-a.pdf`: curl saved a 212-byte block page as `design/datasheets/w7_knowles_spk0641ht4h-1-rev-a.pdf`. That file is not a datasheet. WebFetch returned an empty page. The file was left in place (nothing is deleted).
- Knowles copy at lcsc.com (WebFetch): returned the LCSC home page.
- WebSearch for the nRF54LM20A current draw: one lead (see Q9), not used.

---

## Q1. Item 22: nRF54LM20A USB D+ and D- when VBUS is absent

**Answer: in part.** No file on disk says what D+ and D- do when VBUS is absent.

- Nordic product specification, page "USB pins" (WebFetch, not saved raw). URL: https://docs.nordicsemi.com/r/09E6cV_58cJ3mJAVA8IpZA/bSNY8d3UPpw~8PVO42XXjA
  - "Signal pins connect to the USB device and consist of the D+ and D- pins." (body, signal pins section)
  - "These are dedicated pins and not available as standard GPIO pins."
  - "meaning these pins are not 5 V tolerant."
  - The signal pins are operational when "The device is powered", "VBUS is in the valid voltage range", and "USBHS is enabled by the software driver".
  - The fetch found no statement of high impedance, pull state, or maximum voltage on D+ and D- when VBUS is absent.
  - Caveat: these are the fetch tool's quotes, not checked against a saved copy.
- Nordic files on disk for nRF54LM20 (no USB chapter in any of them):
  - `design/datasheets/nrf54lm20_dk_pca10184_schematic_0_5_4.pdf` (DK schematic, nets USB_nRF54_D- and USB_nRF54_D+).
  - `design/datasheets/nrf54lm20_paaa_ref_schematic_0_6.pdf` (reference schematic, nets USB_D_N and USB_D_P, page 1).
  - `design/datasheets/nrf54lm20x_caaa_ref_schematic_0_2.pdf` (reference schematic, nets USB_D_N and USB_D_P, page 1).
  - `design/datasheets/nrf54lm20x_caaa_ref_pcb_0_2.pdf` (reference PCB, 14 pages).
  - `design/datasheets/bench_nrf54lm20-dk-hw-ug-v0.3.4.pdf` is an HTML page with a .pdf name. A search for "usb" in it found no hit.
  - `design/datasheets/nordic-web/lm20a_pdm.txt` is a script bundle. No USB text.
- Not Nordic: `design/datasheets/nrf54lm20a_szlcsc.pdf` is the Seeed XIAO board page (6 pages).
- Other Nordic-branded or other files for a different chip: `design/datasheets/mcu_farnell_4424294.pdf` (nRF54L15 DK hardware guide v0.9.1, not LM20A). `design/datasheets/mcu_nrf54l15_ds_v2.2.pdf` (26 pages, copyright line names IndieSemiC Private Limited, not LM20A).
- Document that would hold it: the Nordic nRF54LM20A product specification, USB pins section (online). No copy is on disk.

## Q2. Item 24: CSNP32GCR01-BOW supply limit and VDD_SD capacitors

**Answer: in part.** The CS datasheet gives the supply range and a 2.2 uF recommendation. It gives no maximum capacitance.

- CS Semiconductor CSNP32GCR01-BOW datasheet, V1.0: `design/datasheets/slim2_cs-sdnand-20230403.pdf`.
  - Page 4: "Power supply: Vcc = 2.7V - 3.6V".
  - Page 11, section 6 reference design: "It is recommended to have 2.2uF capacitance on VCC."
  - No maximum VCC capacitance and no inrush note found in this file (search of the text for uF, inrush, capacit, ramp).
- Other CS and storage files on disk, not the BOW part:
  - `design/datasheets/slim_cs-csnp32gcr01-bow.pdf` is an HTML page with no datasheet data.
  - `design/datasheets/slim2_cs-csnp32gcr01-20240724.pdf` is the CSNP16GCR01-AOW datasheet (V1.1).
  - `design/datasheets/slim2_cs-csnp32gcr01-20240730.pdf` is a Hanhai SD NAND spec (128 MB to 512 MB).
  - `design/datasheets/slim2_cs-csnp32gcr01-20260408.pdf` is an XTX datasheet (title "XTSDx0xG"), not CS.
- The 5 uF figure comes from the XTX file, page 16: "CC(2) Capacity connected to power line 5 uF To prevent inrush current." Footnote 2 on the same page: "card maximum capacitance between VDD-VSS is defined as 5uF." That is another maker's part, as the deferred item says.
- VDD_SD capacitors in `design/ecad/ring/netlist.csv` (lines 349 to 352) and `design/ecad/ring/parts.csv`:
  - C60, 4.7 uF, MPN GRM155R60J475ME47D (parts.csv line 64).
  - C61, 100 nF (parts.csv line 65).
  - C82, 100 nF (parts.csv line 59).
  - C87, 1.0 uF (parts.csv line 30).
  - Sum: 4.7 + 0.1 + 0.1 + 1.0 = 5.9 uF. This matches sch-notes.md line 277.
  - Pull-ups R60, R63, R64, R65 (47 kohm) are on the same net (netlist lines 353 to 356). They are not capacitors.
- Document that would hold the maximum: CS Semiconductor storage spec for CSNP32GCR01-BOW, a newer revision than V1.0 if one exists. None on disk.

## Q3. Item 25: Knowles microphone capacitor note and VDD_MIC capacitors

**Answer: in part.** The Knowles sentence is not on disk and was not found online. The VDD_MIC capacitors are listed.

- Knowles SPK0641HT4H-1 datasheet: not on disk.
  - `design/datasheets/slim_knowles-sph0690lm4h-1.pdf` is a Knowles 404 page.
  - `design/datasheets/slim_knowles-everest-miconflex-brief.pdf` is an access-denied page.
  - A text search of all files in `design/datasheets` for "Class 2 dielectric" and "SPK0641" found no Knowles file that holds either.
  - Online: knowles.com (curl) returned a block page, and WebFetch of the same URL returned an empty page. The LCSC copy returned the LCSC home page.
- The sentence that the project cites: sch-notes.md line 226 (cites "Knowles sheet 4" and quotes "Capacitors near the microphone should not contain Class 2 dielectrics"). It is not verified: no file on disk holds it.
- Document that would hold it: Knowles SPK0641HT4H-1 datasheet, sheet 4 (Figure 4 and its notes), as cited by the project.
- Capacitors on VDD_MIC (`design/ecad/ring/netlist.csv` lines 340 to 344):
  - C31, 1 uF, MPN GRM033R60J105MEA2D (parts.csv line 50). parts.csv has no dielectric field. sch-notes.md line 226 says "X5R".
  - C32, 1 uF, same MPN (parts.csv line 54). X5R per sch-notes.md line 226.
  - C35, 100 nF, value text "100nF Class 1" (parts.csv line 51). Dielectric: Class 1.
  - C36, 100 nF, value text "100nF Class 1" (parts.csv line 55). Dielectric: Class 1.
  - C86, 1.0 uF, no MPN, no dielectric (parts.csv line 29; netlist line 344).
  - Sum: 1 + 1 + 0.1 + 0.1 + 1.0 = 3.2 uF.
  - bom-notes.md line 84 says "C35,C36 must be Class 1 dielectric (Knowles sheet 4)."

## Q4. Item 27: design risks, ring and case

**Answer: in full.** The deferred item says "six". The files hold more: case has 9 numbered risks, ring section 9 has 4 numbered items plus one summary line.

Ring `design/ecad/ring/sch-notes.md`:
- Section 7 is titled "Conflicts in the architecture", not design risks. Its 7 items:
  - L76: RT1 position conflict (architecture lines 290 and 439).
  - L77: protection "at the contact board" (architecture line 284) has no contact board.
  - L78: MIC_B_CLK, MIC_B_DATA, JOY_CENTER spare test pads (architecture lines 181 to 182, 199, 373, 374, 450).
  - L79: microphone LR pin rule (architecture line 281) against the Select pin of the A5 part.
  - L80: flex strip 6 or 7 lines (architecture lines 369 and 439).
  - L81: JOY lines with no pull-ups or protection (brief).
  - L82: brief cites "slim.md section 5.1" for IM68D128B pins, which is the IM68D121J brief.
- Section 9 "Design risks an electronics engineer must review" (heading at L91):
  - L93: items 1 to 9 of the A3 list stand. Their text is in `evidence/a5/sch-notes_before.md` section 9, which was not read in this run.
  - L95: item 10, charger at 15 mA and 4.35 V until Grepow states the limit.
  - L96: item 11, USB D+ and D- run through the flex tail and J_BAND_B pads 5 and 6; VBUS ESD part U9 sits at the board end.
  - L97: item 12, storage pads 1 and 7 are RSV in SPI mode; W3 pulls them to VDD_SD.
  - L98: item 13, centre press SW2 under the round cap; second choice is two switches within 40 ms.

Case `design/ecad/case/sch-notes.md`, section 7 "Design risks an electronics engineer must review" (heading L76):
- L78: ESD part on VRING, TPD4E05U06 allows 5.5 V maximum on a pin.
- L79: U2 D+/D- left open; TI allowance is open item S5.
- L80: PMID load while charging from USB (supplier item S5).
- L81: full-speed USB host over spring pins and 30 AWG wires; no series resistors on D+/D-.
- L82: strapping pins IO3, IO45, IO46 left open.
- L83: green and blue LEDs dim from 3V3 through 150 ohm (bench B4).
- L84: TS window with RT1 5.23 k and RT2 30.1 k: check the JEITA window.
- L85: BQ25895 CE pulled low by R21: charging starts without firmware.
- L86: TPS63802 MODE on GND for power save.

Mismatch: `design/wiring/deferred-items.md` row 27 cites "six" risks at case L76 and ring L91. The count in the files is 9 (case) and 4 plus 1 summary (ring).

## Q5. Item 33: band pads, VBUS, USB, GND and the nPM1304 VBUS pin

**Answer: in part.** The netlist answers the pads. The nPM1304 gives the pin type and the absolute maximum. No VBUS leakage figure is stated.

Ring netlist (`design/ecad/ring/netlist.csv`):
- J_BAND_B pads (the four charging pads on the inside of the band):
  - Pad 4, VBUS (line 304).
  - Pad 5, D- on net USB_DN (line 285).
  - Pad 6, D+ on net USB_DP (line 289).
  - Pad 7, GND (line 95).
  - Other pads of J_BAND_B: pad 1 CELL+ on VBAT (line 296), pad 2 CELL- on GND (line 94), pad 3 NTC (line 189).
- Protection part U9, TPD4E05U06 (parts.csv line 97):
  - Pin 1 D1+ on USB_DP (line 291). Pin 2 D1- on USB_DN (line 287).
  - Pins 4 and 5, D2+ and D2- on VBUS (lines 308 and 309).
  - Pins 3 and 8, GND (lines 134 and 135).
  - Pins 6, 7, 9, 10, no connect (lines 396 to 399).
- Other parts on the four nets:
  - VBUS: C71 (line 301), C72 (line 302), test pad CP1 (line 303), R1 pin 1 (line 305), U2 pins B1 and B2 (lines 306 and 307).
  - R1 is 2.2 ohm (parts.csv line 13). Its pin 2 goes to net U1_VBUS (line 282), on U1 pin H9 (line 283).
  - USB_DN: test pad CP2 (line 284), U1 pin H6 (line 286). USB_DP: test pad CP3 (line 288), U1 pin H7 (line 290).
  - No switch part appears on the VBUS, USB_DN, USB_DP or GND lines above.

nPM1304 datasheet (`design/datasheets/npm1304_datasheet_v1_0.pdf`):
- Pin type: VBUS is typed "Power", function "Input supply" (page 151, pin 21; page 153, balls B1 and B2). VBUSOUT is a separate analog output (page 151, pin 22; page 153, ball C3).
- Voltage on VBUS with no charger: no nominal value is given. Absolute maximum "VBUS Power (relative to pins AVSS, PVSS1, and PVSS2)" is -0.3 V to 22 V (page 12, Table 4). The device runs from the battery when "VBUS=0 V" (page 11). VBUSOVP is 5.5 V (page 17).
- Leakage current: not stated. Only Figure 42 (page 74) mentions leakage, and it is for the LDO.

## Q6. Item 41: motor supply values

**Answer: in full.**

Stated values (maker documents):
- Jinlong W0525AB001D spec, `design/datasheets/slim2_jinlong-w0525ab001d.pdf`, page 6:
  - Rated current: "Below 80 mA" (item 3-1-4).
  - Starting current, rotor held at operating voltage: "Below 175 mA" (item 3-1-5).
  - Starting voltage: "Below DC 2.5V" (item 3-1-6).
  - Rated voltage DC 3.0 V (page 6, item 3-1-1).
- TI TLV75530P (`design/datasheets/motor_tlv755p.pdf`):
  - Output current limit ICL, page 5: 560 mA min, 720 typ, 865 max, for VOUT = 0.9 x VOUT with 1.5 V < VOUT ≤ 4.5 V.
  - Dropout VDO at 500 mA, page 6, second table block (TJ -40 °C to +125 °C): 2.5 V ≤ VOUT < 3.3 V, 325 mV max. The first block (TJ -40 °C to +85 °C) gives 300 mV max for the same range.
- Nordic nPM1304 (`design/datasheets/npm1304_datasheet_v1_0.pdf`), page 29, IBATLIM "Discharging battery current limit": 100 in the Min column (superscript 1), checked on the rendered page. Footnote 1 on page 30: "Validated through simulation." No typ or max value.

Estimates in `design/ecad/motor-drive/motor-drive.md`:
- Line 13: "ESTIMATE: current taken as proportional to voltage at stall". This gives 145.8 mA and 364.6 mW at 2.5 V.
- Line 12: 90 % converter efficiency, marked ESTIMATE.
- Line 48: dropout taken as 0.65 ohm, marked ESTIMATE. From it: 113.8 mV at a start and 52 mV running. These are estimates, not datasheet values.
- Line 153: start time of 10 ms, marked ESTIMATE. The 190 ms bound comes from another part (INEED C0620BLDCL27). The W0525 spec gives no start time.
- Line 51: the 10 uF capacitor value uses an ESTIMATE of X5R derating.

## Q7. Item 47: W1 to W12, B1 to B6, F1 to F5 status

**Answer: in full.** Every item is in the current files. The list in `design/ecad/motor-drive/reply.txt` line 9 ("not made") is out of date.

Netlist and parts (`design/ecad/ring/`):
- W1: netlist.csv line 363, "VMOT,J_BAND_A,7,MOT+". make_netlist.py line 134 reads ('VMOT', 'MOT+', 'A'). Made.
- W2: netlist.csv line 92, "GND,J_BAND_A,6,MOT-". make_netlist.py line 133. Made.
- W3: parts.csv line 87 (M1, W0525AB001D). netlist.csv lines 364 (VMOT, M1 +) and 96 (GND, M1 -). Made.
- W4: no D1 row in parts.csv. make_netlist.py line 390 records "motor diode removed". Made.
- W5: no Q1 row in parts.csv. make_netlist.py line 389 records "motor switch removed". Made.
- W6: netlist.csv line 182 (MOTOR, R61 pin 1) and line 184 (MOT_EN, R61 pin 2). Made.
- W7: netlist.csv line 185 (MOT_EN, R62 pin 1) and line 98 (GND, R62 pin 2). Made.
- W8: U11 TLV75530P: netlist.csv line 186 (MOT_EN, U11 pin 3 EN), line 297 (VBAT, U11 pin 4 IN), line 365 (VMOT, U11 pin 1 OUT), lines 116 and 117 (GND). parts.csv line 88. C83: lines 294 (VBAT) and 79 (GND). C84: lines 362 (VMOT) and 80 (GND). Made.
- W9: make_netlist.py line 355 carries the new R61 and R62 labels. Made.
- W10: `design/ecad/ring/additions.csv` line 7 (R61 text). Made.
- W11: additions.csv line 8 (R62 text). Made.
- W12: additions.csv lines 9 to 11 (U11, C83, C84). Made.

Bill of materials (`design/bom.csv`):
- B1: no Q1 row (search ",Q1," finds none). Made.
- B2: no D1 row, no NSR0230 row (searched). Made.
- B3: bom.csv line 45 (U11 motor regulator). Made.
- B4: bom.csv line 46 (C83, C84, 10 uF). Made. Since 2026-11-13 C84 is 4.7 uF on its own parts list row.
- B5: bom.csv line 44 (M1 row) reads "S21 closed by design/ecad/motor-drive/motor-drive.md". Made. Note: architecture.md line 519 still reads "still open" for S21. That line was not in the W/B/F list.
- B6: bom.csv line 62 ("Motor regulator enable series resistor 100 ohm", R61) and line 63 (R62 pull-down 100 kohm). Made.

Firmware (`design/firmware.md`):
- F1: section 3.1 line 314 carries the new drive text (U11, VMOT, R61, R62). The old text "through Q1" remains only in line 39, a history note. Made.
- F2: line 331 "from the cell through U11, outside the power chip's 100 mA battery limit". Made.
- F3: line 332 "Motor charge for the fuel gauge (motor-drive.md section 2.8 change F3)". Made.
- F4: line 83 (peripheral table) "(motor-drive.md, regulator U11)". Made.
- F5: line 1028 (T-MOTOR) "motor-drive.md change F5 ... VBAT drops during the pulse". Made.

## Q8. Item 65: nPM1304 charge settings and cell.md

**Answer: in full.**

nPM1304 (`design/datasheets/npm1304_datasheet_v1_0.pdf`):
- Charge current ICHG: "The charge current limit is set between 4 mA and 100 mA in 0.5 mA steps" (page 24, section 6.2.3). Table on page 29: ICHG range 4 to 100 mA, ICHGSTEP 0.5 mA. Default 4 mA (page 35, BCHGISETCHARGE).
- Termination voltage VTERM, page 29: 3.60 V, 3.65 V, and 4.00 to 4.65 V, step 50 mV (VTERM_STEP). Register list, page 36 (BCHGVTERM options 3V60 to 4V65): "4V35 9 4.35 V". Yes, 4.35 V is one of the options. Default 4.0 V (page 36).
- Termination current: 10 % (default) or 5 % of ICHG (page 24; page 29).

cell.md (`design/mfg/specs/cell.md`):
- L40: charge voltage 4.35 V (source "Grepow"). The charger terminates at 4.35 V.
- L41: charge current 15 mA, "0.85 C of the smallest cell, 17.6 mAh". The charger ends at 10 % of it.
- L42: capacity lowest 17.6 mAh (US 7), source "Grepow", at 325.8 mm3.
- L43: capacity highest 31.9 mAh (US 13), source "Grepow".
- L44: peak discharge up to 228 mA for the instant of a motor start, "open item S12: Grepow confirms".
- L45: running discharge about 4.1 mA recording.
- L74 (open point 6): "Capacity 17.6 to 31.9 mAh is a calculation from volume ... not a maker figure." This conflicts with the "Grepow" source label in L42 and L43. Flagged for the lead.
- L72 (open point 4): Grepow must confirm the 15 mA and the 4.35 V termination.

## Q9. Item 66: power budget estimates, architecture.md lines 88 to 94

**Answer: in part.** The rows marked "estimate" are listed below. Maker values were found for the storage part and the nPM1304. None was found for the nRF54LM20A or the radio.

Rows of `design/architecture.md` (table at lines 88 to 94, text notes at lines 96 to 99):
- L89, Main chip recording: "3.0 mA at 1.8 V, estimate, not from a datasheet". Standby L89: "0.005 mA, estimate". Not found on disk: no nRF54LM20A product specification is on disk. The two Nordic nRF54L15 and farnell files are for other chips. Online: the Nordic product specification's current section was not reached. A WebSearch lead cited 2.6 mA for a CoreMark run at 128 MHz from a Nordic blog about the "nRF54L series". Voltage not stated. Not this chip. Not used.
- L90, Storage averaged, recording: "0.3 mA at 3.0 V, estimate". Maker values in `design/datasheets/slim2_cs-sdnand-20230403.pdf` page 8: standby current ISTBY "150 200 μA" (column headers not readable in the text copy). Operation current IOP "15 25 mA", condition "3.3v@50MHz (Write)". The 0.3 mA average is not a maker value. Page 4 also says "Standby Current: < 200uA".
- L93, Radio advertising: "0.02 mA, estimate". Not found on disk (same reason as main chip).
- L94, Power chips recording: "0.05 mA, estimate". nPM1304 page 11 quiescent rows: IQSHIP 370 nA; hibernate 500 nA; battery operation, all BUCKs and LDOs disabled, VBUS disconnected, 600 nA; one BUCK in Auto mode, no load, 800 nA; both BUCKs in Auto mode, 1100 nA; one BUCK in PWM mode, 4.0 mA; both BUCKs in PWM mode, 7.1 mA. No row at 0.05 mA. Standby L94 (0.002 mA) is not marked as an estimate and has no matching row.

Not marked as estimate, for reference:
- L88 microphones: "0.69 mA [DS, figure at 1.536 MHz]". Not checked in this run.
- L92 screen off: "0.001 mA [DS, same glass]". The display sheet's Ivdd row is blank (see Q10).

## Q10. Item 68: screen VCI and IOVCC current, and their rails

**Answer: in part.** The display sheet gives the VCI and IOVCC voltages. It gives no current for either pin. The rails are answered.

- Tailor Pixels TOH095XVT-01, `design/datasheets/display_TOH095XVT-01.pdf` (18 pages):
  - Page 6: pin 4 "VCI ... VCC2.7~3.6V"; pin 5 "IOVCC ... 1.65~3.3V".
  - Page 7, section 7 DC characteristics, row "Current Consumption", items "Normal display" (mA) and "Standby mode" (uA), symbol Ivdd. The rendered page shows all min, typ and max cells blank. The row is named Ivdd, not VCI or IOVCC.
  - A second copy, `design/datasheets/slim_tailor-toh095xvt-01.pdf`, has the same text on pages 6 and 7.
  - Not found: a VCI or IOVCC current.
- Netlist rails:
  - VCI is on net VDD_3V0: DISP1 pin 4 (`design/ecad/ring/netlist.csv` line 335) and J1 pin P4 (line 336).
  - IOVCC is on net VDD_1V8: DISP1 pin 5 (line 319) and J1 pin P5 (line 320).
- nPM1304 source of each rail:
  - VDD_3V0 is driven by U2 pin C6, VOUT2 (netlist line 339). nPM1304 page 153: "C6 VOUT2 Power BUCK2 output". So the VCI rail is BUCK2 output. The same net also feeds U2 pin B5 LSIN2/VINLDO2 (line 338).
  - VDD_1V8 is driven by U2 pin B6, VOUT1 (netlist line 332). nPM1304 page 153: "B6 VOUT1 Power BUCK1 output". So the IOVCC rail is BUCK1 output.
- Document that would hold the current: a current table in the TOH095XVT-01 product specification. None on disk gives it.

## Q11. Item 69: nPM1304 default cut-off and settable values

**Answer: in full.**

- nPM1304 page 109, "System features":
  - VSYSPOF falling threshold: minimum setting 2.5 V; default setting 2.7 V; maximum setting 3.4 V.
  - VSYSPOF rising threshold, default: 100 mV above the falling threshold, 2.8 V.
- nPM1304 page 29:
  - VBATBOR, battery brownout reset trigger: 2.4 V typ.
  - VBATPOR, power-on reset release: 2.75 V typ.
  - VBATLOW, minimum VBAT for charging: 2.1 V typ.
  - IBATLIM, discharge current limit: 100 mA min (footnote 1, page 30: "Validated through simulation"). This is a limit on current, not a voltage. No setting was found for it in the pages read.
- `design/architecture.md`:
  - Line 62 is the section 3 heading "## 3. Power".
  - Line 78: "Cut-off: the power chip stops discharge at 3.1 V." The line then adds "CORRECTION 2026-11-11: no 3.1 V cut-off exists in the nPM1304 specification as read; its power-fail threshold is a setting from 2.5 to 3.4 V, default 2.7 V (page 109)". The 3.1 V text is still there.
- `design/firmware.md` line 1198 (row H17): "Architecture section 3 still says 'the power chip stops discharge at 3.1 V'." It gives VSYSPOF 2.7 V default (2.5 to 3.4 V) [NPM p109] and brownout 2.4 V [NPM p29]. The cell maker's undervoltage limit is open item S12.

RESULT: done, 5 of 11 answered in full (Q4, Q6, Q7, Q8, Q11), 6 in part (Q1, Q2, Q3, Q5, Q9, Q10), 0 not found outright, with the sources named above.
