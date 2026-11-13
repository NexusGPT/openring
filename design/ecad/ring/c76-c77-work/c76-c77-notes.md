# C76 and C77 (1.0 nF, 0201, net VSYS): what they are and maker candidates

Date: 2026-11-13 (`date`, CET, run began 20:12). Working folder: ROOT/design/ecad/ring/c76-c77-work. Fetch addresses and times: fetch-log.md. Quote check: quotes-verify.log (last line "quotes checked 70, not found 0"). Quote list: quotes-list.txt, checked by verify-quotes.sh. Design files were read, not changed.

Citations are `file:line` in ROOT/design (or ROOT/design/ecad/ring where the name is short), and the line holds the quoted words.

## 1. What C76 and C77 are, and where they come from

- Part rows: parts.csv:37 "C76,C,1.0nF,,OpenRing:Chip_0201,power,no"; parts.csv:38 "C77,C,1.0nF,,OpenRing:Chip_0201,power,no". No maker part number in either row.
- Netlist (netlist.csv, read today by `grep -n "C76\|C77"`, saved in netlist-c76-c77.txt): line 73 "GND,C76,2,~,passive", line 74 "GND,C77,2,~,passive", line 372 "VSYS,C76,1,~,passive", line 373 "VSYS,C77,1,~,passive". Both caps sit between VSYS and GND.
- Value source, per the design:
  - bom.csv:75 "value from the nPM1300 kit design (DK PCA10184); to confirm against the nPM1304 product specification (S18)". The line is the "U2 VSYS 1.0 nF (DK C42)" addition for "C76,C77".
  - bom.csv:75 "NEW-11: the ring electronics designer must answer: the part code for 1.0 nF 0201 (power chip VSYS, DK C42); none in any source".
  - npm1304-reference.md:25 "the 1.0 nF pair came from the older chip's kit and is not in this reference".
  - sch-notes.md:253 "C76, C77 kept: the note says they are not in Nordic's circuit, it does not ask to remove them."
  - bom-notes.md:125 "C76 and C77, 1.0 nF each, no part number, 0201, net VSYS: NOT confirmed. The datasheet has no 1 nF capacitor anywhere". The section starts at bom-notes.md:119 "## C73 to C79 against the nPM1304 datasheet (2026-11-13, deferred item 129)".
  - pmic-caps-facts.md:209 "Plus C76 and C77, 1.0 nF each, with no part number."
  - pmic-caps-facts.md:238 "Rating and value of C76 and C77 (1.0 nF, no part number): not stated in any document."
- Role on the net: the design gives no role beyond VSYS capacitance. The datasheet says "VBUS supplies VSYS. When VBUS is disconnected, VSYS is supplied by its decoupling capacitors until it is" (design/datasheets/npm1304_datasheet_v1_0.txt:1636). The design's own Nordic reference lists three 10 uF on VSYS (npm1304-reference.md:25), which the design already has as C74, C75, C88.
- Maximum voltage on VSYS:
  - Design: bom-notes.md:104 "VSYS never exceeds VBUSOVP 5.5 V (nPM1304 PDF p17)".
  - Datasheet: npm1304_datasheet_v1_0.txt:738 "Operating voltage up to 5.5 V" (section 6.1, SYSREG).
  - Datasheet absolute-maximum table: npm1304_datasheet_v1_0.txt:569 "VBAT, VSYS, PVDD, VDDIO", with the row's max "-0.3" at line 573 and "5.5" at line 574.
  - Datasheet: npm1304_datasheet_v1_0.txt:1646 "VSYS must not be supplied from an external source."
  - So the highest VSYS voltage is 5.5 V, and 2 times that is 11 V.
- Design line to compare: the design's own 1 nF C0G part for the microphones is parts.csv:55 "C35,C,1nF C0G,04025A102JAT2A,OpenRing:Chip_0402,mics,no" (0402, not 0201). It is listed for context only.

Conflict noted (not a value conflict): pmic-caps-facts.md:81 gives "netlist line 367" for C76 and "netlist line 368" for C77. netlist.csv has them at lines 372 and 373 (section 1 above). The design file's line reference is out of date.

## 2. 0201 capacitor families already in the design

Murata is the maker for most 0201 capacitors. Samsung is used for the 100 nF parts.

| Ref | Part (design) | Maker | Dielectric and voltage as the design writes them | Source line |
|---|---|---|---|---|
| C1, C2, C5 | CL03A104KP3NNNC, 100 nF | Samsung | "X7R, +/-10 %, 10 V" | bom.csv:26; parts.csv:5 |
| C6 | GRM035R60J475ME15J, 4.7 uF | Murata | "X5R, +/-20 %, 6.3 V" | bom.csv:28; parts.csv:8 |
| C7, C10, C14 | GRM033D80E225ME47D, 2.2 uF | Murata | "X6T, +/-20 %, 2.5 V" | bom.csv:29; parts.csv:10 |
| C31, C32 | GRM033R60J105MEA2D, 1 uF | Murata | "1 uF X5R 6.3 V" | bom.csv:38; parts.csv:54 |
| C73 | GRM033R60J105MEA2D, 1.0 uF | Murata | (parts.csv row, power net) | parts.csv:34 |
| C3 | GJM0335C1H1R2WB01D, 1.2 pF | Murata | "NP0, +/-0.05 pF, 50 V" | bom.csv:17; parts.csv:19 |

Parts.csv rows read in full: C13 and C89 are "DNP" (parts.csv:23, :26), no value.

## 3. Candidates (1000 pF, 0201 / 0603 metric, rated at least 11 V)

Rating test: 50 V is 9.1 times the 5.5 V VSYS maximum. Both candidates pass.

