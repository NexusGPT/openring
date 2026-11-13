# Maker documents for the W1 ring board parts

Run: 13 Nov 2026, from 00:36 CET (clock from `date`). Helper: w1b.
Saved PDFs: `design/datasheets/w1b_*.pdf`.
Values come from the saved PDF text (pypdf) or from page images of the saved PDF (Read tool). Each value names its page in that PDF.

## Summary

| Part | Ref | Saved maker document | Code confirmed by it |
|---|---|---|---|
| 1 GRM155R61E105KA12D | C71 | w1b_murata_grm155r61e105ka12.pdf | Yes (p.1) |
| 2 GRM155R61A225KE95D | C85 | none | Not found |
| 3 GRM155R61A105KE15D | C86, C87 | none | Not found |
| 4 GRM188R61C106KAALD | C88 | none | Not found |
| 5 GRM2195C1H104JA01D | C35, C36 | none | Not found. No 100 nF C0G in 0603 or 0402 in the sources read (see section 5) |
| 6 DFE201610E-2R2M=P2 | L71, L72 | none | Not found |
| 7 NCP15XH103F03RC | RT1 | w1b_murata_ncp15xh103f03rc.pdf | Yes (p.1) |
| 8 1269AS-H-2R2M=P2 | L10 | w1b_murata_1269as-h-2r2m.pdf | Yes (p.2) |
| 9 2.2 uF 6.3 V+ 0402 | C60 | none | Not found |
| 10 SPK0641HT4H-1 | U5, U6 | w1b_knowles_spk0641ht4h-1_chipdip.pdf, plus on-disk chipsmall copy | Yes (title and pin table) |
| 11 nRF54LM20A CSP61 | U1 | none | Not read (see section 11) |

Count: 4 of 11 parts (1, 7, 8, 10) have a saved maker document that shows the code or the part.

## 1. GRM155R61E105KA12D (C71)

- File: `design/datasheets/w1b_murata_grm155r61e105ka12.pdf` (Murata "Product Search Data Sheet", created 2021/01/15, 4 pages).
- Address: https://akizukidenshi.com/goodsaffix/GRM155R61E105KA12.pdf (Murata-printed sheet hosted by a distributor).
- p.1: code list GRM155R61E105KA12J, GRM155R61E105KA12W, GRM155R61E105KA12D. Confirms the code.
- p.2 (スペック):
  - Capacitance 1.0 uF ±10%.
  - Rated voltage 25 Vdc.
  - Temperature characteristic X5R (EIA), range -55 to 85 deg C, change ±15.0%.
  - Size code 1005M (0402). L 1.0 ±0.05 mm, W 0.5 ±0.05 mm, T 0.5 ±0.05 mm. Terminal g 0.3 mm min, e 0.15 to 0.35 mm.
- Land pattern: not in this sheet. Not found. Searched: the Murata product sheet (4 pages, no land drawing). The Murata catalog C02E (see section 5) has no land pattern for this size.
- Note: the sheet says "This datasheet may be out of date."

## 2. GRM155R61A225KE95D (C85): not found

- Searched: Octopart, findchips, datasheets.com, oemstron (lists a 30-page PDF for the D suffix, not downloaded), RS, Future, Arrow, ChipDip (search results only).
- Result: no Murata-printed sheet was downloaded. The one listing I saw (oemstron, D suffix) gives 10 V, so the sheet could not confirm the 10 V rating in any case.

## 3. GRM155R61A105KE15D (C86, C87): not found

- Searched: one web search for "GRM155R61A105KE15". No hits for this code.

## 4. GRM188R61C106KAALD (C88): not found

- Searched: web search. Results: lioncircuits, LCSC, Octopart, Avnet, aiema, microchipusa, Farnell. Aiema lists a 186-page and a 206-page catalog. Not downloaded.
- Result: no part-specific Murata sheet found.

## 5. GRM2195C1H104JA01D (C35, C36): not found. No 100 nF C0G in 0603 or 0402 in the sources read

Murata 0805 code:
- Searched: "GRM2195C1H104JA01", "GRM2195C1H104JA01D", "GRM2195C1C104JA01". No listing and no sheet for the 104 code. The nearest codes are GRM2195C1H103JA01D (10 nF, 50 V, C0G, 0805) and GRM2195C1H122JA01D (1200 pF). These are sibling values, not the 100 nF part.
- Murata catalog C02E-13 (151 pages): saved at `ipv4.pccomponents.com/datasheets/mur-GRM.pdf`. Its C0G list (temperature compensating type) shows 0402 rows (GRM1535C1H...). The largest 0402 C0G value listed is 100 pF: row `GRM1535C1H101JDD5`, 50 V, 100 pF, ±5% (catalog text, PDF page 24). No GRM18 or GRM21 C0G row for 100 nF appears in the catalog text.

