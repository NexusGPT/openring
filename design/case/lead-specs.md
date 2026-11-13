# Case lead wires as the makers deliver them (w16)

Project commit: cc6519bd (master). Checked 2026-11-13.
Saved copies: `design/datasheets/`. Citation form: `file:line` in the saved text, `p.N` for the printed page.

Short answer: neither maker states the lead wire gauge, the insulation or the strip length. The thermistor sheet gives the wire size, the alloy and a solder limit. The cell sheet gives only the lead length (100 mm, as drawn) and that the leads are flying leads.

## Part 1. Cell DNK852338 (700 mAh LiPo with PCM), two flying leads

Source: `design/datasheets/case_cell_dnk852338.pdf` (1 page, read in full; drawing crop `w16_cell_leads_crop-1.png`, 600 dpi, same folder).

| Value | Exact quote | Document | Page |
|---|---|---|---|
| Lead type | "Battery Terminals WC/FL*" and "*WC=With Connector FL=Flying Leads" | case_cell_dnk852338.pdf | p.1, Mechanical Data (bottom-left) and footnote |
| Lead length as delivered | "CL 100" in the table "Item Parameter (mm)"; "CL" is written on the leads in the lower drawing | case_cell_dnk852338.pdf | p.1, Battery Dimension Pictures (centre). The maker does not write "lead length" in words; the meaning of CL is read from where the callout sits. |
| Leads per cell | two leads: one black, one red, drawn from the PCM end (centre-bottom drawing) | case_cell_dnk852338.pdf | p.1, drawing at CL (crop, 600 dpi, `w16_cell_leads_crop-1.png`: black lead left, red lead right) |
| Colour meaning | not stated in words; the text says only "Ensure that charging leads are connected correctly. Reverse charging can lead to cell damage, fire or explosion." | case_cell_dnk852338.pdf | p.1, Announcements (bottom-right) |
| Polarity marks | "+" and "-" are printed on the cell face and terminal area in the top drawing; the maker does not say which lead is + | case_cell_dnk852338.pdf | p.1, top drawing of Battery Dimension Pictures (page centre; page image, not a text quote) |
| Wire gauge or conductor diameter | not stated by the maker | case_cell_dnk852338.pdf | p.1, all text read |
| Insulation type and outer diameter | not stated by the maker | case_cell_dnk852338.pdf | p.1 |
| Stripped or tinned end length | not stated by the maker | case_cell_dnk852338.pdf | p.1 |
| Soldering limit (temperature, time) | not stated by the maker | case_cell_dnk852338.pdf | p.1 |

Enough for a builder to cut, strip and solder the leads without asking: **no, missing:** wire gauge and conductor diameter; insulation type and outer diameter; which colour is + (the maker does not say, only the drawing colours); stripped or tinned length; solder temperature and time; confirmation that CL 100 means the lead length. The cut lengths 13.0 and 15.2 mm (board-notes, Wiring table) are the case's own choice, not maker values.

## Part 2. Thermistor Semitec 103AT-2 (10 kohm NTC, leaded bead)

Source: maker's data sheet "AT Thermistor", `design/datasheets/w16_semitec_P12-13-AT-Thermistor.pdf`, text `w16_semitec_P12-13-AT-Thermistor.txt` (2 pages: p.12 = txt lines 1-118, p.13 = txt lines 119-234). Page image `w16_semitec_pg-1.png`; Fig. 2 crop at 400 dpi `w16_semitec_fig2_crop-1.png`. Source URL: https://www.semitec-global.com/uploads/2022/01/P12-13-AT-Thermistor.pdf (linked from https://www.semitec-global.com/products/thermistor_at/).

The sheet gives shape 2 (Fig. 2) as the 103AT-2 shape: "Shape 2: See Fig. 2" (line 28), "White: 103AT-2" (line 46), Fig. 2 is the drawing for the "Color code" column.

| Value | Exact quote | Document | Page |
|---|---|---|---|
| Product and shape | "103AT-2、3 10.0 ｋΩ 3435 Ｋ ± 1％" with "- 50 to 110" (same row) | w16_semitec_P12-13-AT-Thermistor.txt:105 | p.12, Specifications |
| Lead wire | "0.5 tin plated 42 alloy" (Fig. 2) | w16_semitec_P12-13-AT-Thermistor.txt:34 | p.12, Dimensions, Fig. 2 |
| Lead size symbol | "□0.5 tin plated 42 alloy": the symbol before 0.5 is a square glyph; the sheet does not define it | w16_semitec_P12-13-AT-Thermistor.txt:33-34; image `w16_semitec_fig2_crop-1.png` (top right of Fig. 2) | p.12 |
| Other wire callouts on the same sheet (not this shape) | Fig. 1 "0.3 TPE resin parallel wire" (line 14); Fig. 5 "Φ0.5 tin plated copper wire" (line 69); Fig. 4 "PVC AWG30" (line 73) | same file | p.12 |
| Insulation type and outer diameter | not stated for shape 2; Fig. 2 shows no insulating sleeve. The PVC AWG30 callout is for shape 4 only (line 73), TPE for shape 1 only (line 14). | same file | p.12 |
| Wire gauge (AWG) | not stated for shape 2 | same file | p.12 |
| Lead colour | not stated. The "Color code" callout in Fig. 2 points to the dark dot on the bead, not to a lead. | image `w16_semitec_fig2_crop-1.png` | p.12, Fig. 2 |
| Lead length as delivered | not stated for shape 2. Fig. 2 gives "17±1.5" (bead tip to lead end, line 42) and "4.0 max." (bead length, line 48). By eye from the 400 dpi crop, the lead beyond the bead is about 13.0 mm. This is an estimate read off the drawing, not a maker value. | same file | p.12, Fig. 2 |
| Lead pitch | "2.54 ± 0.25" | same file, line 38 | p.12, Fig. 2 |
| Bead size (for TH1 body) | "2.4 max." (bead height, line 45) and "4.0 max." (bead length, line 48) | same file | p.12, Fig. 2 (lower view) |
| Stripped or tinned end length | not stated by the maker | same file | p.12-13 |
| Soldering limit | "When soldering make sure to have a minimum distance of 5 mm (8.5 mm), use a soldering iron with 50 W and solder for maximum 7 (2) seconds at 340 ˚C (350 ˚C)." Lines 190-192. "The values in brackets are for AT-5." (line 195). Caution column header "AT-2, 3, 5" (line 171). So for 103AT-2: 5 mm minimum distance, 50 W iron, 7 s maximum at 340 °C. | same file | p.13, Caution |
| Solder distance origin | the sheet does not say from which point the 5 mm is measured | same file | p.13 |
| Cut shorter than the minimum | "If you plan to cut the lead wire shorter than the above minimum distance please contact us." (lines 193-194) | same file | p.13 |
| Soldering-heat test (reference only) | "AT-2, 3, 4 10 s at 260 ℃ or 3.5 s at 350 ℃" (line 121) | same file | p.13, Reliability |
| Handling limits | "Do not apply a mechanical load of more than 2 N" (line 177); "sensor head of 3 mm" as the minimum bend distance (line 174) | same file | p.13, Caution |