| # | Maker | Part number (as the maker writes it) | Capacitance and tolerance | Rated voltage | Dielectric | Size L x W x T (mm) | Packaging code | Saved maker text | Quotes checked |
|---|---|---|---|---|---|---|---|---|---|
| A | Murata (same maker as the design's 0201 family) | GRM0335C1H102JE01 (sheet title "GRM0335C1H102JE01_(0603M(0201), C0G(EIA), 1000pF, DC 50V)"; sheet id "GRM0335C1H102JE01-01A") | 1000pF, "+/-5%" | "DC 50V" | "C0G(EIA)", "0+/-30 ppm/℃" | "0.6+/-0.03" x "0.3+/-0.03" x "0.3+/-0.03" | "D" = "φ180mm Reel PAPER Tape W8P2", "15000 pcs./Reel". The part-number system example reads "J            E01              D" (txt line 39). The full string with "D" is not written out on any quoted line. | design/datasheets/c76_murata_GRM0335C1H102JE01.pdf and .txt; txt lines 28, 39, 49, 51, 60, 66 | every quote of this row found in quotes-verify.log |
| B | Murata (same maker) | GRM033R71H102KA12 (sheet title "GRM033R71H102KA12_(0603M(0201), X7R(EIA), 1000pF, DC 50V)"; sheet id "GRM033R71H102KA12-01A") | 1000pF, "+/-10%" | "DC 50V" | "X7R(EIA)", capacitance change "-15 to 15 %", "-55 to 125℃" | "0.6+/-0.03" x "0.3+/-0.03" x "0.3+/-0.03" | "D" = "φ180mm Reel PAPER Tape W8P2", "15000 pcs./Reel". Packaging code is the same letter scheme as A (txt line 66). | design/datasheets/c76_murata_GRM033R71H102KA12.pdf and .txt; txt lines 28, 51, 60, 66 | every quote of this row found in quotes-verify.log |

Notes on each row:

- A: the Murata 0201 C0G part. Its sheet is the 0603M (0201) size; the design's C0G 0201 part is a GJM0335 (bom.csv:17), a different series. The sheet's rated value line is at txt line 60; the title and table are at txt lines 28 and 35.
- B: the Murata X7R part. The sheet's "A12" suffix is the one saved; the "A01" suffix that was searched for is not on the maker's site as fetched (see section 4).
- Murata's own temperature lines: A "-55 to 125℃" (txt line 60); B "-55 to 125℃" (txt line 60). Both stated.
- Not checked: ESR and any AEC-Q or lot data; the saved sheets were read only for the fields quoted in the table.

## 4. Second large maker: not found

No second maker has a part number that a saved maker page or sheet states at 1000 pF, 0201, 50 V. Checked:

- Kyocera AVX: the surface-mount catalog text (c76_kyocera-avx_SurfaceMount-catalog.txt) has no 0201 or 1000 pF line. `grep -n -E "02013|0201|1000 ?pF|102J|102K|1 ?nF"` returns no hit (saved in grep-avx-catalog-0201-1000pf.txt; exit 1). The C0G (NP0) KGM datasheet text (c76_kyocera-avx_C0GNP0-KGM.txt) confirms the family codes: "03 = 0201" (line 18), "1H = 50V" (line 17), "0201 (KGM03)" (line 222). Its 1000 pF row (text lines 172 to 195) is a thickness-letter table whose column headers are missing in the text copy, so no 0201 1000 pF 50 V row can be read. No AVX part number is given here.
- Samsung: the CL03C102JB3NNN product page (c76_samsung_CL03C102JB3NNN.html) does not name CL03C102 (count 0, samsung-cl03c102-count.txt). Its re-check returned HTTP 500. The 100 pF sibling page is saved (c76_samsung_CL03C101JB3NNN.html) but is not a candidate.
- TDK: both catalog fetches returned HTML, not the PDF; no text copy was made (grep-tdk-html.txt, no hit).
- Yageo: search only; CC0201JRNPO9BN102 was not in the results, no page fetched.

## 5. Not found (what was searched, and where)

- Murata GRM033R71H102KA01 (the "A01" code): the maker's address returned "The page you requested could not be found" (saved c76_murata_GRM033R71H102KA01.html; the re-check returned HTTP 403). Not a candidate.
- Murata GJM0335C1H102JB01: "could not be found" (saved c76_murata_GJM0335C1H102JB01.html). Not a candidate.
- The design's own statement of C76 and C77 rating: not in any design file (pmic-caps-facts.md:238). The datasheet has no 1 nF value: grep -i "[0-9] ?nF" over npm1304_datasheet_v1_0.txt returns only 100 nF lines (13122 to 14638), saved in grep-datasheet-nf.txt.

## 6. Problems found and how each is decided

- P1, design line reference: pmic-caps-facts.md:81 says netlist line 367; netlist.csv has the C76 VSYS pin at line 372. Inside this job, not changed (the file is read-only here). Decided: reported, the lead to fix the reference.
- P2, the "A01" code: the design does not name it; it was only in the search. GRM033R71H102KA01 gives "could not be found" (saved). Decided: the saved "A12" sheet is the candidate; the lead decides which code is fitted.
- P3, the Murata 0201 C0G part is in a different series from the design's C0G 0201 part (GJM0335C1H1R2WB01D, bom.csv:17). Decided: stated as fact, no recommendation.

questions_for_owner: none for this search. The choice between candidates A and B (C0G or X7R) and the second-maker part number are the lead's decision.

RESULT: done, two Murata 1000 pF 0201 candidates (GRM0335C1H102JE01 C0G and GRM033R71H102KA12 X7R, both 50 V) are backed by saved maker sheets and the quote check ends "not found 0"; no second-maker part number was found.