Candidate search (brief item 5). Makers and what was read:
- Kyocera AVX C0G (NP0) table, TDS-SMDMLCC-0010 Rev 4, PDF page 3 of 4 (printed page 5). This is `design/datasheets/w1_kyocera_avx_c0g_dielectric.pdf`, read from the page image (copy at scratchpad). Columns: 0402, 0603, 0805, 1206 with WVDC. The 0.1 uF row has marks only under 1206 at 16 V, 25 V and 50 V. No mark under 0603 or 0805 in the 0.1 uF row. Result: no 0.1 uF C0G in 0603 and none in 0805 in this table.
- TDK C1608C0G1E104J080AC and C1608C0G1H104J: one web search. Result: no part-specific sheet found. The only nearby C0G 0603 values found were 10 nF (C1608C0G1H103J080AA, a Future Electronics listing, not a maker sheet).
- Murata GRM1885C1H104JA01 (0603 C0G, 100 nF): one web search. Result: no listing. Only 100 pF (GRM1885C1H101JA01D) and 1 nF (GRM1885C1H102JA01D) come up, as distributor listings.
- Samsung, Yageo, Kyocera AVX (other than the table above): not searched in this run.

Result: none found in 0603 or 0402 for 100 nF C0G, in the sources read. The 0805 100 nF C0G part is not confirmed.

Problem found, for the lead: `design/ecad/ring/pcb/footprint-notes.md` section d says the AVX table offers 0.1 uF C0G "only in 0805 at 16 V and in 1206 at 25 V and 50 V". The AVX table page shows the 0.1 uF row only in 1206 (16, 25, 50 V), with no 0805 mark. The footprint note's 0805 claim is not supported by this page. The 0805 16 V part is not confirmed. Under this table, C35 and C36 have no 100 nF C0G option in 0402 or 0603 or 0805.

## 6. DFE201610E-2R2M=P2 (L71, L72): not found

