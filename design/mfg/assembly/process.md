# Process sheet: every soldered or pressed joint of the ring and its case

Project root ROOT = .. Design version: commit d446272b. Work folder: `design/mfg/assembly/process-work/` (WORK). Written 2026-11-13 from 13:21 (`WORK/logs/start-time.txt`).

How to read the sources. Every value carries its source in round brackets: a maker's document by its key (table S below) with its page and the quoted words, or a design file with its line and the quoted words. `WORK/resolve_cites.py` found the page or line of every quote by searching the file; `WORK/audit_cites.py` searches them again. Three Hirose pages are drawings with no text layer: they are cited as "image" with the rendered page kept in `WORK/img/`. A value marked [CHOICE] is a choice between two valid options; the other option is in the list "for the lead to confirm" at the end. A value marked [CALC] is arithmetic; the numbers come from `WORK/logs/calc.log` or `WORK/logs/stencil_calc.log`.

## S. Sources

Maker documents fetched for this sheet (curl, no account, no form; the time is the file time written by curl, `WORK/logs/fetch-times.log`; addresses in `WORK/logs/fetch3.log`, `fetch5.log`, `fetch6.log`, `fetch7.log`, `fetch9.log`, `fetch10.log`, `fetch13.log`):

| Key | Saved file (design/datasheets/) | Address | Fetched |
|---|---|---|---|
| K1 | proc_kester_np505hr_tds.pdf (Kester NP505-HR solder paste, technical data sheet, issue 20 October 2021) | https://www.kester.com/downloads?Command=Core_Download&EntryId=61924 | 2026-11-13 13:24:53 CET |
| K2 | proc_kester_np505hr_flyer.pdf (NP505-HR flyer) | https://www.kester.com/downloads?Command=Core_Download&EntryId=39053 | 2026-11-13 13:24:51 CET |
| K3 | proc_kester_np505hr_product_page.html, text in proc_kester_np505hr_product_page.txt | https://www.kester.com/products/product/np505-hr-solder-paste | 2026-11-13 13:24:38 CET |
| K4 | proc_kester_275_tds.pdf (Kester 275 flux-cored wire, issue 17 May 2021) | https://www.kester.com/downloads?Command=Core_Download&EntryId=61953 | 2026-11-13 13:27:03 CET |
| K5 | proc_kester_275_product_page.html, text in proc_kester_275_product_page.txt | https://www.kester.com/products/product/275-flux-cored-wire | 2026-11-13 13:26:51 CET |
| K6 | proc_kester_959t_tds.pdf (Kester 959T liquid flux, issue 17 February 2021) | https://www.kester.com/downloads?Command=Core_Download&EntryId=61863 | 2026-11-13 13:34:14 CET |
| K7 | proc_kester_lead_free_handsoldering.pdf (Kester, lead-free hand soldering) | https://www.kester.com/Portals/0/Documents/Knowledge%20Base/Lead-free-Handsoldering.Final_.4.19.06.pdf | 2026-11-13 13:30:38 CET |
| K8 | proc_kester_alloy_temperature_chart.pdf | https://www.kester.com/Portals/0/Documents/Knowledge%20Base/Alloy%20Temperature%20Chart.pdf?ver=2020-06-26-135752-693 | 2026-11-13 13:30:36 CET |
| K9 | proc_kester_reflow_profile_snagcu.pdf (Kester reflow profile, SnAgCu alloys) | https://www.kester.com/Portals/0/Documents/Knowledge%20Base/Reflow%20Profile%20for%20SnAgCu%20Alloys.pdf | 2026-11-13 13:30:57 CET |
| T1 | proc_ti_slua271c_qfn_son_attachment.pdf (TI SLUA271C, QFN and SON PCB attachment) | https://www.ti.com/lit/pdf/slua271 | 2026-11-13 13:27:48 CET |
| T2 | proc_ti_snva009ai_dsbga.pdf (TI SNVA009AI, DSBGA wafer level chip scale package) | https://www.ti.com/lit/pdf/snva009 | 2026-11-13 13:27:48 CET |

Pages that could not be fetched (no account was asked, the server refused the plain request): Chip Quik paste sheets (403, `WORK/logs/fetch1.log`), Nordic's nRF54LM20A product specification pages (403, `WORK/logs/fetch4.log`), an AIM SAC305 alloy sheet (404, `WORK/logs/fetch10.log`, `WORK/logs/fetch11.log`).

Maker documents already in design/datasheets:

| Key | File | Part |
|---|---|---|
| H1 | w1_hirose_fh35c-15s-0.3shw50_drawing.pdf | J1 screen connector (drawing, pages are images) |
| H2 | w1_hirose_fh35c-15s-0.3shw50_spec.pdf | J1 product specification |
| A1 | slim_alps-skta-aaae010-orwin.pdf | SW1 to SW5 |
| N1 | w1_knowles_spk0641ht4h-1_chipsmall.pdf | U5, U6 microphones |
| P1 | npm1304_datasheet_v1_0.txt | U2 power chip (text copy of the datasheet) |
| B1 | case_bq25895.pdf | case charger U2 |
| E1 | case_esp32s3_mini1.pdf | case radio module U1 |
| X1 | slim2_cs-csnp32gcr01-20260408.pdf | ring storage U3 |
| X2 | p3_sgm38046.pdf | ring screen supply U4 |
| X3 | codes_tpd4e05u06.pdf | ring U9, case U6 |
| X4 | w1_ti_sn74axc4t774.pdf | ring U10 |
| X5 | motor_tlv755p.pdf | ring U11 |
| X6 | w1b_murata_1269as-h-2r2m.pdf | ring L10, L71, L72 |
| X7 | w1_kyocera_avx_x7r_dielectric.pdf | ring C60, C85 |
| X8 | w1_kyocera_cx2016db_catalog_page10.pdf | ring X1 |
| X9 | case_tps63802.pdf | case U3 |
| X10 | w5_coilcraft_xfl4015.pdf | case L1, L2 |
| X11 | case_kb_aptf1616.pdf | case LED1 |
| HW | w15_harwin_product_P70-6000045R.txt | spring pins P1 to P4 (text of the maker's product page) |
| HP | p3_harwin_p70.txt and p3_harwin_p70_chipdip.pdf | spring pins (the two files the brief names) |
| JL | w5_jlcpcb_capabilities.html | board maker's capability page |

## P1. Solder, flux and cleaning

P1.1 Alloy. One alloy for the whole product: SAC305 (Sn96.5 Ag3.0 Cu0.5), as the design already names it (`design/ecad/band/band-interface.md:137`: "Board lands pre-tinned (SAC305 stencil 0.05 mm)") (`design/mfg/assembly/assembly.md:150`: "soldered flat on its land with SAC305 paste at this step"). Melting range 217 to 220 C (K8 p.1: "Sn96.5Ag3Cu0.5 217-220"). No part limit read for this sheet forbids it: the lowest peak limit found is 250 C (J1, Murata L10/L71/L72, the case radio module, P3 table), and SAC305 needs a peak of only 235 C (K1 p.3: "Peak Temp (235-250°C)"). The cell never goes through a reflow (P3).

P1.2 Solder paste: Kester NP505-HR, SAC305, Type 4, 88.5 % metal, no-clean.
- Product and order code: "NP505-HR Sn96.5Ag3.0Cu0.5 T4 88.5% 500g JAR", part 7040211410, for stencil printing (K3 :87: "NP505-HR Sn96.5Ag3.0Cu0.5 T4 88.5% 500g JAR") (K3 :88: "7040211410").
- Particle size: Type 4 is 20 to 38 micrometre in the maker's own list (K3 :103: "NP505-HR 11.5% Sn96.5Ag3Cu0.5 20-38µ 500g J"). Why Type 4: the maker recommends it "for standard and fine pitch" (K1 p.4: "Type 4 mesh size is recommended for standard and fine pitch") and states the paste prints and reflows parts smaller than ours (K1 p.1: "printing and reflowing 01005 components in air reflow"); TI asks Type 3 or finer for wafer-level chips (T2 p.10: "Use Type 3 paste (25 to 45 micron particle size range) or finer solder paste for printing."). Type 5 is also sold, with half the shelf life (K1 p.4: "6 months for Innolot T4 and SAC305 T5") [CHOICE].
- Flux class: ROL0 (K1 p.1: "classified as ROL0 per IPC J-STD-"). It prints down to an area ratio of 0.55 (K1 p.1: "Consistent print performance to 0.55AR (SAC305)").
- Storage: refrigerated (K1 p.4: "Under refrigeration (0 to 10 °C / 32 to 50 °F)").

P1.3 Solder wire: Kester 275, SAC305, no-clean core.
- Flux class of the core: ROL0 (K4 p.1: "Classified as ROL0 per J-STD-004"). The product page marks the core "Contains Halogen" (K5 :76: "Contains Halogen"); ROL0 is the lowest halide class of J-STD-004 (evidence against, kept: the lead decides whether this matters for the skin-side ring).
- Sizes used (order codes from the maker's list): 0.25 mm (K5 :286: "Sn96.5Ag03Cu.5 2.2%/275 .010 1 LB SPL") (K5 :287: "2470687623"); 0.4 mm (K5 :209: "Sn96.5Ag03Cu.5 2.2%/275 .015 1 LB SPL") (K5 :210: "2470687608"); 0.5 mm (K5 :165: "Sn96.5Ag03Cu.5 2.2%/275 .020 1 LB SPL") (K5 :166: "2470687603"). 2.2 % flux meets the maker's advice for lead-free wire (K7 p.2: "Lead-free solder wires should contain at least 2% flux by weight."). band-interface.md asks "SAC305 0.3 wire" for the ring cell tabs (`design/ecad/band/band-interface.md:117`: "solder SAC305 0.3 wire or a pre-tinned land"); 0.3 mm is not in the maker's list, so the sheet uses 0.25 mm [CHOICE].

P1.4 Liquid flux (only where no paste or cored wire brings flux: the hot-bar joint of step 14 (step 16 before 2026-11-13), and touch-up): Kester 959T, a no-clean liquid flux (K6 p.1: "Low-Solid, No-Clean Liquid Flux"), class ORL0 (K6 p.1: "Classified as ORL0 per J-STD-004B"), named by the wire maker as the compatible liquid flux (K4 p.3: "959T or 985M no clean flux may be used as a compatible liquid flux") and fit for secondary soldering (K6 p.1: "can be used for secondary soldering"). It burns: flash point (K6 p.2: "18 °C (25 °F)"); keep it away from the hot plate until it has dried. Never on the switches: Alps forbids flux on the switch face before soldering (A1 p.4: "Upper face shall be free from flax prior to soldering.") and asks to keep flux out of the switch (A1 p.4: "Safeguard the switch assembly against flux penetration from its top side.").

P1.5 Residues: LEFT, never washed.
- The paste residue is designed to stay (K1 p.4: "NP505-HR is a no-clean formula. The residues are designed to remain on the PCB post-reflow."); the wire residue needs no removal (K4 p.3: "The 275 flux residues are non-corrosive, non-conductive and do not require removal in most"), and alcohol would not remove it anyway (K4 p.3: "IPA will not clean the residues off the surface of the circuit board after the").
- The microphones forbid washing and brushing after reflow (N1 p.9: "Do not board wash or clean after the reflow process.") (N1 p.9: "Do not brush board with or without solvents after the reflow process."); the switches forbid solvent cleaning (A1 p.4: "do not try to clean the switch with a solvent or the like.").
- What follows for later steps:
  - Step 4 of the guide said, when this sheet was written, "Both faces of PCB1 are cleaned of flux residue" (`design/mfg/assembly/assembly.md:112` of that version: "Both faces of PCB1 are cleaned of flux residue"). That conflicts with the microphone maker. Step 4 becomes inspection only (change C8; done, `design/mfg/assembly/assembly.md:116`).
  - Spring-pin probing at step 5: the 12 test pads get no paste (P2), so no paste residue lies on them; the paste residue elsewhere is hard and probe-able (K2 p.2: "Consistent hard probable surface, shatter-type residue").
  - Liner cast at step 21: the resin is cast over joints that keep their residue. The paste maker states compatibility with "most conformal coating materials" (K2 p.1: "Compatible with most conformal coating materials"); no saved document says that the liner resin EP30Med bonds over this residue: unverified. The test strip of step 21 gets one soldered disc and one soldered tab with their residue (change C19).
  - The screen: J1's contacts meet the cable above the soldered tails; residue at the tails is left. Hirose's pages read here say nothing about residue: unverified.

## P2. Stencils

Rule. Area ratio = opening area / (opening perimeter x foil thickness); a laser-cut stencil needs 0.66 or more; a nickel-formed stencil prints down to 0.57 (T1 p.11: "where the area ratio is less than 0.66, the stencil must be nickel formed") (T1 p.11: "formed stencils print with area ratios down to 0.57") (T1 p.11: "Area of Aperture Walls"); aspect ratio (width / thickness) above 1.5 (T1 p.11: "Figure 4-2) to be greater than 1.5 (see IPC-7525)"). Laser-cut and electro-polished (T2 p.10: "Use laser cutting followed by electro-polishing for stencil fabrication"); stainless steel is one of the paste maker's stencil materials (K1 p.3: "Stainless Steel, Molybdenum, Nickel Plated or Brass"). Every opening of the delivered paste files was measured by `WORK/stencil_calc.py` (log `WORK/logs/stencil_calc.log`: ring-B 45 openings, ring-F 302, case_main-F 265, case_main-B 0; 0 openings with no land on the ring, 4 on the case board, which are the thermal pad windows below).

| Board, face | Smallest opening | Thickness | Area ratio [CALC] | Material |
|---|---|---|---|---|
| Ring, screen face (B, pass 1) | 0201 lands 0.27 x 0.30 mm (C1, C2, C5, C7, C14, FB1, R71, R72) | 0.10 mm. Hirose asks 0.10 for J1 (H1 p.1, drawing image, seen in WORK/img/hirose_p1-1.png) | 0201: 0.711; J1 openings after change C3: 0.811 and 0.849 | stainless, laser cut, electro-polished |
| Ring, parts face (F, pass 2) | U1 (main chip) round 0.200 mm, 61 openings | 0.075 mm [CHOICE] | U1 0.667; U2 0.750; U4 0.867; largest thickness keeping 0.66 is 0.0758 mm | stainless, laser cut, electro-polished |
| Band ribbon FLEX1 (7 sizes), switch face F | switch lands 0.55 x 0.55 mm | 0.08 mm, the switch maker's paste thickness (A1 p.4: "(4)The thickness of cream solder : 0.08mm") | 1.719 | stainless, laser cut |
| Band ribbon FLEX2 (7 sizes), pad face B | disc openings 0.58 mm round (change C2) | 0.08 mm (same foil as FLEX1) | 1.812 | stainless, laser cut |
| Case main board, top (F) | U6 0.565 x 0.200 mm (corner radius 0.04) | 0.10 mm | 0.764 | stainless, laser cut |
| Case main board, bottom (B) | no opening | no stencil | none | none |
| Case pin board (PCB2) | pin pads 1.70 mm with 1.10 mm holes (HP :68: "Ø1.70 Solder pad") | 0.10 mm (same as the case main board) | 1.500 [CALC: one ring opening per pin pad, outer 1.70 mm, inner 1.10 mm, area 1.3195 mm2 over outer plus inner perimeter 8.7965 mm x 0.10 mm, `design/mfg/assembly/guide-fix4-work/logs/pin-ring-area-ratio.log`]; the delivered `fab/case_pins/gerber/case_pins-F_Paste.gbr` holds the four rings, each centred on its pin pad (change C6 done; `design/mfg/assembly/guide-joints-work/logs/ring_openings.log`: "ring openings on pin pads: 4 of 4") | stainless, laser cut |

Why 0.10 on the case board and not TI's 0.125 (B1 p.64, drawing image, seen in WORK/img/bq_p64-64.png): at 0.125 the U6 openings fall under 0.66 [CALC: 0.591 for the rectangle, `WORK/logs/calc.log`].

Reduced openings (lands that get less paste than the land):
- J1 on the ring's screen face: today the file has 1:1 openings (0.30 x 0.65 and 0.30 x 0.80, `WORK/logs/stencil_calc.log`). Hirose's stencil pattern is 0.23 wide, 0.55 long in the row of 0.65 lands, 0.65 long in the row of 0.80 lands, and 0.30 x 0.70 at the two fitting tabs (H1 p.1, drawing image, seen in WORK/img/hirose_p1-1.png). Change C3.
- The 12 test pads on the screen face: no paste (the guide's own rule, (`design/mfg/assembly/assembly.md:96`: "are copper on this face and get no paste")); change C3 removes them from the file.
- Case charger U2 thermal pad: the file already holds four 1.1 x 1.1 mm windows (`WORK/logs/case_noland.log`), TI's own example (B1 p.64, drawing image, seen in WORK/img/bq_p64-64.png): 66.4 % of the 2.7 mm package pad [CALC], inside TI's 50 to 70 % (T1 p.11: "coverage is approximately 50% to 70% of the pad area"). The joint table's finding "pad 25 has no paste" (`design/mfg/assembly/joint-table-notes.md`) comes from check rule R4, which looks for an opening at the land's centre only; the windows sit off the centre, round the middle via. Nothing to change in the board.
- FLEX2 disc lands: four round openings instead of one (change C2), to keep paste off the centre via.

## P3. Reflow profile

The paste maker's profile (K1 p.3: "Peak Temp (235-250°C)") (K1 p.3: "Ramp Rate") (K1 p.3: "<2.5C/sec") (K1 p.3: "Pre-heat Zone") (K1 p.3: "40-80 secs") (K1 p.3: "Soak Zone") (K1 p.3: "60-120 secs typical") (K1 p.3: "Reflow Zone 45-") (K1 p.3: "90 secs typical"); Kester's general SnAgCu profile puts the time above 217 C at 60 to 75 s typical (K9 p.1: "60-75 sec. typical"), 90 s at most (K9 p.1: "(90 sec max)"). The graph of K1 page 3 is read from its image (`WORK/img/kester_tds_p3_graph-3.png`): pre-heat to 150 C, soak 150 C to the liquidus line.

The profile of this product (one profile for every oven pass and the hot plate; temperatures at the board surface, read by a thermocouple taped beside the most massive part):
1. Ramp from room temperature to 150 C at less than 2.5 C/s (K1).
2. Soak 150 C to 200 C in 90 to 110 s (inside J1's 90 to 120 s (H1 p.6, drawing image, seen in WORK/img/hirose_p6-6.png), inside K1's 60 to 120 s), then 200 C to 217 C.
3. Time above 217 C: 60 to 75 s (K9 typical; inside K1's 45 to 90 s; inside the microphones' 60 to 150 s (N1 p.9: "Time (tL) 60-150 seconds")).
4. Time above 230 C: at most 35 s.
5. Peak 240 C, accepted 235 to 245 C on the thermocouple (235 is K1's lowest peak).
6. Cool at 6 C/s or slower (N1 p.9: "Ramp-down rate (TP to TSMAX) 6°C/second max"); do not move the board while the solder is liquid.

Part limits against this profile (upper values 245 C and 35 s; margins [CALC] in `WORK/logs/calc.log`):

| Pass | Part | Limit and source | Profile | Margin |
|---|---|---|---|---|
| Ring pass 1 and 2 | J1 Hirose FH35C | peak 250 C (H2 p.2: "PEAK TMP. 250℃MAX."); at most 60 s at 230 C (H2 p.2: "REFLOW TMP. 230℃ MIN WITHIN 60 sec."); at most 2 reflows (H1 p.6, drawing image, seen in WORK/img/hirose_p6-6.png) | 245 C, 35 s, 2 passes (it sits on the screen face, which goes through both) | 5 C; 25 s; 0 passes: AT THE LIMIT. No third reflow of the ring board, ever: a screen-face part that falls is hand-soldered (the guide already says so). Rework of J1 with an iron: Hirose allows (H2 p.2: "TMP. 350±10℃ FOR 5±1 sec.") |
| Ring pass 1 and 2 | eight 0201 parts of the screen face (Samsung, Murata, Yageo) | no saved document with a reflow limit was found (`WORK/logs/scan_limits.log` lists the files searched) | 2 passes | unverified |
| Ring pass 2 | U1 nRF54LM20A | no saved document; Nordic's pages refused the request (`WORK/logs/fetch4.log`) | 1 pass | unverified: for the lead |
| Ring pass 2 | U2 nPM1304 | moisture class 1 for the CSP (P1 :608: "MSL CSP"); no peak temperature in the saved datasheet (`WORK/logs/npm1304-reflow-search.log`) | 1 pass | peak unverified: for the lead |
| Ring pass 2 | U3 storage CSNP32GCR01 | moisture class 3 (X1 p.25: "(-40℃ to +85℃), MSL3"); no peak found | 1 pass | peak unverified; keep it in its sealed bag until placement |
| Ring pass 2 | U4 SGM38046 | (X2 p.2: "Lead Temperature (Soldering, 10s) ............................+260℃") | 245 C | 15 C |
| Ring pass 2 | U5, U6 Knowles SPK0641HT4H-1 | peak (N1 p.9: "Peak Temperature (TP) 260°C"); (N1 p.9: "Maximum of 3 reflow cycles is recommended.") | 245 C, 1 pass | 15 C; 2 passes |
| Ring pass 2 | U9 TPD4E05U06DQAR | (X3 p.37: "TPD4E05U06DQAR Active Production USON (DQA) | 10 3000 | LARGE T&R Yes NIPDAU Level-1-260C-UNLIM") | 245 C | 15 C |
| Ring pass 2 | U10 SN74AXC4T774RSVR | (X4 p.28: "SN74AXC4T774RSVR Active Production UQFN (RSV) | 16 3000 | LARGE T&R Yes NIPDAU Level-1-260C-UNLIM") | 245 C | 15 C |
| Ring pass 2 | U11 TLV75530PDQNR | (X5 p.28: "TLV75530PDQNR Active Production X2SON (DQN) | 4 3000 | LARGE T&R Yes NIPDAU | NIPDAUAG Level-1-260C-UNLIM") | 245 C | 15 C |
| Ring pass 2 | L10, L71, L72 Murata 1269AS-H-2R2M | (X6 p.3: "Peak temp. 250(+5,-0)℃ ( 230℃min , 30±10 s )"); (X6 p.5: "Reflow times ： 2 times max") | 245 C, 35 s, 1 pass | 5 C; 5 s; 1 pass |
| Ring pass 2 | C60, C85 Kyocera AVX X7R | (X7 p.2: "Soak the sample in 260ºC±5ºC solder for 10±0.5 seconds") | 245 C | 15 C |
| Ring pass 2 | X1 Kyocera CX2016DB | (X8 p.1: "MSL1"), (X8 p.1: "Reflow compatible"); no peak | 1 pass | peak unverified |
| Ring pass 2 | X2 TXC 9HT11, ANT1 Johanson, every other passive | the saved documents give no reflow limit (`WORK/logs/scan_limits.log`) | 1 pass | unverified |
| FLEX1 (step 6) | SW1 to SW5 Alps SKTAAAE010 | (A1 p.4: "260℃ Max. 3sec."); 40 s above 230 C (A1 p.4: "40 s Max."); pre-heat (A1 p.4: "120 sec. MAX."); (A1 p.4: "2 times Max."); the design repeats it (`design/ecad/band/band-interface.md:106`: "peak 260 C 3 s max, at most 2 reflows") | 245 C, 35 s, 1 pass | 15 C; 5 s; 1 pass |
| FLEX2 (step 8) | gold discs on polyimide | the design gives the film as (`design/ecad/band/band-interface.md:137`: "the polyimide film is rated far above it"); no disc maker yet | 245 C on the hot plate | no limit stated |
| Never in a reflow | the ring cell BT1 with PRT1 and RT1 | (`design/wiring/lead-decisions.md:22`: "never above 45 C in assembly") | the cell is joined at step 9, after every reflow and hot plate; only the iron of P4 touches its tabs | not exposed |
| Case main board (change C5) | U1 ESP32-S3-MINI-1 | (E1 p.47: "Solder the module in a single reflow.") (E1 p.47: "Peak temperature: 235 – 250 °C"); moisture class 3 (E1 p.47: "(MSL) of 3") | 245 C, 1 pass | 5 C; 0 passes: AT THE LIMIT (no second reflow of the case main board) |
| Case main board | U2 BQ25895RTW | (B1 p.57: "Level-2-260C-1 YEAR") | 245 C | 15 C |
| Case main board | U3 TPS63802 | (X9 p.31: "Level-1-260C-UNLIM") | 245 C | 15 C |
| Case main board | U6 TPD4E05U06DQAR | as U9 of the ring (X3) | 245 C | 15 C |
| Case main board | L1, L2 Coilcraft XFL4015/4020 | (X10 p.1: "Max three 40 second reflows at") (X10 p.1: "+260°C, parts cooled to room temperature between cycles") | 245 C, 1 pass | 15 C |
| Case main board | LED1 Kingbright APTF1616 | (X11 p.4: "The maximum number of reflow soldering passes is 2 times."); peak not read | 1 pass | peak unverified |
| Case main board | J1 USB4105, U4 SD NAND, U5 TPS2553, passives | not read for this sheet | 1 pass | unverified |
| Case pin board (change C6) | P1 to P4 Harwin P70-6000045R | (HW :326: "Max Solder Temperature: 260°C for 10 seconds") | 245 C | 15 C |

Result of the table: no part read fails. Two parts sit exactly at their cycle limit (J1 at 2 of 2, the case module at 1 of 1); 8 rows of the table hold a part or a limit marked "unverified": no saved document gives it (`WORK/logs/p3-unverified-rows.log`).

## P4. Hand soldering

General: heat the land and the lead first, then feed the wire to the joint, never to the tip (K4 p.3: "Heat both the land area and component lead to be soldered with the iron prior to"); choose a tip that carries enough heat, a chisel where it fits (K7 p.4: "Chose a tip with enough heat delivering capacity."). The tip face is no wider than the land (sizes from the pad dumps in design/mfg/assembly/joint-table-work/pads/). Kester's usual lead-free tip range is 371 to 400 C (K4 p.3: "between 371 to 400 °C (700 to 750 °F) for lead-free"); where a part limit is lower, the part limit wins.

| Joint class | Iron tip | Time | Wire | Tip face | Source of heat and time |
|---|---|---|---|---|---|
| Motor leads on FLEX1 (step 7), lands 0.30 x 0.80 | 320 C | 2 s | Kester 275 0.25 mm | chisel, 0.8 mm or narrower | (`design/ecad/band/band-interface.md:125`: "solder by hand (iron 320 C, 2 s)") |
| Ring cell tabs on FLEX2 (step 9), lands 0.26 x 0.45 | 280 C at most | 2 s per joint | Kester 275 0.25 mm | chisel or conical, 0.45 mm or narrower | (`design/ecad/band/band-interface.md:117`: "iron tip 280 C maximum, contact 2 s per joint") |
| Case thermistor TH1 leads (case step 10), plated holes | 340 C, 50 W iron | at most 7 s, joint 5 mm or more from the bead | Kester 275 0.5 mm | chisel, 1.3 mm or narrower | (`design/wiring/lead-decisions.md:71`: "at most 7 seconds at 340 degrees C with a 50 W iron") |
| Case cell leads W5, W6 (case step 10), plated holes, pads 1.3 mm | 340 C, 50 W iron | at most 7 s | Kester 275 0.5 mm | chisel, 1.3 mm or narrower | [CHOICE] the cell maker gives no limit (`design/wiring/lead-decisions.md:70`: "no solder limit"); the sheet uses the thermistor's setting of the same step so the iron is not changed |
| Case 30 AWG wires W1 to W4 and W7 (case steps 7 and 8): PCB2 pads 0.9 x 1.1, PCB1 holes with 1.3 mm pads | 340 C, 50 W iron | at most 7 s | Kester 275 0.4 mm | chisel, 0.9 mm or narrower | [CHOICE] no maker gives a limit for these pads or wires; same setting as above |
| Spring pins P1 to P4 in PCB2 (case step 4) | no iron: reflow (P3 profile, change C6) | | paste K1 | | the pin maker allows 260 C for 10 s (HW); an iron in Kester's range would pass that, so the pins are reflowed [CHOICE] |

The two Harwin documents the brief names give the pad and hole only (HP :69: "Ø1.10 Hole"); they state no soldering limit. The limit above is on the maker's product page (HW).

## P5. Hot plate for the four gold discs (step 8) and the FLEX1 switches if no oven is used

Method: the paste is printed through the 0.08 mm FLEX2 stencil (change C2), the discs laid on with tweezers, the ribbon on the plate with a thermocouple taped on the ribbon beside a disc. The plate follows the P3 profile on the thermocouple: to 150 C at less than 2.5 C/s, 150 to 200 C in 90 to 110 s, 60 to 75 s above 217 C, peak 240 C (235 to 245 C), then the ribbon is slid off onto a metal block to cool. The discs are not pressed while the solder is liquid (the guide already says so).

Disc height before the liner [CALC, `WORK/logs/calc.log`]: openings 4 x 0.58 mm round = 1.0568 mm2; paste 1.0568 x 0.08 = 0.0845 mm3; land 1.6 mm round = 2.0106 mm2. Even if all paste were metal, the solder layer is at most 0.0845 / 2.0106 = 0.042 mm. The disc (0.070 mm) therefore stands 0.070 to 0.112 mm above the land copper. The metal share of the paste by volume is not in a saved document, so only this upper bound is given. Step 8 checks this height (feeler gauge or microscope focus) and no longer checks "flush with the liner": that check needs the liner and stays at step 21, whose check already says (`design/mfg/assembly/assembly.md:262`: "pads flush and clean") (change C11).

## P6. Tools

| Tool | Size that matters | Used at | Source |
|---|---|---|---|
| Stencils (P2) | 0.10 mm ring screen face; 0.075 mm ring parts face; 0.08 mm FLEX1 and FLEX2 (one foil per ribbon, 7 sizes each); 0.10 mm case main and pin boards | steps 2, 6, 8, case 1 and 4 | P2 |
| Print carrier | holds the 0.30 mm ring board flat; second carrier with a pocket under J1 for pass 2 | step 2 | (`design/mfg/assembly/assembly.md:96`: "with a pocket under J1") |
| Squeegee | 80 to 90 durometer steel or polyurethane blade | steps 2, 6, 8 | (K1 p.3: "80 to 90 durometer stainless steel or polyurethane") |
| Reflow oven with a thermocouple logger | holds the P3 profile; logger reads the board surface | steps 2, 6, case 1, case 4 | P3 |
| Hot plate with a thermocouple | reaches 245 C; flat | step 8 | P5 |
| Tweezers | fine, non-magnetic, for 0201 parts and the 1.6 mm discs; never on J1's lever | steps 2, 8 | Hirose (H1 p.5, drawing image, seen in WORK/img/hirose_p5-5.png): operate the lever by hand, no sharp tool |
| J1 lever and cable | NO TOOL: fingertip on the middle of the lever; the cable held by its stiffened end and pushed in flat to the end | step 16 | (H1 p.5, drawing image, seen in WORK/img/hirose_p5-5.png) |
| Soldering iron | 50 W, temperature controlled, tips of P4 | steps 7, 9, case 1 (f), 7, 8, 10 | P4 |
| Hot bar | see hotbar-joint.md | step 14 | not settled here |
| Magnifier | 10 times stereo microscope (the guide's own inspection power) | steps 2, 4, 6, 8, 14, 16 | (`design/mfg/assembly/assembly.md:103`: "under the 10 times magnifier") |
| Meter | multimeter with continuity beep and 0.01 V | steps 6, 7, 8, 9, 14, 16, case 1, 9, 10 | the guide's checks |
| Probe tips | needle tips of 0.2 mm or finer, to land on one 0.30 mm land of the 0.51 mm pitch rows without touching the next (gap 0.21 mm) | steps 6 to 9 at the ribbon ends | (`design/ecad/band/band-interface.md:137`: "no bridge between the 0.21 mm gaps (land pitch 0.51 minus land 0.30)") |
| Feeler gauge or microscope with focus scale | 0.02 mm step | steps 6, 8 | the guide's step 6 feeler; P5 |

## P7. Locating features (fiducials)

No board has a fiducial (joint table, `design/mfg/assembly/joint-table-notes.md`). The board maker's assembly rule: 5 mm tooling edges with 1 mm fiducials centred 3.85 mm from the panel edges (JL :102: "1 mm fiducials centered at 3.85 mm from the panel edges"). The ring board is 27.2 x 12.6 mm with parts on both faces and no free corner, so the fiducials go on the panel rails, not on the board:
- Ring board panel: rails of 5 mm; three 1 mm fiducials on the parts face (F) and three on the screen face (B), at 3.85 mm from the panel edges, not in a line [CHOICE: three].
- FLEX1 panel (each size): three on the switch face (F). FLEX2 panel (each size): three on the pad face (B).
- Case main board panel: three on the top face (F). Case pin board panel: three on F.
- A builder who prints by hand aligns the stencil by its openings on the lands under the 10 times magnifier; the fiducials serve a placing machine. The mask opening round each fiducial is not in a saved document: the board helpers take it from the fiducial footprint they use.

## P8. Design-file changes this sheet needs

| # | File | Change | Reason |
|---|---|---|---|
| C1 | design/ecad/band/flex1-us7.kicad_pcb to flex1-us13.kicad_pcb and design/ecad/band/fab/flex1-usN/ | paste openings 1:1 on the 12 switch lands (0.55 x 0.55), a F_Paste Gerber per size | the Alps paste of 0.08 mm needs a stencil (P2) |
| C2 | design/ecad/band/flex2-us7.kicad_pcb to flex2-us13.kicad_pcb and design/ecad/band/fab/flex2-usN/ | B paste openings on each disc land: four 0.58 mm round openings centred 0.49 mm from the land centre on the diagonals; a B_Paste Gerber per size | paste off the centre via (`design/ecad/band/band-interface.md:141`: "Each disc land has one via 0.30/0.10 at its centre"); the paste is a printing paste (K3); P5 height |
| C3 | design/ecad/ring/pcb/fab/gerber/ring-B_Paste.gbr (through the J1 footprint's paste layer) | J1 openings to Hirose's stencil pattern (0.23 x 0.55, 0.23 x 0.65, tabs 0.30 x 0.70); remove the 12 test pad openings | (H1 p.1, drawing image, seen in WORK/img/hirose_p1-1.png); step 2's own rule |
| C4 | ring, FLEX1, FLEX2, case main and pin board panels | P7 fiducials and rails | P7 |
| C5 | design/ecad/case/pcb/board-notes.md, case procedure | (done: it is case step 1) a new step "0. Build the case main board", before step 1: print the 0.10 mm stencil, place, reflow once with the P3 profile, inspect every joint at 10 times, then hand-solder the USB socket J1's shell slots with Kester 275 0.5 mm at 340 C; nothing is powered at this step | no step builds the board (table group 2) |
| C6 | design/ecad/case/pcb/case_pins.kicad_pcb and its paste file; case procedure step 3 (done: case step 4) | paste openings over the four pin pads (pin in paste); step 3 reflows PCB2 with the pins in the P3 profile on a carrier with holes for the pin tails | P4 pins row |
| C7 | assembly.md step 2 | stencils of P2, profile P3, Locate: stencil aligned on the lands (hand) or the fiducials of C4 (machine); no third reflow (J1 2 of 2) | P2, P3 |
| C8 | assembly.md step 4 | no washing and no brushing; inspection only; the residue stays | P1.5 |
| C9 | assembly.md step 6 | stencil of C1, oven or hot plate with the P3 profile; no liquid flux | P2, P3, P1.4 |
| C10 | assembly.md steps 7 and 9 | wire Kester 275 0.25 mm; tips of P4 | P4 |
| C11 | assembly.md step 8 | paste printed through the C2 stencil (no needle), hot plate profile P5; check the disc height 0.070 to 0.112 mm; drop "flush with the liner" (it is checked at step 21) | P5 |
| C12 | assembly.md steps 16 and 17 | a new check at the end of step 16, before step 17: the ring runs on its cell (VBAT live) and the jig gives USB through CP1 to CP4; run T-SCREEN and T-SIGN with the screen folded down; on a fault, lift the screen and re-seat J1 (still possible until step 17) | J1's 14 contacts are proven before step 17 closes J1 (table group 9) |
| C13 | the 14 flex drawings (design/ecad/band/fab/) | the land number and net of each land of the ribbon's board end | the checks of steps 6 to 9 probe these lands (review 3 G2) |
| C14 | assembly.md step 2 check | the accept rule for a reflowed joint (for example ANT1's end terminations), a standard the lead names | no saved document gives it |
| C15 | case procedure step 9 (step 8 when written) | wait for a steady reading on W1 (C15 on VRING charges) | review 3 G10 |
| C16 | case procedure step 10 (step 9 when written) | after the cell lead joints: red probe on pad W5, black on pad W6: the same +3.0 to 4.35 V as before cutting | no check after the joint today; values from (`design/wiring/lead-decisions.md:70`: "the reading must be positive, between 3.0 and 4.35 V") |
| C17 | assembly.md step 14 (step 16 when written), band-interface.md section 7 | the hot-bar joint: see hotbar-joint.md | not settled here |
| C18 | assembly.md step 16 (step 15 when written) | tool: none, fingertip on the lever (P6) | (H1 p.5, drawing image, seen in WORK/img/hirose_p5-5.png) |
| C19 | assembly.md step 21 and design/mfg/specs/band-liner.md | the test strip carries one soldered disc and one soldered tab with their flux residue | P1.5 |

Note for the lead (not a design file): check_joints.py rule R4 cannot see paste windows that sit off a land's centre (U2 pad 25 of the case board). I did not edit the script; the U2 row names the windows separately so that R4 still checks every other land.

## Fill of the joint table

`WORK/fill_joints.py` writes `design/mfg/assembly/joints.csv` from `WORK/joints-before.csv` (the table as found, same sha256 as the delivered table at the start, `WORK/logs/before-sha.txt`). Each filled field adds `P<n>` (this file's section) to the row's source cell. `joint-gaps.md` is rebuilt by the table helper's `make_gaps.py`.

Results (logs in WORK/logs/):
- check_joints.py before the fill: last line `RESULT FAIL 365` (`WORK/logs/check-before.log`). After the fill: last line `RESULT FAIL 160`, rules R1 0, R2 160, R3 0, R4 0, R5 0 (`WORK/logs/check-final.log`, `WORK/logs/check-final-rules.txt`). A first run after the fill, before the expectation file was written, gave the same `RESULT FAIL 160` (`WORK/logs/check-after1.log`).
- Rows: 99; passing 32 (the 4 complete before, the 14 J1 contacts, the 10 ends of the case wires, the 2 case cell leads, the 2 thermistor leads); with a gap 67 (`WORK/logs/list-gaps-final.log`: `GAPS 67 of 99 rows`).
- Each failing row waits for (`WORK/logs/reason-counts.log`): hotbar-joint.md 15; change C1 alone 7 and C1 with C13 12; change C2 alone 7 and C2 with C13 4; change C13 alone 10; change C6 5; change C4 with C14 4; change C4 alone 1; change C3 with C4 1; change C4 with C5 1. Total 67.
- joint-gaps.md rebuilt by `make_gaps.py`: `gap lines 67 complete 32 unplaced 0 []` (`WORK/logs/make_gaps.log`). Its group headings are the table helper's fixed texts and still describe the gaps as they were before this fill; the line of each joint carries its new gap.
- The 13 tests of the table helper, run from a copy with the same sha256 (`WORK/logs/tests-sha.log`) so that its kept files land in WORK: last line `TESTS PASS 13 of 13 as expected` (`WORK/logs/tests.log`).
- Fields filled or rewritten: 517 (`WORK/logs/fill.log`).

Case step numbers after the case procedure was rewritten on 2026-11-13 (`design/ecad/case/pcb/board-notes.md`): the new build step of C5 is step 1; the pin reflow of C6 is step 4 (written here as step 3); wire pin end 7 (was 6), wire main end 8 (was 7), the check of C15 is in step 9 (was 8), the cell leads and the check of C16 in step 10 (was 9).

## For the lead to confirm

- Paste Type 4 (maker's advice for fine pitch, 12-month life); the other option is Type 5 (finer, 6-month life).
- Ring parts face stencil 0.075 mm stainless (area ratio 0.667); the other option is 0.08 mm nickel-formed (0.625, allowed down to 0.57 by TI).
- Wire 0.25 mm for the ring cell tabs; band-interface.md names 0.3 mm, which the maker does not list; the other option is 0.4 mm.
- Spring pins reflowed (pin in paste, change C6); the other option is an iron, which the pin maker's 260 C, 10 s limit does not forbid for the pin itself but which needs a joint temperature nobody measures.
- Case cell leads and 30 AWG wires at 340 C, 50 W, at most 7 s (the thermistor's setting of the same step); the other option is Kester's usual 371 C with a shorter time, which no maker bounds.
- Three fiducials per paste face on the panel rails; the other option is two.
- Hot plate for the discs (P5); the other option is the reflow oven with the P3 profile.
- Residues left on every board (no-clean); the other option is washing, which the microphone maker forbids on the ring board.
- Flux 959T for the hot-bar joint and touch-up; the other option is 985M, which the wire maker names too (its sheet was not fetched).

questions_for_owner: none

RESULT: done, check_joints.py ended `RESULT FAIL 365` before the fill and `RESULT FAIL 160` after it, every remaining failure waiting for hotbar-joint.md or a design-file change of P8.