Enough for a builder to cut, strip and solder the leads without asking: **no, missing:** lead length as delivered (only an estimate from the drawing, about 13 mm); insulation (not stated for shape 2, which appears bare); meaning of the square glyph in "□0.5" (square or round section); wire gauge; lead colour; stripped or tinned length. The soldering limit is stated (5 mm minimum, 50 W, 7 s at 340 °C), with the solder-distance origin missing.

Distributor's statement, not a maker value: DigiKey gives "Length - Lead Wire 0.49" (12.50mm)" for 103AT-2 (page saved as `w16_digikey_103AT-2_webfetch_summary.txt`, not a raw page; the raw fetch returned HTTP 403).

Conflict found: the case BOM (`design/case/case-bom.csv` line 70) gives the bead as "bead 1.6 dia (start value; maker sheet not read)". The maker sheet gives 2.4 max height and 4.0 max length for the bead (p.12, Fig. 2). The 1.6 mm figure is not in the maker sheet.

## Documents opened, all addresses fetched

| Address | Result | Saved as |
|---|---|---|
| https://www.semitec-global.com/uploads/2022/01/P12-13-AT-Thermistor.pdf | HTTP 200, application/pdf, 102736 bytes | `w16_semitec_P12-13-AT-Thermistor.pdf`, `.txt`, `w16_semitec_pdfinfo.log` (2 pages), `w16_semitec_pg-1.png`, `w16_semitec_fig2_crop-1.png` |
| https://www.semitec-global.com/ | HTTP 200, 71453 bytes; no 103AT-2 data | `w16_semitec_home.html`, `w16_semitec_home_links.log` |
| https://www.semitec-global.com/products/ | HTTP 200, 83860 bytes; lists "AT Thermistor (high accuracy type)" | `w16_semitec_products.html`, `w16_semitec_products_grep.log` |
| https://www.semitec-global.com/products/thermistor_at/ | HTTP 200, 58915 bytes; same spec table and the same PDF link (html line 498); no lead data | `w16_semitec_thermistor_at.html`, `w16_semitec_thermistor_at.txt`, `w16_semitec_thermistor_at_grep.log` |
| https://www.digikey.com/en/products/detail/semitec-usa-corp/103AT-2/16579059 | curl HTTP 403 (raw page not saved); WebFetch summary gave lead length 12.50 mm (distributor's statement) | `w16_digikey_curl.log`, `w16_digikey_103AT-2_webfetch_summary.txt` |
| https://www.mouser.com/new/semitec/semitecatet/ | HTTP 200, 18680 bytes; no 103AT-2 row in the saved text (grep found no lines) | `w16_mouser_semitec_atet_page.html`, `.txt`, `w16_mouser_grep.log` (empty) |

Two web searches were run for the 103AT-2 data sheet; they gave distributor pages only and are not used as sources.

Cell: no web fetch. The cell sheet was read from the project file.

Not stated by the maker, list of documents opened: cell sheet (case_cell_dnk852338.pdf, p.1); Semitec AT sheet (pp.12-13); Semitec AT product page; the other Semitec pages listed above. Not found in any of them: lead gauge, lead insulation for shape 2, lead colour for shape 2, stripped length, cell solder limit.

## questions_for_owner

1. Cell lead gauge, insulation, outer diameter, lead colour for + and -, stripped or tinned length, and solder limit are not in the DNK sheet. The sheet lists a sales contact (<email removed>, p.1). I did not contact the maker; the owner decides whether to ask.
2. Thermistor: Semitec's sheet does not give lead length or insulation for shape 2. Does the owner want a sample measured, or a question to Semitec, before the 10 mm cut is fixed?
3. Thermistor: the 5 mm minimum solder distance is not said to be measured from a named point. Confirm the joint position relative to the bead so that the 10 mm cut keeps 5 mm.
4. Thermistor: the square glyph in "□0.5 tin plated 42 alloy" is not defined. Confirm with Semitec whether the lead is 0.5 mm square or round.
5. BOM row TH1 (line 70, bead 1.6 dia) does not match the maker's 2.4 max x 4.0 max bead. Owner to decide whether to update the BOM.

RESULT: done, both parts are answered from saved maker documents, but the cell lead gauge, insulation, colour and solder limit and the thermistor lead length and insulation are not stated by the makers.