- Murata product page (https://www.murata.com/en-global/products/productdetail?partno=DFE201610E-2R2M%3DP2) redirects to pim.murata.com. WebFetch of the redirect target returned no content. curl of https://pim.murata.com/en-global/pim/details/?partNum=DFE201610E-2R2M%3DP2 returned 5,965 bytes of HTML and no PDF link.
- Web searches: Octopart, Farnell, Future, RS, SnapEDA, datasheets.com, LCSC. These show a 2.2 uH part with DCR 140 mohm (distributor value) and rated current 1.7 A, 1.9 A or 2.4 A depending on the listing. The current figures disagree. None is a maker document; not used for any value.
- Not confirmed by a maker document.

## 7. NCP15XH103F03RC (RT1)

- File: `design/datasheets/w1b_murata_ncp15xh103f03rc.pdf` (Murata "Product Search Data Sheet", last updated 08/29/2021, 3 pages, downloaded from Arrow).
- Address: https://static.chipdip.ru/lib/012/DOC013012218.pdf (Murata-printed sheet hosted by ChipDip).
- p.1: part number NCP15XH103F03RC. Confirms the code.
- p.2 (Specifications):
  - Resistance (25 deg C) 10 kohm, tolerance ±1%.
  - B-constant (25/50 deg C) 3380 K, tolerance ±1%.
  - B-constant (25/80) 3428 K and (25/100) 3455 K, reference values.
  - Size code 1.0 x 0.5 mm, 0.4 x 0.2 inch (0402).
  - Maximum operating current (25 deg C) 0.1 mA. Dissipation constant 1 mW/deg C. Operating range -40 to 125 deg C. Max voltage 5 V.
- Land pattern: not in this sheet. Not found.
- Murata full spec (`pim.murata.com/asset/pim4/ntcForTemperatureSensor/SPEC_NCP15_PDF_NTCFORTEMPERATURESENSOR`, 2.27 MB) downloaded but encrypted. The text could not be read with the venv (pypdf needs the `cryptography` package, not installed). Not used.

## 8. 1269AS-H-2R2M=P2 (L10)

- Series name: DFE252010C Type. Murata spec No. J(E)TE243A-0004A-01 (9 pages). It lists 1269AS-H-2R2M=P2 in its electrical table.
- File: `design/datasheets/w1b_murata_1269as-h-2r2m.pdf` (9 pages, Murata-printed).
- Address: https://cdn.eicom.ru/media/PDF/8139348.pdf (Murata spec hosted by a distributor; it prints MURATA MFG.CO., LTD. and the part numbers).
- p.2 (Electrical specifications, Read as image):
  - Part 1269AS-H-2R2M=P2. Nominal inductance 2.2 uH, tolerance ±20%.
  - DC resistance 156 mohm (max).
  - Rated current, based on inductance change (current at 30% drop from initial inductance): 1.9 A (max). This is the saturation figure.
  - Rated current, based on temperature rise (40 deg C at 6-layer test board): 1.5 A (max).
  - Test: 1 MHz, 0.5 V. DC resistance measured with HIOKI 3541.
- p.1 (Physical dimensions, Read as image): L 2.5 ±0.2 mm, W 2.0 ±0.2 mm, H 1.0 mm max. Mass 0.024 g.
- p.5 (Recommended PCB pattern, Read as image): overall length 2.8 mm, gap between pads 1.2 mm, pad vertical length 2.0 mm. Pad width is not printed. Unit mm.
- Confirmed: yes, the exact code is in the p.2 table.
- Sibling sheet also saved: `design/datasheets/w1b_murata_1269as-h-1r5m_series.pdf` (Murata product sheet for 1269AS-H-1R5M=P2, 3 pages). Used only to check the 1269AS series name. Its values are not used.

## 9. 2.2 uF X5R/X7R, 6.3 V or more, 0402 (C60): not found

- Candidate GRM155R61A225KE95D: 10 V, so it does not meet 6.3 V or more with margin. Not a fit for the rating in the brief, and no sheet found (see section 2).
- Candidate GRM155R60J225ME95D (6.3 V, ±20%, X5R, 0402): Octopart lists it. No Murata-printed sheet was read. Not confirmed.
- Candidate GRM155R60J225KE95: an Octopart listing shows 4 V and ±20%, which conflicts with the code. Not used.
- Searches: 2 web searches (Murata GRM155R60J225KE95, 2.2 uF 6.3 V 0402). No Murata sheet found.

## 10. SPK0641HT4H-1 (U5, U6)

Two Knowles-printed copies, both "Datasheet SPK0641HT4H-1 Rev A, © 2016 Knowles":
- Copy A (on disk, distributor host): `design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.pdf` (11 pages).
- Copy B (ChipDip): https://static.chipdip.ru/lib/185/DOC011185940.pdf, saved as `design/datasheets/w1b_knowles_spk0641ht4h-1_chipdip.pdf` (11 pages).
- Maker site: https://www.knowles.com/products/microphones/mems-microphones/spk0641ht4h-1 returned 212 bytes, no sheet (logged in the earlier run). https://www.knowles.com/docs/default-source/model-downloads/spk0641ht4h-1-rev-a.pdf returned HTTP 404. No maker-site PDF was downloaded.

Points (Copy A, same on Copy B):
- Pin table (PDF p.6): 1 DATA (PDM output, digital O); 2 CLOCK (digital I); 3 SELECT (L/R select, internally pulled low); 4 Vdd (power); 5 to 8 GROUND (power).
- Supply current, performance mode, Table 3 (PDF p.3): Vdd 1.8 V typ 630 uA, max 710 uA. Vdd 3.6 V typ 700 uA, max 800 uA. Copy B has the same values (lines 83 to 84 of its text).
- Supply current, low-power mode, Table 4 (PDF p.4): Vdd 1.8 V typ 230 uA, max 275 uA. Vdd 3.6 V typ 270 uA, max 330 uA.
- Capacitor sentence (PDF p.4, Figure 4 notes): "Capacitors near the microphone should not contain Class 2 dielectrics due to their piezoelectric effect." (15 words, quoted exactly).
- Land pattern: "Example Land Pattern" is on PDF p.6, as a drawing. Its numbers are not in the text layer, so no land dimensions are read here.

Agreement: Copy A and Copy B agree on the supply current values and on the capacitor sentence (Copy B text lines 83, 84, 110, 111 and 192). The pin table heading and the land pattern heading sit on PDF p.6 in both. Pin rows were not compared line by line.

## 11. nRF54LM20A, CSP61 (CAAA): partly not read

- Product spec: https://docs.nordicsemi.com/r/bundle/ps_nrf54lm20a/page/chapters/mec_spec.html-csp61_package (HTML page, 366,386 characters).
- WebFetch on that page (offsets 0 and 100000): returned the CSP61 heading and navigation only. No ball pitch, ball diameter, body size or A1 corner values were returned. Marked "not read through the fetch tool".
- Product spec keyfeatures page: https://docs.nordicsemi.com/r/bundle/ps_nrf54lm20a/page/keyfeatures_html5.html. WebFetch returned the USB regulator links (USBREG chapter). The VBUS-absent statement on D+ and D- and the current consumption table were not reached. Not read.
- Web search snippet (not read through fetch, not saved): 3.02 x 2.43 mm body, 0.325 mm pitch, CSP61 (CAAA), 40 GPIO. Shown only as a snippet. Not used as a confirmed value.
- Nordic's PDF of the product spec: not found by search. curl was not used on the docs site (it refuses, per the earlier log).
- Not confirmed: all values in this part.

## Not done

- Parts 2, 3, 4, 6, 9: no maker sheet found. See each section for the addresses and searches.
- Part 5: the Samsung, Yageo and Kyocera AVX (other than the table) candidates were not searched in this run.
- Part 11: values not read (section 11).
- Land patterns for parts 1, 7 and the 0603 and 0805 C0G parts: not found in saved sheets.

RESULT: done, 4 of 11 parts have a saved maker document that confirms the code (1, 7, 8, 10); no 100 nF Class 1 part exists in 0603 or 0402 in the sources read (AVX 0.1 uF C0G row has no 0603 mark; Murata C02E 0402 C0G tops at 100 pF); the footprint-notes 0805 16 V claim is not supported by the AVX table.
